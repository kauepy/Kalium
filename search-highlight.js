// search-highlight.js
// Destaca o termo pesquisado na página.
// Remove os destaques automaticamente quando a pesquisa é apagada.

(function () {

    const HIGHLIGHT_CLASS = 'kalium-highlight';


    // =========================================================
    // ESCAPA CARACTERES ESPECIAIS PARA USAR O TERMO NO REGEX
    // =========================================================

    function escaparRegex(termo) {

        return termo.replace(
            /[.*+?^${}()|[\]\\]/g,
            '\\$&'
        );

    }


    // =========================================================
    // DESTACA AS OCORRÊNCIAS
    // =========================================================

    function destacarTermo(termo) {

        if (!termo || !termo.trim()) {
            return [];
        }

        const main =
            document.querySelector('main') ||
            document.body;

        if (!main) {
            return [];
        }

        // Remove destaques antigos antes de criar novos
        limparDestaques();

        const escaped =
            escaparRegex(termo.trim());

        const regex =
            new RegExp(`(${escaped})`, 'gi');

        const matches = [];

        const walker =
            document.createTreeWalker(
                main,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode(node) {

                        const parent =
                            node.parentElement;

                        if (!parent) {
                            return NodeFilter.FILTER_REJECT;
                        }

                        const tag =
                            parent.tagName;

                        // Não procurar dentro destes elementos
                        if (
                            tag === 'SCRIPT' ||
                            tag === 'STYLE' ||
                            tag === 'INPUT' ||
                            tag === 'TEXTAREA' ||
                            tag === 'NOSCRIPT' ||
                            tag === 'MARK'
                        ) {
                            return NodeFilter.FILTER_REJECT;
                        }

                        return NodeFilter.FILTER_ACCEPT;
                    }
                }
            );


        const textNodes = [];

        let node;

        while (
            (node = walker.nextNode())
        ) {

            textNodes.push(node);

        }


        textNodes.forEach((textNode) => {

            const text =
                textNode.nodeValue;

            regex.lastIndex = 0;

            if (!regex.test(text)) {
                regex.lastIndex = 0;
                return;
            }

            regex.lastIndex = 0;

            const fragment =
                document.createDocumentFragment();

            let lastIndex = 0;

            let match;


            while (
                (match = regex.exec(text)) !== null
            ) {

                // Texto antes do termo
                if (match.index > lastIndex) {

                    fragment.appendChild(
                        document.createTextNode(
                            text.slice(
                                lastIndex,
                                match.index
                            )
                        )
                    );

                }


                // Elemento de destaque
                const mark =
                    document.createElement('mark');

                mark.className =
                    HIGHLIGHT_CLASS;

                mark.textContent =
                    match[0];

                fragment.appendChild(mark);

                matches.push(mark);

                lastIndex =
                    regex.lastIndex;

            }


            // Texto depois do último termo
            if (lastIndex < text.length) {

                fragment.appendChild(
                    document.createTextNode(
                        text.slice(lastIndex)
                    )
                );

            }


            textNode.parentNode.replaceChild(
                fragment,
                textNode
            );

        });


        return matches;

    }


    // =========================================================
    // VAI PARA O PRIMEIRO RESULTADO
    // =========================================================

    function irParaPrimeira(matches) {

        if (
            !matches ||
            matches.length === 0
        ) {
            return;
        }

        const first =
            matches[0];

        first.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });


        // Pequena animação no primeiro resultado
        setTimeout(() => {

            first.classList.add(
                'kalium-pulse'
            );


            setTimeout(() => {

                first.classList.remove(
                    'kalium-pulse'
                );

            }, 2000);

        }, 400);

    }


    // =========================================================
    // REMOVE TODOS OS DESTAQUES
    // =========================================================

    function limparDestaques() {

        const destaques =
            document.querySelectorAll(
                `.${HIGHLIGHT_CLASS}`
            );


        destaques.forEach((elemento) => {

            const parent =
                elemento.parentNode;

            if (!parent) {
                return;
            }


            parent.replaceChild(
                document.createTextNode(
                    elemento.textContent
                ),
                elemento
            );


            // Junta novamente os nós de texto
            parent.normalize();

        });

    }


    // =========================================================
    // ENCONTRA O CAMPO DE BUSCA
    // =========================================================

    function ehCampoDeBusca(elemento) {

        if (!elemento) {
            return false;
        }

        if (
            elemento.tagName !== 'INPUT' &&
            elemento.tagName !== 'TEXTAREA'
        ) {
            return false;
        }


        const id =
            (elemento.id || '')
                .toLowerCase();


        const classe =
            (elemento.className || '')
                .toString()
                .toLowerCase();


        const placeholder =
            (elemento.getAttribute('placeholder') || '')
                .toLowerCase();


        return (
            id === 'searchinput' ||
            id.includes('search') ||
            id.includes('busca') ||
            classe.includes('search') ||
            classe.includes('busca') ||
            placeholder.includes('buscar') ||
            placeholder.includes('pesquisar')
        );

    }


    // =========================================================
    // MONITORA A PESQUISA
    // =========================================================

    function monitorarTermoBusca() {

        document.addEventListener(
            'input',
            (event) => {

                const input =
                    event.target;


                if (
                    !ehCampoDeBusca(input)
                ) {
                    return;
                }


                const termo =
                    input.value.trim();


                // Se o usuário apagou a pesquisa
                if (!termo) {

                    limparDestaques();

                    sessionStorage.removeItem(
                        'kalium_termo'
                    );


                    console.log(
                        '[Kalium] Pesquisa apagada. Destaques removidos.'
                    );

                    return;

                }


                // Se o usuário começou a alterar
                // o termo, remove o destaque antigo.
                limparDestaques();

            }
        );

    }


    // =========================================================
    // OBSERVA MUDANÇAS NO DOM
    // =========================================================

    function observarCampoBusca() {

        const observer =
            new MutationObserver(() => {

                // O listener principal está no document,
                // então não precisamos fazer nada aqui.
                // Esta função existe apenas para manter
                // compatibilidade caso a busca seja recriada.

            });


        observer.observe(
            document.body,
            {
                childList: true,
                subtree: true
            }
        );

    }


    // =========================================================
    // INICIALIZAÇÃO
    // =========================================================

    function init() {

        // Começa a observar o campo de pesquisa
        monitorarTermoBusca();

        observarCampoBusca();


        // Recupera o termo salvo
        const termo =
            sessionStorage.getItem(
                'kalium_termo'
            );


        if (!termo) {
            return;
        }


        const matches =
            destacarTermo(termo);


        if (matches.length > 0) {

            irParaPrimeira(matches);


            console.log(
                `[Kalium] ${matches.length} ocorrências de "${termo}" destacadas.`
            );

        } else {

            console.log(
                `[Kalium] Termo "${termo}" não encontrado nesta página.`
            );

        }

    }


    // =========================================================
    // DISPONIBILIZA AS FUNÇÕES PARA OUTROS JS
    // =========================================================

    window.KaliumHighlightUI = {

        destacar: destacarTermo,

        limpar: limparDestaques

    };


    // =========================================================
    // INICIA QUANDO O DOM ESTIVER PRONTO
    // =========================================================

    if (
        document.readyState === 'loading'
    ) {

        document.addEventListener(
            'DOMContentLoaded',
            init
        );

    } else {

        init();

    }

})();