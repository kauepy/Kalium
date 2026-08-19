// search-highlight.js
// Destaca todas as ocorrências do termo na página e rola até a primeira.
// Usa sessionStorage (some ao fechar a aba).

(function () {
    const HIGHLIGHT_CLASS = 'kalium-highlight';

    function injetarCSS() {
        if (document.getElementById('kalium-highlight-style')) return;
        const css = `
            .${HIGHLIGHT_CLASS} {
                background: linear-gradient(180deg, transparent 60%, #22c55e55 60%);
                color: inherit;
                padding: 0 2px;
                border-radius: 3px;
                transition: background 1.2s ease;
                scroll-margin-top: 80px;
            }
            .${HIGHLIGHT_CLASS}.kalium-pulse {
                animation: kalium-pulse-anim 2s ease;
            }
            @keyframes kalium-pulse-anim {
                0%   { background: linear-gradient(180deg, transparent 60%, #22c55e 60%); }
                50%  { background: linear-gradient(180deg, transparent 60%, #16a34a 60%); }
                100% { background: linear-gradient(180deg, transparent 60%, #22c55e55 60%); }
            }
        `;
        const style = document.createElement('style');
        style.id = 'kalium-highlight-style';
        style.textContent = css;
        document.head.appendChild(style);
    }

    function destacarTermo(termo) {
        if (!termo || !termo.trim()) return [];
        const main = document.querySelector('main') || document.body;
        if (!main) return [];

        const escaped = termo.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escaped})`, 'gi');

        const matches = [];
        const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
            acceptNode(node) {
                const parent = node.parentElement;
                if (!parent) return NodeFilter.FILTER_REJECT;
                const tag = parent.tagName;
                if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'INPUT' ||
                    tag === 'TEXTAREA' || tag === 'NOSCRIPT' || tag === 'MARK') {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            },
        });

        const textNodes = [];
        let node;
        while ((node = walker.nextNode())) textNodes.push(node);

        textNodes.forEach((textNode) => {
            const text = textNode.nodeValue;
            if (!regex.test(text)) {
                regex.lastIndex = 0;
                return;
            }
            regex.lastIndex = 0;

            const fragment = document.createDocumentFragment();
            let lastIndex = 0;
            let m;

            while ((m = regex.exec(text)) !== null) {
                if (m.index > lastIndex) {
                    fragment.appendChild(
                        document.createTextNode(text.slice(lastIndex, m.index))
                    );
                }
                const mark = document.createElement('mark');
                mark.className = HIGHLIGHT_CLASS;
                mark.textContent = m[0];
                fragment.appendChild(mark);
                matches.push(mark);
                lastIndex = regex.lastIndex;
            }

            if (lastIndex < text.length) {
                fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
            }

            textNode.parentNode.replaceChild(fragment, textNode);
        });

        return matches;
    }

    function irParaPrimeira(matches) {
        if (!matches || matches.length === 0) return;
        const first = matches[0];
        first.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => {
            first.classList.add('kalium-pulse');
            setTimeout(() => first.classList.remove('kalium-pulse'), 2000);
        }, 400);
    }

    function limparDestaques() {
        document.querySelectorAll(`.${HIGHLIGHT_CLASS}`).forEach((el) => {
            const parent = el.parentNode;
            if (parent) {
                parent.replaceChild(document.createTextNode(el.textContent), el);
                parent.normalize();
            }
        });
    }

    function init() {
        const termo = sessionStorage.getItem('kalium_termo');
        if (!termo) return;
        injetarCSS();
        const matches = destacarTermo(termo);
        if (matches.length > 0) {
            irParaPrimeira(matches);
            console.log(`[Kalium] ${matches.length} ocorrências de "${termo}" destacadas.`);
        } else {
            console.log(`[Kalium] Termo "${termo}" não encontrado nesta página.`);
        }
    }

    window.KaliumHighlightUI = {
        destacar: destacarTermo,
        limpar: limparDestaques,
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
