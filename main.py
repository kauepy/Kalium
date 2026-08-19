"""
Backend de busca/gestão do site Kalium.

Usa SQLite para persistência (store_sqlite.py).
Indexa automaticamente os HTMLs do diretório configurado na primeira
inicialização.

Funcionalidades:
- Busca de conteúdo (FTS5 do SQLite) por termo
- Filtro de categoria e paginação
- Listagem de categorias e páginas
- CRUD de itens (GET lista, GET por id, POST cria)
- Health check
- Telemetria de pesquisas
- Rate limiting por IP
- CORS restrito
- Tratamento de erros seguro
- Servidor de arquivos estáticos (HTML/CSS/JS)
"""

# ===================== Auto-verificação de dependências =====================
import sys
import subprocess
import importlib.util

REQUIRED_PACKAGES = ["fastapi", "uvicorn", "pydantic"]


def _ensure_packages():
    missing = [pkg for pkg in REQUIRED_PACKAGES if importlib.util.find_spec(pkg) is None]
    if not missing:
        return

    print("=" * 60)
    print(f"⚠️  Dependências faltando: {', '.join(missing)}")
    print("🔧 Tentando instalar automaticamente...")
    print("=" * 60)

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing],
            stdout=sys.stdout,
            stderr=subprocess.STDOUT,
        )
        print("✅ Dependências instaladas com sucesso!\n")
    except subprocess.CalledProcessError:
        print("\n" + "=" * 60)
        print("� Falha ao instalar dependências automaticamente.")
        print("=" * 60)
        print(f"\nTente: {sys.executable} -m pip install " + " ".join(missing))
        sys.exit(1)


_ensure_packages()

# ===================== Imports =====================
import logging
import os
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from store_sqlite import SQLiteStore
from indexar_html import indexar as reindexar_htmls

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("site-backend")

# ===================== Configuração =====================
DB_PATH = os.environ.get("KALIUM_DB", "site.db")
HTML_DIR = os.environ.get("KALIUM_HTML_DIR", "html")
AUTO_REINDEX = os.environ.get("KALIUM_AUTO_REINDEX", "1") == "1"

BASE_DIR = Path(__file__).parent

origens_padrao = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000"
allowed_origins = os.environ.get("ALLOWED_ORIGINS", origens_padrao).split(",")

# ===================== Store global =====================
store: SQLiteStore | None = None


# ===================== Lifespan =====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global store
    logger.info("🚀 Inicializando Kalium Backend...")

    store = SQLiteStore(DB_PATH)

    if AUTO_REINDEX and store.vazio():
        logger.info(f"📂 Banco vazio. Indexando HTMLs de '{HTML_DIR}'...")
        try:
            n = reindexar_htmls(HTML_DIR, DB_PATH, verbose=False)
            logger.info(f"✅ {n} itens indexados.")
        except Exception as e:
            logger.warning(f"⚠️ Falha na auto-indexação: {e}")
    else:
        logger.info(f"📚 Banco com {store.contar()} itens carregados.")

    logger.info(f"� CORS permitido: {allowed_origins}")
    logger.info("✅ Pronto para receber requisições.")

    yield

    logger.info("🛑 Encerrando backend...")
    if store:
        store.fechar()


# ===================== App =====================
app = FastAPI(
    title="Site Search API",
    version="2.1.0",
    description="Backend de busca do Kalium com persistência SQLite e FTS5",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ===================== Rate limiting =====================
JANELA_SEGUNDOS = 10
LIMITE_REQUISICOES_POR_JANELA = 60
historico_requisicoes = defaultdict(deque)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host if request.client else "desconhecido"
    agora = time.monotonic()
    fila = historico_requisicoes[ip]

    while fila and agora - fila[0] > JANELA_SEGUNDOS:
        fila.popleft()

    if len(fila) >= LIMITE_REQUISICOES_POR_JANELA:
        logger.warning(f"Rate limit atingido para {ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Muitas requisições. Aguarde um instante e tente de novo."}
        )

    fila.append(agora)
    return await call_next(request)


@app.exception_handler(Exception)
async def excecao_nao_tratada(request: Request, exc: Exception):
    logger.exception(f"Erro não tratado em {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor."})


# ===================== Schemas =====================
class BuscaRequest(BaseModel):
    termo: str = Field(..., min_length=1, max_length=200)
    categoria: str | None = Field(None, max_length=50)
    pagina: int = Field(1, ge=1, le=1000)
    limite: int = Field(20, ge=1, le=100)


class ItemBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    descricao: str | None = Field(None, max_length=2000)
    categoria: str | None = Field(None, max_length=50)
    url: str | None = Field(None, max_length=500)
    pagina: str | None = Field(None, max_length=200)
    secao: str | None = Field(None, max_length=200)


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    criado_em: str


class PesquisaRegistro(BaseModel):
    termo: str = Field(..., min_length=1, max_length=200)
    pagina: str
    pagina_destino: str | None = None
    ocorrencias: int = Field(0, ge=0)
    total_palavras_pagina: int = Field(0, ge=0)


# ===================== Endpoints da API =====================
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "itens_no_banco": store.contar() if store else 0,
    }


@app.get("/api/info")
async def info():
    return {
        "nome": "Site Search API",
        "versao": "2.1.0",
        "persistência": "SQLite + FTS5",
        "endpoints": [
            "/health",
            "/api/v1/buscar",
            "/api/v1/categorias",
            "/api/v1/paginas",
            "/api/v1/itens",
            "/api/v1/pesquisas",
            "/api/v1/admin/reindexar",
        ],
    }


# ---------- BUSCA ----------
@app.post("/api/v1/buscar")
async def buscar_conteudo(request: BuscaRequest):
    resultados, total = store.buscar(
        termo=request.termo,
        categoria=request.categoria,
        pagina=request.pagina,
        limite=request.limite,
    )
    return {
        "termo": request.termo,
        "categoria": request.categoria,
        "pagina": request.pagina,
        "limite": request.limite,
        "total": total,
        "resultados": resultados,
    }

# ---------- CATEGORIAS E PÁGINAS ----------
@app.get("/api/v1/categorias")
async def listar_categorias():
    return {"categorias": store.listar_categorias()}


@app.get("/api/v1/paginas")
async def listar_paginas():
    return {"paginas": store.listar_paginas()}


# ---------- ITENS ----------
@app.get("/api/v1/itens")
async def listar_itens(
    limite: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    categoria: str | None = Query(None, max_length=50),
):
    """Lista todos os itens com paginação. Usado pelo frontend."""
    sql_count = "SELECT COUNT(*) AS n FROM itens WHERE 1=1"
    sql_items = "SELECT * FROM itens WHERE 1=1"
    params_count = []
    params_items = []

    if categoria:
        sql_count += " AND categoria = ?"
        sql_items += " AND categoria = ?"
        params_count.append(categoria)
        params_items.append(categoria)

    total = store._conn.execute(sql_count, params_count).fetchone()["n"]
    sql_items += " ORDER BY pagina, id LIMIT ? OFFSET ?"
    params_items.extend([limite, offset])
    rows = store._conn.execute(sql_items, params_items).fetchall()

    return {
        "total": total,
        "limite": limite,
        "offset": offset,
        "itens": [dict(r) for r in rows],
    }


@app.post("/api/v1/itens")
async def criar_item(item: ItemCreate):
    novo = store.criar(item.model_dump(exclude_none=True))
    return novo


@app.get("/api/v1/itens/{item_id}")
async def obter_item(item_id: int):
    item = store.obter(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


# ---------- TELEMETRIA ----------
@app.post("/api/v1/pesquisas")
async def registrar_pesquisa(request: Request, dados: PesquisaRegistro):
    ip = request.client.host if request.client else "desconhecido"
    payload = dados.model_dump()
    payload["_ip"] = ip
    registro = store.registrar_pesquisa(payload)
    return {"ok": True, "registro": registro}


@app.get("/api/v1/pesquisas")
async def listar_pesquisas(limite: int = Query(100, ge=1, le=500)):
    return {"pesquisas": store.listar_pesquisas(limite)}


@app.get("/api/v1/pesquisas/estatisticas")
async def estatisticas_termo(termo: str = Query(..., min_length=1, max_length=200)):
    return store.estatisticas_termo(termo)


# ---------- ADMIN ----------
@app.post("/api/v1/admin/reindexar")
async def admin_reindexar(limpar: bool = Query(False)):
    """Força re-indexação dos HTMLs."""
    try:
        n = reindexar_htmls(HTML_DIR, DB_PATH, limpar=limpar)
        return {"ok": True, "itens_indexados": n}
    except Exception as e:
        logger.exception("Falha na re-indexação")
        raise HTTPException(status_code=500, detail=f"Falha ao re-indexar: {e}")


# ===================== ARQUIVOS ESTÁTICOS =====================
# (DEVE SER A ÚLTIMA SEÇÃO DO ARQUIVO!)
# Servimos CSS/JS/IMG em rotas dedicadas e HTMLs por rota explícita.

# Pastas estáticas (CSS, JS, IMG)
@app.get("/css/{caminho:path}")
async def servir_css(caminho: str):
    arquivo = BASE_DIR / "css" / caminho
    if arquivo.exists() and arquivo.is_file():
        return FileResponse(arquivo)
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")


@app.get("/js/{caminho:path}")
async def servir_js(caminho: str):
    arquivo = BASE_DIR / "js" / caminho
    if arquivo.exists() and arquivo.is_file():
        return FileResponse(arquivo)
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")


@app.get("/img/{caminho:path}")
async def servir_img(caminho: str):
    arquivo = BASE_DIR / "img" / caminho
    if arquivo.exists() and arquivo.is_file():
        return FileResponse(arquivo)
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")


# HTMLs - uma rota pra cada um (mais previsível que StaticFiles)
HTML_FILES = ["index.html", "conteudo.html", "ciclo.html", "sobre.html"]


@app.get("/", response_class=FileResponse)
async def raiz_html():
    return FileResponse(BASE_DIR / "html" / "index.html")


@app.get("/index.html", response_class=FileResponse)
async def index_html():
    return FileResponse(BASE_DIR / "html" / "index.html")


@app.get("/ciclo.html", response_class=FileResponse)
async def ciclo_html():
    return FileResponse(BASE_DIR / "html" / "ciclo.html")


@app.get("/conteudo.html", response_class=FileResponse)
async def conteudo_html():
    return FileResponse(BASE_DIR / "html" / "conteudo.html")


@app.get("/sobre.html", response_class=FileResponse)
async def sobre_html():
    return FileResponse(BASE_DIR / "html" / "sobre.html")


# ===================== Arranque direto =====================
if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🚀 Kalium Backend v2.1.0 (SQLite + FTS5)")
    print("=" * 60)
    print(f"📍 API:        http://localhost:8000")
    print(f"📚 Docs:       http://localhost:8000/docs")
    print(f"❤️  Health:    http://localhost:8000/health")
    print(f"🌐 Site:       http://localhost:8000/")
    print(f"🗄️  Banco:      {DB_PATH}")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
