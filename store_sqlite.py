"""
Store SQLite para o Kalium.

Substitui o InMemoryStore do main.py por persistência real em arquivo.
Inclui:
- Tabela de itens (catálogo de páginas/seções)
- Tabela de telemetria de pesquisas
- Índice FTS5 independente para busca rápida por termo
- Métodos de seed a partir do indexador HTML

Uso:
    from store_sqlite import SQLiteStore
    store = SQLiteStore("site.db")
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path


class SQLiteStore:
    """Store SQLite com schema fixo e métodos equivalentes ao InMemoryStore."""

    # Schema SEM content='itens' — a FTS é independente e populada manualmente
    # em criar(). Isso evita o erro "no such column: pagina" e simplifica a manutenção.
    SCHEMA_ITENS = """
    CREATE TABLE IF NOT EXISTS itens (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo       TEXT NOT NULL,
        descricao    TEXT,
        categoria    TEXT,
        url          TEXT,
        pagina       TEXT,
        secao        TEXT,
        criado_em    TEXT NOT NULL,
        UNIQUE(titulo, pagina, secao)
    );

    CREATE INDEX IF NOT EXISTS idx_itens_categoria ON itens(categoria);
    CREATE INDEX IF NOT EXISTS idx_itens_pagina ON itens(pagina);
    """

    # FTS5 independente (não usa content=). Tem suas próprias colunas.
    # Sincronização é feita manualmente em criar().
    SCHEMA_FTS = """
    CREATE VIRTUAL TABLE IF NOT EXISTS itens_fts USING fts5(
        titulo,
        descricao,
        secao,
        categoria,
        tokenize = 'porter unicode61'
    );
    """

    SCHEMA_PESQUISAS = """
    CREATE TABLE IF NOT EXISTS pesquisas (
        id                     INTEGER PRIMARY KEY AUTOINCREMENT,
        termo                  TEXT NOT NULL,
        pagina                 TEXT NOT NULL,
        pagina_destino         TEXT,
        ocorrencias            INTEGER DEFAULT 0,
        total_palavras_pagina  INTEGER DEFAULT 0,
        ip                     TEXT,
        timestamp              TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_pesquisas_termo ON pesquisas(termo);
    CREATE INDEX IF NOT EXISTS idx_pesquisas_timestamp ON pesquisas(timestamp);
    """

    def __init__(self, db_path: str = "site.db"):
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._conectar()
        self._criar_schema()

    # ===================== Conexão =====================
    def _conectar(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def _criar_schema(self):
        with self._conn:
            for stmt in self.SCHEMA_ITENS.split(";"):
                stmt = stmt.strip()
                if stmt:
                    self._conn.execute(stmt)
            for stmt in self.SCHEMA_FTS.split(";"):
                stmt = stmt.strip()
                if stmt:
                    self._conn.execute(stmt)
            for stmt in self.SCHEMA_PESQUISAS.split(";"):
                stmt = stmt.strip()
                if stmt:
                    self._conn.execute(stmt)

    def fechar(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    # ===================== Itens =====================
    def criar(self, dados: dict) -> dict:
        """Insere item na tabela principal e sincroniza com a FTS."""
        agora = time.strftime("%Y-%m-%dT%H:%M:%S")
        with self._conn:
            # Tenta inserir; se já existe (UNIQUE), busca o id existente
            cur = self._conn.execute(
                """INSERT OR IGNORE INTO itens
                    (titulo, descricao, categoria, url, pagina, secao, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    dados.get("titulo", ""),
                    dados.get("descricao"),
                    dados.get("categoria"),
                    dados.get("url"),
                    dados.get("pagina"),
                    dados.get("secao"),
                    agora,
                ),
            )

            if cur.lastrowid:
                row_id = cur.lastrowid
            else:
                # Já existia — busca pelo UNIQUE (titulo, pagina, secao)
                row = self._conn.execute(
                    """SELECT id FROM itens
                        WHERE titulo = ?
                        AND (pagina IS ? OR pagina = ?)
                        AND (secao  IS ? OR secao  = ?)""",
                    (
                        dados.get("titulo", ""),
                        dados.get("pagina"),
                        dados.get("pagina"),
                        dados.get("secao"),
                        dados.get("secao"),
                    ),
                ).fetchone()
                row_id = row["id"] if row else None

            # Sincroniza com a FTS (manualmente)
            if row_id:
                # Primeiro remove da FTS caso já exista (idempotente)
                self._conn.execute(
                    "DELETE FROM itens_fts WHERE rowid = ?", (row_id,)
                )
                self._conn.execute(
                    """INSERT INTO itens_fts(rowid, titulo, descricao, secao, categoria)
                        VALUES (?, ?, ?, ?, ?)""",
                    (
                        row_id,
                        dados.get("titulo", ""),
                        dados.get("descricao") or "",
                        dados.get("secao") or "",
                        dados.get("categoria") or "",
                    ),
                )

        return self.obter(row_id) if row_id else dados

    def obter(self, item_id: int) -> dict | None:
        if not item_id:
            return None
        row = self._conn.execute(
            "SELECT * FROM itens WHERE id = ?", (item_id,)
        ).fetchone()
        return dict(row) if row else None

    def listar_categorias(self) -> list[str]:
        rows = self._conn.execute(
            "SELECT DISTINCT categoria FROM itens WHERE categoria IS NOT NULL ORDER BY categoria"
        ).fetchall()
        return [r["categoria"] for r in rows]

    def listar_paginas(self) -> list[str]:
        rows = self._conn.execute(
            "SELECT DISTINCT pagina FROM itens WHERE pagina IS NOT NULL ORDER BY pagina"
        ).fetchall()
        return [r["pagina"] for r in rows]

    def contar(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS n FROM itens").fetchone()
        return row["n"]

    # ===================== Busca =====================
    def buscar(self, termo: str, categoria: str | None,
                pagina: int, limite: int) -> tuple[list[dict], int]:
        """
        Busca usando FTS5 com ranking por relevância (bm25).
        Fallback para LIKE simples se o termo der problema com FTS.
        """
        termo_limpo = termo.strip().replace('"', ' ')
        if not termo_limpo:
            return [], 0

        # Tenta FTS primeiro
        try:
            return self._buscar_fts(termo_limpo, categoria, pagina, limite)
        except sqlite3.OperationalError as e:
            # Se o termo tem caracteres que quebram a query FTS, usa LIKE
            print(f"[buscar] FTS falhou ({e}), usando LIKE")
            return self._buscar_like(termo, categoria, pagina, limite)

    def _buscar_fts(self, termo: str, categoria: str | None,
                    pagina: int, limite: int) -> tuple[list[dict], int]:
        """Busca via FTS5 com bm25."""
        sql = """
            SELECT i.*, bm25(itens_fts) AS rank
            FROM itens_fts
            JOIN itens i ON i.id = itens_fts.rowid
            WHERE itens_fts MATCH ?
        """
        params: list = [f'"{termo}"*']

        if categoria:
            sql += " AND i.categoria = ?"
            params.append(categoria)

        # Conta total
        count_sql = f"SELECT COUNT(*) AS n FROM ({sql})"
        total_row = self._conn.execute(count_sql, params).fetchone()
        total = total_row["n"]

        sql += " ORDER BY rank LIMIT ? OFFSET ?"
        params.extend([limite, (pagina - 1) * limite])

        rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows], total

    def _buscar_like(self, termo: str, categoria: str | None,
                    pagina: int, limite: int) -> tuple[list[dict], int]:
        """Fallback: busca simples com LIKE."""
        like = f"%{termo.lower()}%"
        sql = """
            SELECT * FROM itens
            WHERE (LOWER(titulo) LIKE ? OR LOWER(descricao) LIKE ?)
        """
        params: list = [like, like]

        if categoria:
            sql += " AND categoria = ?"
            params.append(categoria)

        count_sql = f"SELECT COUNT(*) AS n FROM ({sql})"
        total_row = self._conn.execute(count_sql, params).fetchone()
        total = total_row["n"]

        sql += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limite, (pagina - 1) * limite])

        rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows], total

    # ===================== Telemetria =====================
    def registrar_pesquisa(self, dados: dict) -> dict:
        agora = datetime.utcnow().isoformat() + "Z"
        ip = dados.get("_ip", "desconhecido")
        with self._conn:
            cur = self._conn.execute(
                """INSERT INTO pesquisas
                    (termo, pagina, pagina_destino, ocorrencias,
                    total_palavras_pagina, ip, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    dados.get("termo", ""),
                    dados.get("pagina", ""),
                    dados.get("pagina_destino"),
                    dados.get("ocorrencias", 0),
                    dados.get("total_palavras_pagina", 0),
                    ip,
                    agora,
                ),
            )
            registro_id = cur.lastrowid

        return {
            "id": registro_id,
            "termo": dados.get("termo"),
            "pagina": dados.get("pagina"),
            "pagina_destino": dados.get("pagina_destino"),
            "ocorrencias": dados.get("ocorrencias", 0),
            "total_palavras_pagina": dados.get("total_palavras_pagina", 0),
            "timestamp": agora,
        }

    def listar_pesquisas(self, limite: int = 100) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM pesquisas ORDER BY id DESC LIMIT ?", (limite,)
        ).fetchall()
        return [dict(r) for r in rows]

    def estatisticas_termo(self, termo: str) -> dict:
        termo_lower = termo.lower()
        rows = self._conn.execute(
            """SELECT pagina_destino, COUNT(*) AS n
                FROM pesquisas
                WHERE LOWER(termo) = ?
                GROUP BY pagina_destino""",
            (termo_lower,),
        ).fetchall()
        por_pagina = {r["pagina_destino"] or "desconhecida": r["n"] for r in rows}
        total = sum(por_pagina.values())
        return {"termo": termo, "total_pesquisas": total, "por_pagina": por_pagina}

    # ===================== Reset / Seed =====================
    def limpar(self):
        """Apaga todos os dados (útil pra re-indexação)."""
        with self._conn:
            self._conn.execute("DELETE FROM itens_fts")
            self._conn.execute("DELETE FROM itens")
            self._conn.execute("DELETE FROM pesquisas")

    def vazio(self) -> bool:
        return self.contar() == 0


if __name__ == "__main__":
    # Teste rápido
    store = SQLiteStore("site.db")
    print(f"Itens no banco: {store.contar()}")
    print(f"Páginas: {store.listar_paginas()}")
    print(f"Categorias: {store.listar_categorias()}")
    store.fechar()
