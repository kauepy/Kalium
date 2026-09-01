// search-engine.js
// Motor de busca do Kalium, agora integrado à API.
// Em vez de embutir os dados localmente, consulta o backend.
//
// Estratégia:
//  1. Tenta usar Lunr.js (carregado opcionalmente) para busca local rápida.
//  2. Se a API tiver o endpoint de busca (/buscar), usa o backend como
//     fonte principal e faz cache em memória das respostas.

class KaliumSearchEngine {
    constructor(documents = []) {
        this.documents = Array.isArray(documents) ? documents : [];
        this.idx = null;
        this.apiBase =
            (typeof window !== 'undefined' && window.KaliumData && window.KaliumData.apiBase) ||
            'http://localhost:8000/api/v1';

        this.responseCache = new Map(); // chave: "termo|cat|p|lim" -> resultados
        this.init();
    }

    init() {
        // Se o Lunr estiver disponível (carregado por <script>), usa local.
        if (typeof lunr !== 'undefined') {
            try {
                const docsRef = this.documents;
                this.idx = lunr(function () {
                    this.field('title', { boost: 10 });
                    this.field('section', { boost: 5 });
                    this.field('content');
                    this.ref('id');

                    if (Array.isArray(docsRef)) {
                        for (const doc of docsRef) this.add(doc);
                    }
                });
            } catch (err) {
                console.warn('[Kalium] Falha ao inicializar Lunr:', err);
                this.idx = null;
            }
        }
    }

    /**
     * Busca principal. Tenta a API primeiro; se falhar, faz busca local.
     */
    async search(query, options = {}) {
        const termo = (query || '').trim();
        if (!termo) return [];

        const { categoria = null, pagina = 1, limite = 50 } = options;

        // 1) Tenta API
        try {
            const resultados = await this.searchAPI(termo, categoria, pagina, limite);
            if (resultados !== null) return resultados;
        } catch (err) {
            console.warn('[Kalium] Busca via API falhou, usando local:', err);
        }

        // 2) Fallback local (Lunr ou substring simples)
        return this.searchLocal(termo, categoria);
    }

    /**
     * Versão síncrona para compatibilidade com o código antigo que
     * ainda chama search(query) sem await. Recomendado migrar para await.
     */
    searchSync(query) {
        const termo = (query || '').trim();
        if (!termo) return [];
        return this.searchLocal(termo);
    }

    async searchAPI(termo, categoria, pagina, limite) {
        const cacheKey = `${termo}|${categoria || ''}|${pagina}|${limite}`;
        if (this.responseCache.has(cacheKey)) {
            return this.responseCache.get(cacheKey);
        }

        const params = new URLSearchParams({
            termo,
            pagina: String(pagina),
            limite: String(limite),
        });
        if (categoria) params.set('categoria', categoria);

        const resp = await fetch(`${this.apiBase}/buscar?${params.toString()}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!resp.ok) return null;

        const data = await resp.json();
        const itens = data.resultados || [];

        // Normaliza para o formato que a UI consome
        const normalizado = itens.map((it) => ({
            id: String(it.id),
            page: it.categoria || 'index',
            title: it.titulo || '',
            section: it.categoria || 'Geral',
            content: it.descricao || '',
            url: it.url || null,
            score: 1,
        }));

        this.responseCache.set(cacheKey, normalizado);
        return normalizado;
    }

    searchLocal(query, categoria) {
        const lower = query.toLowerCase();
        const resultados = [];

        for (const doc of this.documents) {
            if (categoria && doc.page !== categoria) continue;

            let score = 0;
            const titulo = (doc.title || '').toLowerCase();
            const conteudo = (doc.content || '').toLowerCase();
            const secao = (doc.section || '').toLowerCase();

            if (titulo.includes(lower)) score += 10;
            if (secao.includes(lower)) score += 5;
            if (conteudo.includes(lower)) score += 1;

            if (score > 0) resultados.push({ ...doc, score });
        }

        return resultados.sort((a, b) => b.score - a.score);
    }

    searchByPage(query, page) {
        const lower = (query || '').toLowerCase();
        return this.documents.filter(
            (d) => d.page === page &&
                (`${d.title} ${d.section} ${d.content}`.toLowerCase().includes(lower))
        );
    }

    getPages() {
        return Array.from(new Set(this.documents.map((d) => d.page)));
    }

    getSuggestions(query) {
        if (!query || query.length < 2) return [];
        const lower = query.toLowerCase();
        const set = new Set();
        for (const doc of this.documents) {
            if ((doc.title || '').toLowerCase().includes(lower)) set.add(doc.title);
        }
        return Array.from(set).slice(0, 5);
    }
}

// Variável global (mantida por compatibilidade)
let kaliumSearch = null;

async function initializeSearch() {
    // Espera o conteúdo estar disponível (preenchido por search-data.js)
    const dados =
        (window.KaliumData && (await window.KaliumData.load())) ||
        (typeof window !== 'undefined' && window.KALIUM_CONTENT) ||
        [];

    kaliumSearch = new KaliumSearchEngine(dados);
    console.log(`✅ Busca inicializada com ${dados.length} itens`);
    return true;
}
