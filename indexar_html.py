"""
Indexador HTML do Kalium.

Lê todos os arquivos .html do diretório configurado e extrai:
- Título de cada página
- Cabeçalhos (<h1>, <h2>, <h3>) como seções
- Parágrafos (<p>) como conteúdo descritivo

Popula o SQLiteStore com esses dados. Pode ser executado manualmente
ou automaticamente na primeira inicialização do backend.

Uso:
    python indexar_html.py [--html-dir html] [--db site.db] [--limpar]
"""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from store_sqlite import SQLiteStore


class ExtratorHTML(HTMLParser):
    """
    Extrai título da página, cabeçalhos e parágrafos de um HTML.
    Mantém o contexto (em qual heading cada parágrafo está).
    """

    def __init__(self):
        super().__init__()
        self.titulo_pagina = ""
        self.secoes: list[dict] = []
        self._heading_atual: str | None = None
        self._buffer: list[str] = []
        self._dentro_heading = False
        self._dentro_titulo = False
        self._dentro_p = False
        self._tag_stack: list[str] = []

    # ----- Helpers -----
    def _texto_tags(self, tag: str, attrs: list, target_attr: str = None):
        pass

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self._tag_stack.append(tag)

        if tag == "title":
            self._dentro_titulo = True
            self._buffer = []
        elif tag in ("h1", "h2", "h3", "h4"):
            self._dentro_heading = True
            self._buffer = []
        elif tag == "p":
            self._dentro_p = True
            self._buffer = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title" and self._dentro_titulo:
            self.titulo_pagina = "".join(self._buffer).strip()
            self._dentro_titulo = False
            self._buffer = []
        elif tag in ("h1", "h2", "h3", "h4") and self._dentro_heading:
            heading = "".join(self._buffer).strip()
            if heading:
                self._heading_atual = heading
                # Abre uma seção nova
                self.secoes.append({
                    "titulo": heading,
                    "conteudo": [],
                })
            self._dentro_heading = False
            self._buffer = []
        elif tag == "p" and self._dentro_p:
            paragrafo = "".join(self._buffer).strip()
            paragrafo = re.sub(r"\s+", " ", paragrafo)
            if paragrafo and self.secoes:
                self.secoes[-1]["conteudo"].append(paragrafo)
            elif paragrafo and not self.secoes:
                # Parágrafo antes de qualquer heading
                self.secoes.append({
                    "titulo": self.titulo_pagina or "Conteúdo",
                    "conteudo": [paragrafo],
                })
            self._dentro_p = False
            self._buffer = []

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data):
        if self._dentro_titulo or self._dentro_heading or self._dentro_p:
            self._buffer.append(data)


def extrair_pagina(caminho: Path) -> tuple[str, str, list[dict]]:
    """Retorna (nome_arquivo, titulo_pagina, lista_de_secoes)."""
    html = caminho.read_text(encoding="utf-8")
    ext = ExtratorHTML()
    ext.feed(html)
    return caminho.name, ext.titulo_pagina, ext.secoes


# Mapeamento de arquivo → categoria (pra alimentar o filtro)
CATEGORIA_POR_ARQUIVO = {
    "index.html": "artigos",
    "conteudo.html": "artigos",
    "ciclo.html": "artigos",
    "sobre.html": "guias",
}


def indexar(html_dir: str, db_path: str, limpar: bool = False, verbose: bool = True):
    """Indexa todos os HTMLs do diretório no SQLiteStore."""
    base = Path(html_dir)
    if not base.exists():
        print(f"[ERRO] Diretório não encontrado: {html_dir}")
        sys.exit(1)

    arquivos = sorted(base.glob("*.html"))
    if not arquivos:
        print(f"[AVISO] Nenhum .html encontrado em {html_dir}")
        return 0

    store = SQLiteStore(db_path)

    if limpar:
        if verbose:
            print("[INFO] Limpando banco antes de re-indexar...")
        store.limpar()

    total = 0
    for arquivo in arquivos:
        if verbose:
            print(f"[INFO] Indexando {arquivo.name}...")
        nome, titulo, secoes = extrair_pagina(arquivo)

        # Cria um registro principal (a página inteira)
        categoria = CATEGORIA_POR_ARQUIVO.get(nome, "artigos")
        url = f"/{nome}"

        # Insere a página como item (resumo)
        if titulo or secoes:
            descricao_resumo = ""
            if secoes and secoes[0]["conteudo"]:
                descricao_resumo = " ".join(secoes[0]["conteudo"])[:500]
            store.criar({
                "titulo": titulo or nome,
                "descricao": descricao_resumo,
                "categoria": categoria,
                "url": url,
                "pagina": nome,
                "secao": "Página",
            })
            total += 1

        # Insere cada seção como item separado
        for secao in secoes:
            conteudo = " ".join(secao["conteudo"]).strip()
            if not conteudo:
                continue
            store.criar({
                "titulo": secao["titulo"],
                "descricao": conteudo[:1000],
                "categoria": categoria,
                "url": f"{url}#{slugify(secao['titulo'])}",
                "pagina": nome,
                "secao": secao["titulo"],
            })
            total += 1

    store.fechar()
    if verbose:
        print(f"\n✅ Indexação concluída: {total} itens adicionados em {db_path}")
    return total


def slugify(texto: str) -> str:
    """Converte um título em slug pra usar como âncora."""
    s = texto.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexa os HTMLs do Kalium no SQLite.")
    parser.add_argument("--html-dir", default="html", help="Diretório com os .html")
    parser.add_argument("--db", default="site.db", help="Caminho do banco SQLite")
    parser.add_argument("--limpar", action="store_true", help="Apaga o banco antes de indexar")
    args = parser.parse_args()

    indexar(args.html_dir, args.db, limpar=args.limpar)
