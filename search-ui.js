// search-ui.js
class KaliumSearchUI {
    constructor() {
        this.modalOpen = false;
        this.currentQuery = '';
        this.searchTimeout = null;
        this.init();
    }

    init() {
        this.createModal();
        this.attachEventListeners();
        console.log('[Kalium] UI inicializada');
    }

    createModal() {
        // Evita criar duplicado se o script for carregado 2x
        if (document.getElementById('searchModal')) return;

        const html = `
            <div class="search-overlay" id="searchOverlay"></div>
            <div class="search-modal" id="searchModal">
                <div class="search-modal-header">
                    <span class="search-modal-title">🔬 Buscar</span>
                    <button class="search-modal-close" id="searchCloseBtn">×</button>
                </div>
                <input type="text" id="searchInput" class="search-modal-input"
                    placeholder="Pesquisar no Kalium..." autocomplete="off">
                <div class="search-result-count" id="resultCount"></div>
                <div class="search-results-container" id="searchResults">
                    <div class="search-empty-state">
                        <div class="search-empty-state-icon">🔍</div>
                        <div class="search-empty-state-title">Digite para começar</div>
                        <div class="search-empty-state-text">Pesquise por qualquer termo do conteúdo</div>
                    </div>
                </div>
                <div class="search-modal-footer">
                    Pressione <kbd>ESC</kbd> para fechar
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    }

    attachEventListeners() {
        // Captura TODOS os botões .icon-btn (incluindo o da lupa)
        const searchBtns = document.querySelectorAll('.icon-btn');
        console.log(`[Kalium] Botões de busca encontrados: ${searchBtns.length}`);

        searchBtns.forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('[Kalium] Botão de busca clicado');
                this.toggle();
            });
        });

        const closeBtn = document.getElementById('searchCloseBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        const overlay = document.getElementById('searchOverlay');
        if (overlay) {
            overlay.addEventListener('click', () => this.close());
        }

        const input = document.getElementById('searchInput');
        if (input) {
            input.addEventListener('input', (e) => {
                this.currentQuery = e.target.value;
                this.scheduleSearch();
            });
        }

        // Atalho Ctrl+K / Cmd+K e ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalOpen) {
                this.close();
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.toggle();
            }
        });

        // Click em resultado
        document.addEventListener('click', (e) => {
            const resultItem = e.target.closest('.search-result-item');
            if (!resultItem) return;
            const page = resultItem.dataset.page;
            const url = resultItem.dataset.url;
            const termo = this.currentQuery.trim();
            this.navegarComTermo(page, url, termo);
            this.close();
        });
    }

    navegarComTermo(page, url, termo) {

        const paths = {
            index: '/html/index.html',
            conteudo: '/html/conteudo.html',
            ciclo: '/html/ciclo.html',
            sobre: '/html/sobre.html'
        };

        let destino = null;

        // Normaliza o nome da página recebido pela API
        const pagina = String(page || '')
            .trim()
            .toLowerCase();

        // 1. Tenta encontrar pelo nome da página
        if (pagina === 'index') {
            destino = paths.index;
        }

        else if (pagina === 'conteudo') {
            destino = paths.conteudo;
        }

        else if (pagina === 'ciclo') {
            destino = paths.ciclo;
        }

        else if (pagina === 'sobre') {
            destino = paths.sobre;
        }

        // 2. Se não encontrou pela página, usa a URL
        if (!destino && url) {

            destino = url;

            // Remove / inicial para poder normalizar
            destino = destino.replace(/^\/+/, '');

            // Se já começa com html/, mantém
            if (!destino.startsWith('html/')) {
                destino = `html/${destino}`;
            }

            destino = `/${destino}`;
        }

        // 3. Fallback
        if (!destino) {
            destino = paths.index;
        }

        // 4. Adiciona o termo ANTES do #
        if (termo) {

            const hashIndex = destino.indexOf('#');

            let base = destino;
            let hash = '';

            if (hashIndex !== -1) {
                base = destino.substring(0, hashIndex);
                hash = destino.substring(hashIndex);
            }

            const sep =
                base.includes('?')
                    ? '&'
                    : '?';

            destino =
                `${base}${sep}buscar=${encodeURIComponent(termo)}${hash}`;

            sessionStorage.setItem(
                'kalium_termo',
                termo
            );
        }

        console.log(
            `[Kalium] Página recebida: "${page}"`
        );

        console.log(
            `[Kalium] URL recebida: "${url}"`
        );

        console.log(
            `[Kalium] Navegando para: ${destino}`
        );

        window.location.href = destino;
    }

    toggle() {
        this.modalOpen ? this.close() : this.open();
    }

    open() {
        this.modalOpen = true;
        document.getElementById('searchOverlay')?.classList.add('active');
        document.getElementById('searchModal')?.classList.add('active');
        document.getElementById('searchInput')?.focus();

        const termoAnterior = sessionStorage.getItem('kalium_termo');
        if (termoAnterior && !this.currentQuery) {
            this.currentQuery = termoAnterior;
            const input = document.getElementById('searchInput');
            if (input) input.value = termoAnterior;
            this.performSearch();
        }
    }

    close() {
        this.modalOpen = false;
        document.getElementById('searchOverlay')?.classList.remove('active');
        document.getElementById('searchModal')?.classList.remove('active');
    }

    scheduleSearch() {
        if (this.searchTimeout) clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => this.performSearch(), 200);
    }

    async performSearch() {
        const termo = this.currentQuery.trim();
        if (!termo) {
            this.renderEmptyState();
            return;
        }

        if (!kaliumSearch) {
            console.error('[Kalium] Motor de busca não inicializado');
            this.renderError('Motor não inicializado');
            return;
        }

        this.renderLoading();

        try {
            const resultados = await kaliumSearch.search(termo, { limite: 50 });
            this.renderResults(resultados || []);
        } catch (err) {
            console.error('[Kalium] Erro na busca:', err);
            this.renderError('Falha na busca');
        }
    }

    renderLoading() {
        const c = document.getElementById('searchResults');
        const n = document.getElementById('resultCount');
        if (n) n.textContent = 'Buscando...';
        if (c) c.innerHTML = `
            <div class="search-empty-state">
                <div class="search-empty-state-icon">⏳</div>
                <div class="search-empty-state-title">Carregando resultados</div>
            </div>`;
    }

    renderError(msg) {
        const c = document.getElementById('searchResults');
        const n = document.getElementById('resultCount');
        if (n) n.textContent = msg;
        if (c) c.innerHTML = `
            <div class="search-empty-state">
                <div class="search-empty-state-icon">⚠️</div>
                <div class="search-empty-state-title">Erro</div>
                <div class="search-empty-state-text">${msg}</div>
            </div>`;
    }

    renderResults(results) {
        const c = document.getElementById('searchResults');
        const n = document.getElementById('resultCount');

        if (!results || results.length === 0) {
            if (n) n.textContent = 'Nenhum resultado';
            if (c) c.innerHTML = `
                <div class="search-empty-state">
                    <div class="search-empty-state-icon">📭</div>
                    <div class="search-empty-state-title">Nenhum resultado</div>
                </div>`;
            return;
        }

        const plural = results.length !== 1 ? 's' : '';
        if (n) n.textContent = `${results.length} resultado${plural}`;
        if (!c) return;

        c.innerHTML = results.map((result) => {
            const preview = (result.content || '').substring(0, 80);
            return `
                <div class="search-result-item"
                    data-page="${this.escape(result.page || '')}"
                    data-url="${this.escape(result.url || '')}">
                    <div class="search-result-section">${this.escape(result.section || '')}</div>
                    <div class="search-result-title">${this.highlightQuery(result.title || '')}</div>
                    <div class="search-result-content">${this.highlightQuery(preview)}...</div>
                </div>`;
        }).join('');
    }

    renderEmptyState() {
        const c = document.getElementById('searchResults');
        const n = document.getElementById('resultCount');
        if (n) n.textContent = '';
        if (c) c.innerHTML = `
            <div class="search-empty-state">
                <div class="search-empty-state-icon">🔍</div>
                <div class="search-empty-state-title">Digite para começar</div>
            </div>`;
    }

    highlightQuery(text) {
        if (!this.currentQuery.trim() || !text) return text;
        const escaped = this.currentQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp(`(${escaped})`, 'gi'),
            '<strong style="color: #22c55e;">$1</strong>');
    }

    escape(text) {
        if (text === null || text === undefined) return '';
        return String(text)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    console.log('[Kalium] DOM pronto, inicializando busca...');
    const ok = await initializeSearch();
    console.log(`[Kalium] Motor de busca: ${ok ? 'OK' : 'FALHOU'}`);
    if (ok) {
        const ui = new KaliumSearchUI();
        window.kaliumUI = ui; // pra debug no console
    }
});