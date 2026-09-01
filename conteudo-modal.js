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
        },

        "plantas": {
        titulo: "Importância do Potássio nas Plantas",
        texto: `
            <p>O potássio é um macronutriente primário e o segundo nutriente mais requerido pelas plantas, ficando atrás apenas do nitrogênio.</p>
            <ul>
                <li>Ativação enzimática e síntese proteica;</li>
                <li>Regulação hídrica e abertura de estômatos;</li>
                <li>Resistência a estresses bióticos (pragas) e abióticos (secas e geadas).</li>
            </ul>
        `
    },
    "humano": {
        titulo: "Funções no Corpo Humano",
        texto: `
            <p>O potássio é essencial para o funcionamento das células, músculos e nervos. Ele participa do metabolismo energético, equilíbrio do pH sanguíneo, controle da pressão arterial e prevenção de problemas renais e ósseos.</p>
        `
    },
    "formas-solo": {
        titulo: "Formas de Potássio no Solo",
        texto: `
            <p>Existe um equilíbrio dinâmico entre quatro formas de reserva no solo:</p>
            <ul>
                <li><strong>Estrutural (Mineral):</strong> Preso em minerais primários. É a maior fração, mas de liberação muito lenta.</li>
                <li><strong>Fixado (Não trocável):</strong> Retido em argilas expansivas. Pouco acessível.</li>
                <li><strong>Trocável:</strong> Adsorvido em superfícies do solo. É a principal reserva de reposição rápida.</li>
                <li><strong>Solução do Solo (K⁺):</strong> Forma iônica dissolvida na água, prontamente absorvida pelas raízes.</li>
            </ul>
        `
    },
    "perdas-solo": {
        titulo: "Perdas de Potássio no Solo",
        texto: `
            <p>O solo perde potássio principalmente através de três vias principais:</p>
            <ul>
                <li><strong>Extração e Exportação:</strong> Retirada pelas colheitas (20 a 150 kg/ha).</li>
                <li><strong>Lixiviação:</strong> Carreado pela água em profundidade (20 a 70 kg/ha/ano).</li>
                <li><strong>Erosão:</strong> Perda da camada superficial do solo (0 a 80 kg/ha).</li>
            </ul>
        `
    },
    "manejo-fertilizantes": {
        titulo: "Manejo e Fertilizantes Potássicos",
        texto: `
            <p>A deficiência de potássio causa clorose, necrose e enfraquecimento dos tecidos vegetais. Já o excesso pode causar estresse osmótico e inibir a absorção de outros cátions.</p>
            <p><strong>Principais fertilizantes potássicos utilizados:</strong></p>
            <ul>
                <li><strong>Cloreto de Potássio (KCl):</strong> O mais utilizado mundialmente ("potássio branco").</li>
                <li><strong>Sulfato de Potássio (K₂SO₄):</strong> Indicado para culturas sensíveis ao cloro (ex: fumo e frutas).</li>
                <li><strong>Nitrato de Potássio (KNO₃):</strong> Fornece K e N juntos, muito utilizado em fertirrigação.</li>
            </ul>
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