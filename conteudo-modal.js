document.addEventListener('DOMContentLoaded', () => {

    const botoes = document.querySelectorAll('[data-conteudo]');

    const overlay = document.getElementById('conteudoOverlay');
    const fechar = document.getElementById('conteudoFechar');

    const titulo = document.getElementById('conteudoTitulo');
    const texto = document.getElementById('conteudoTexto');


    const conteudos = {

        importancia: {
            titulo: 'Importância do Potássio',

            texto: `
                <p>
                    O potássio é um nutriente essencial para o crescimento
                    e desenvolvimento das plantas.
                </p>

                <p>
                    Ele desempenha diversas funções importantes para
                    o funcionamento adequado dos vegetais.
                </p>

                <p>
                    Na agricultura, o potássio possui grande importância
                    para o desenvolvimento das culturas.
                </p>
            `
        },


        corpo: {
            titulo: 'Funções no Corpo Humano',

            texto: `
                <p>
                    O potássio é um mineral essencial para o funcionamento
                    adequado do corpo humano.
                </p>

                <p>
                    Ele participa de processos importantes relacionados
                    às células, músculos e sistema nervoso.
                </p>

                <p>
                    Também contribui para o equilíbrio de líquidos
                    no organismo.
                </p>
            `
        }

    };


    botoes.forEach(botao => {

        botao.addEventListener('click', () => {

            const tipo = botao.dataset.conteudo;

            const conteudo = conteudos[tipo];

            if (!conteudo) return;


            titulo.textContent = conteudo.titulo;

            texto.innerHTML = conteudo.texto;


            overlay.classList.add('active');

            document.body.style.overflow = 'hidden';

        });

    });


    function fecharModal() {

        overlay.classList.remove('active');

        document.body.style.overflow = '';

    }


    fechar.addEventListener('click', fecharModal);


    overlay.addEventListener('click', (evento) => {

        if (evento.target === overlay) {
            fecharModal();
        }

    });


    document.addEventListener('keydown', (evento) => {

        if (evento.key === 'Escape') {
            fecharModal();
        }

    });

});