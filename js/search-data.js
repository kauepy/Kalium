// search-data.js
// Carrega o conteúdo do backend (GET /api/v1/itens) e expõe pro motor de busca.

(function () {
    const API_BASE =
        (typeof window !== 'undefined' && window.KALIUM_API_BASE) ||
        'http://localhost:8000/api/v1';

    const FALLBACK_CONTENT = [];
    let cachedContent = null;

    function normalizarItem(it) {
        return {
            id: String(it.id),
            page: it.pagina || it.categoria || 'index',
            title: it.titulo || '',
            section: it.secao || it.categoria || 'Geral',
            content: it.descricao || '',
            url: it.url || null,
        };
    }

    async function loadContent() {
        try {
            const resp = await fetch(`${API_BASE}/itens?limite=200`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });
            if (resp.ok) {
                const data = await resp.json();
                const itens = data.itens || data.resultados || [];
                console.log(`[Kalium] ${itens.length} itens carregados da API`);
                return itens.map(normalizarItem);
            }
            console.warn(`[Kalium] API respondeu ${resp.status}`);
        } catch (err) {
            console.warn('[Kalium] Falha ao buscar itens:', err);
        }
        return FALLBACK_CONTENT;
    }

    function getContent() {
        return cachedContent || [];
    }

    async function awaitKaliumContent() {
        if (cachedContent !== null) return cachedContent;
        cachedContent = await loadContent();
        return cachedContent;
    }

    window.KALIUM_CONTENT = null;
    window.KaliumData = {
        load: awaitKaliumContent,
        get: getContent,
        apiBase: API_BASE,
    };

    awaitKaliumContent().then((data) => {
        window.KALIUM_CONTENT = data;
        document.dispatchEvent(new CustomEvent('kalium:content-ready', { detail: data }));
    });
})();
