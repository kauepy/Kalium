// search-ui.js
class KaliumSearchUI {
    constructor() {
        this.modalOpen = false;
        this.currentQuery = '';
        this.searchTimeout = null;
        this.mode = 'site'; // 'site' | 'ia'
        this.iaAbort = null;
        this.init();
    }

    init() {
        this.createModal();
        this.attachEventListeners();
        this.applyMode();
        console.log('[Kalium] UI inicializada');
    }

    createModal() {
        if (document.getElementById('searchModal')) return;

        const html = `
            <div class="search-overlay" id="searchOverlay"></div>
            <div class="search-modal" id="searchModal">
                <div class="search-modal-header">
                    <span class="search-modal-title" id="searchModalTitle">🔬 Buscar</span>
                    <button class="search-modal-close" id="searchCloseBtn" type="button">×</button>
                </div>
                <div class="search-mode-toggle" role="tablist">
                    <button type="button" class="search-mode-btn active" data-mode="site" id="modeSiteBtn">No site</button>
                    <button type="button" class="search-mode-btn" data-mode="ia" id="modeIaBtn">Perguntar à IA</button>
                </div>
                <div class="search-ask-row">
                    <input type="text" id="searchInput" class="search-modal-input"
                        placeholder="Pesquisar no Kalium..." autocomplete="off" maxlength="500">
                    <button type="button" class="search-ia-ask hidden" id="iaAskBtn">Perguntar</button>
                </div>
                <div class="search-result-count" id="resultCount"></div>
                <div class="search-results-container" id="searchResults">
                    <div class="search-empty-state">
                        <div class="search-empty-state-icon">🔍</div>
                        <div class="search-empty-state-title">Digite para começar</div>
                        <div class="search-empty-state-text">Pesquise por qualquer termo do conteúdo</div>
                    </div>
                </div>
                <div class="search-modal-footer" id="searchFooter">
                    Pressione <kbd>ESC</kbd> para fechar
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    }

    attachEventListeners() {
        document.querySelectorAll('[data-kalium="search"]').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.setMode('site');
                this.toggle();
            });
        });

        document.querySelectorAll('[data-kalium="ia"]').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.setMode('ia');
                this.open();
            });
        });

        // compatibilidade: lupa antiga sem data-kalium
        if (!document.querySelector('[data-kalium="search"]')) {
            document.querySelectorAll('.icon-btn').forEach((btn) => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.toggle();
                });
            });
        }

        document.getElementById('searchCloseBtn')?.addEventListener('click', () => this.close());
        document.getElementById('searchOverlay')?.addEventListener('click', () => this.close());
        document.getElementById('modeSiteBtn')?.addEventListener('click', () => this.setMode('site'));
        document.getElementById('modeIaBtn')?.addEventListener('click', () => this.setMode('ia'));
        document.getElementById('iaAskBtn')?.addEventListener('click', () => this.perguntarIA());

        const input = document.getElementById('searchInput');
        if (input) {
            input.addEventListener('input', (e) => {
                this.currentQuery = e.target.value;
                if (this.mode === 'site') this.scheduleSearch();
            });
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && this.mode === 'ia') {
                    e.preventDefault();
                    this.perguntarIA();
                }
            });
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalOpen) {
                this.close();
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.setMode('site');
                this.toggle();
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
                e.preventDefault();
                this.setMode('ia');
                this.open();
            }
        });

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

    setMode(mode) {
        if (mode !== 'site' && mode !== 'ia') return;
        this.mode = mode;
        this.applyMode();
        if (this.modalOpen && mode === 'site' && this.currentQuery.trim()) {
            this.performSearch();
        }
    }

    applyMode() {
        const isIa = this.mode === 'ia';
        const title = document.getElementById('searchModalTitle');
        const input = document.getElementById('searchInput');
        const askBtn = document.getElementById('iaAskBtn');
        const footer = document.getElementById('searchFooter');
        const siteBtn = document.getElementById('modeSiteBtn');
        const iaBtn = document.getElementById('modeIaBtn');

        if (title) title.textContent = isIa ? 'IA Kalium' : '🔬 Buscar';
        if (input) {
            input.placeholder = isIa
                ? 'Pergunte sobre potássio...'
                : 'Pesquisar no Kalium...';
        }
        if (askBtn) askBtn.classList.toggle('hidden', !isIa);
        if (footer) {
            footer.innerHTML = isIa
                ? 'Enter para perguntar · <kbd>ESC</kbd> para fechar · <kbd>Ctrl</kbd>+<kbd>I</kbd>'
                : 'Pressione <kbd>ESC</kbd> para fechar · <kbd>Ctrl</kbd>+<kbd>K</kbd>';
        }
        siteBtn?.classList.toggle('active', !isIa);
        iaBtn?.classList.toggle('active', isIa);

        if (isIa) {
            this.renderIaEmpty();
        } else if (!this.currentQuery.trim()) {
            this.renderEmptyState();
        }
    }

    navegarComTermo(page, url, termo) {

        const paths = {
            index: '/html/index.html',
            conteudo: '/html/conteudo.html',
            ciclo: '/html/ciclo.html',
            sobre: '/html/sobre.html'
        };

        let destino = null;

        const pagina = String(page || '')
            .trim()
            .toLowerCase();

        if (pagina === 'index') {
            destino = paths.index;
        } else if (pagina === 'conteudo') {
            destino = paths.conteudo;
        } else if (pagina === 'ciclo') {
            destino = paths.ciclo;
        } else if (pagina === 'sobre') {
            destino = paths.sobre;
        }

        if (!destino && url) {
            destino = url;
            destino = destino.replace(/^\/+/, '');
            if (!destino.startsWith('html/')) {
                destino = `html/${destino}`;
            }
            destino = `/${destino}`;
        }

        if (!destino) {
            destino = paths.index;
        }

        if (termo) {
            const hashIndex = destino.indexOf('#');
            let base = destino;
            let hash = '';

            if (hashIndex !== -1) {
                base = destino.substring(0, hashIndex);
                hash = destino.substring(hashIndex);
            }

            const sep = base.includes('?') ? '&' : '?';
            destino = `${base}${sep}buscar=${encodeURIComponent(termo)}${hash}`;
            sessionStorage.setItem('kalium_termo', termo);
        }

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
        if (this.mode === 'site' && termoAnterior && !this.currentQuery) {
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
        if (this.iaAbort) {
            this.iaAbort.abort();
            this.iaAbort = null;
        }
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

    async perguntarIA() {
        const pergunta = this.currentQuery.trim();
        if (!pergunta) {
            this.renderIaEmpty();
            return;
        }

        if (!kaliumSearch) {
            this.renderError('Motor não inicializado');
            return;
        }

        if (this.iaAbort) this.iaAbort.abort();
        this.iaAbort = new AbortController();

        const askBtn = document.getElementById('iaAskBtn');
        if (askBtn) askBtn.disabled = true;
        this.renderIaLoading();

        try {
            const dados = await kaliumSearch.perguntarIA(pergunta, this.iaAbort.signal);
            this.renderIaAnswer(dados);
        } catch (err) {
            if (err.name === 'AbortError') return;
            console.error('[Kalium] Erro na IA:', err);
            this.renderError(err.message || 'Falha ao perguntar à IA');
        } finally {
            if (askBtn) askBtn.disabled = false;
            this.iaAbort = null;
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

    renderIaLoading() {
        const c = document.getElementById('searchResults');
        const n = document.getElementById('resultCount');
        if (n) n.textContent = 'Consultando fontes...';
        if (c) c.innerHTML = `
            <div class="search-empty-state">
                <div class="search-empty-state-icon">⏳</div>
                <div class="search-empty-state-title">A IA está pensando</div>
                <div class="search-empty-state-text">Isso pode levar alguns segundos</div>
            </div>`;
    }

    renderError(msg) {
        const c = document.getElementById('searchResults');
        const n = document.getElementById('resultCount');
        if (n) n.textContent = 'Erro';
        if (c) c.innerHTML = `
            <div class="search-empty-state">
                <div class="search-empty-state-icon">⚠️</div>
                <div class="search-empty-state-title">Erro</div>
                <div class="search-empty-state-text">${this.escape(msg)}</div>
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

    renderIaAnswer(dados) {
        const c = document.getElementById('searchResults');
        const n = document.getElementById('resultCount');
        const fontes = dados.fontes || [];
        if (n) n.textContent = fontes.length ? `${fontes.length} fonte${fontes.length !== 1 ? 's' : ''}` : 'Resposta';
        if (!c) return;

        const fontesHtml = fontes.length
            ? `<div class="search-ia-sources">
                    <div class="search-ia-sources-title">Fontes</div>
                    ${fontes.map((f) => {
                        const titulo = this.escape(f.titulo || f.url || 'Fonte');
                        const url = this.escape(f.url || '');
                        const num = this.escape(String(f.numero ?? ''));
                        if (!url) {
                            return `<span class="search-ia-source"><span class="search-ia-source-index">${num}.</span>${titulo}</span>`;
                        }
                        return `<a class="search-ia-source" href="${url}" target="_blank" rel="noopener noreferrer"><span class="search-ia-source-index">${num}.</span>${titulo}</a>`;
                    }).join('')}
               </div>`
            : '';

        c.innerHTML = `
            <div class="search-ia-answer">
                <div class="search-ia-answer-text">${this.escape(dados.resposta || '')}</div>
                ${fontesHtml}
            </div>`;
    }

    renderEmptyState() {
        const c = document.getElementById('searchResults');
        const n = document.getElementById('resultCount');
        if (n) n.textContent = '';
        if (c) c.innerHTML = `
            <div class="search-empty-state">
                <div class="search-empty-state-icon">🔍</div>
                <div class="search-empty-state-title">Digite para começar</div>
                <div class="search-empty-state-text">Pesquise por qualquer termo do conteúdo</div>
            </div>`;
    }

    renderIaEmpty() {
        const c = document.getElementById('searchResults');
        const n = document.getElementById('resultCount');
        if (n) n.textContent = '';
        if (c) c.innerHTML = `
            <div class="search-empty-state">
                <div class="search-empty-state-icon">✨</div>
                <div class="search-empty-state-title">Pergunte à IA</div>
                <div class="search-empty-state-text">Sobre potássio e o ciclo do potássio</div>
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
        window.kaliumUI = ui;
    }
});
