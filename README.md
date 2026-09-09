Kalium

Site de divulgação científica sobre o potássio e seu ciclo biogeoquímico.

Sobre o projeto

O Kalium é uma aplicação web desenvolvida com o objetivo de apresentar informações científicas sobre o potássio (K) de forma acessível, organizada e interativa.

O projeto reúne conteúdos relacionados às características do potássio, sua importância e seu ciclo biogeoquímico, utilizando tecnologias de desenvolvimento web e recursos de Inteligência Artificial para ampliar as possibilidades de interação com o conteúdo.

A aplicação possui uma interface desenvolvida com HTML, CSS e JavaScript, um back-end desenvolvido em Python, armazenamento de dados utilizando SQLite e um sistema de Inteligência Artificial integrado à aplicação.

Funcionalidades

Entre as principais funcionalidades do Kalium estão a apresentação de conteúdos científicos sobre o potássio, a visualização de informações relacionadas ao seu ciclo biogeoquímico, o sistema de pesquisa interna, o destaque dos termos encontrados durante as pesquisas e a utilização de Inteligência Artificial para auxiliar na obtenção e apresentação de informações.

O sistema de Inteligência Artificial também possui mecanismos para gerenciamento de contexto, utilização de prompts, validação das entradas e respostas e pesquisa de informações externas quando necessário.

Estrutura do projeto

O projeto está dividido em diferentes diretórios e arquivos, cada um responsável por uma parte específica da aplicação.

A pasta IA contém os módulos responsáveis pelo funcionamento da Inteligência Artificial. O arquivo assistant.py coordena o funcionamento do assistente, enquanto config.py concentra configurações utilizadas pelo sistema. O arquivo context.py é responsável pelo gerenciamento do contexto utilizado nas interações. O arquivo model.py realiza a comunicação com o modelo de Inteligência Artificial. O arquivo prompts.py contém as instruções utilizadas para orientar o comportamento do modelo. O arquivo security.py realiza validações e aplica regras de segurança. O arquivo sources.py trabalha com as fontes utilizadas nas respostas e web_search.py é responsável pelas pesquisas realizadas na internet.

A pasta html contém as páginas da aplicação. O arquivo index.html corresponde à página inicial, conteudo.html apresenta os conteúdos científicos, ciclo.html apresenta informações sobre o ciclo biogeoquímico do potássio e sobre.html apresenta informações sobre o projeto.

A pasta css contém os arquivos responsáveis pela aparência e organização visual da aplicação. Os arquivos index.css, search-modal.css e search-modal_2.css definem os estilos utilizados pelas diferentes partes da interface.

A pasta js contém os arquivos JavaScript responsáveis pela interatividade da aplicação. O arquivo menu.js controla o menu de navegação, conteudo-modal.js controla os modais de conteúdo e os arquivos search-data.js, search-engine.js, search-highlight.js e search-ui.js formam o sistema de pesquisa da aplicação.

A pasta img contém as imagens utilizadas nas páginas do projeto.

O arquivo main.py contém a implementação principal do back-end da aplicação e é responsável pela comunicação entre a interface e os recursos disponibilizados pelo servidor.

O arquivo store_sqlite.py concentra as funções relacionadas à utilização do banco de dados SQLite.

O arquivo indexar_html.py auxilia no processo de indexação dos conteúdos presentes nas páginas HTML para utilização pelo sistema de pesquisa.

O arquivo requirements.txt contém as dependências necessárias para executar o projeto em Python.

O arquivo iniciar_backend.bat contém comandos para facilitar a inicialização do back-end no Windows.

O arquivo .gitignore define arquivos e diretórios que não devem ser enviados ao sistema de versionamento.

Tecnologias utilizadas

O front-end do projeto utiliza HTML5, CSS3 e JavaScript. O back-end é desenvolvido em Python e utiliza SQLite para armazenamento de dados.

A camada de Inteligência Artificial utiliza Python para realizar a comunicação com o modelo, gerenciar contexto, aplicar instruções, realizar validações e, quando necessário, obter informações externas por meio do sistema de pesquisa.

Execução

Para executar o projeto, primeiro deve-se clonar o repositório e acessar o diretório do Kalium.

git clone https://github.com/kauepy/Kalium.git
cd Kalium

Em seguida, recomenda-se criar um ambiente virtual Python:

python -m venv venv

No Windows, o ambiente virtual pode ser ativado utilizando:

venv\Scripts\activate

As dependências do projeto podem ser instaladas utilizando o arquivo requirements.txt:

pip install -r requirements.txt

As configurações sensíveis utilizadas pela aplicação devem ser armazenadas por meio de variáveis de ambiente e não devem ser publicadas no repositório.

Após a configuração das dependências, o back-end pode ser iniciado utilizando o arquivo iniciar_backend.bat ou por meio dos comandos correspondentes à configuração atual do servidor.

Objetivo

O objetivo do Kalium é utilizar recursos de desenvolvimento de software para criar uma ferramenta de divulgação científica capaz de apresentar informações sobre o potássio de maneira acessível e interativa.

O projeto também permite aplicar conhecimentos relacionados ao desenvolvimento web, programação em Python, bancos de dados, JavaScript, integração de APIs, Inteligência Artificial, processamento de informações e organização de sistemas de software.

Desenvolvimento

O projeto foi desenvolvido por Kauê Seemann da Cruz.

O código-fonte completo da aplicação está disponível publicamente no GitHub:

https://github.com/kauepy/Kalium

Status do projeto

O Kalium encontra-se em desenvolvimento. Novas funcionalidades, melhorias na Inteligência Artificial, aprimoramentos na interface e expansão do conteúdo científico poderão ser adicionados ao projeto durante seu desenvolvimento.