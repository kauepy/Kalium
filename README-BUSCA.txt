╔════════════════════════════════════════════════════════════╗
║     ARQUIVOS DE BUSCA - KALIUM                             ║
║  Modal de Pesquisa que Abre no Canto Direito              ║
╚════════════════════════════════════════════════════════════╝

📁 ARQUIVOS INCLUSOS:
────────────────────

JS (JavaScript):
  • search-data.js       → Base de dados com 42 itens de conteúdo
  • search-engine.js     → Motor de busca com Lunr.js
  • search-ui.js         → Interface do modal

CSS (Estilos):
  • search-modal.css     → Estilos do modal (drawer lado direito)

════════════════════════════════════════════════════════════

🚀 COMO INTEGRAR NO SEU PROJETO:

1. Crie as pastas:
   projeto/
   ├── js/      (copie os 3 .js aqui)
   └── css/     (copie o .css aqui)

2. Em CADA arquivo HTML, no <head> adicione:
   <link rel="stylesheet" href="css/search-modal.css">

3. Em CADA arquivo HTML, ANTES de </body> adicione:
   
   <!-- Lunr (precisa internet) -->
   <script src="https://cdn.jsdelivr.net/npm/lunr@2.3.9/lunr.min.js"></script>
   <script src="https://cdn.jsdelivr.net/npm/lunr-languages@1.4.0/lunr.pt.js"></script>
   
   <!-- Scripts de busca -->
   <script src="js/search-data.js"></script>
   <script src="js/search-engine.js"></script>
   <script src="js/search-ui.js"></script>

4. Abra a página e clique no ícone de lupa (🔍)

════════════════════════════════════════════════════════════

✨ RECURSOS:

✅ Busca em TODAS as páginas simultaneamente
✅ Modal que abre no canto direito (drawer)
✅ 42 itens de conteúdo indexados
✅ Suporte completo a português
✅ Atalho: Ctrl+K (Windows/Linux) ou Cmd+K (Mac)
✅ Fechar: ESC
✅ Relevância dos resultados (score)
✅ Sem dependências (só Lunr do CDN)

════════════════════════════════════════════════════════════

📝 ADICIONAR NOVO CONTEÚDO:

Edite search-data.js e adicione:

{
    id: '999',
    page: 'conteudo',        // index, conteudo, ciclo, sobre
    title: 'Seu Título',
    section: 'Nome da Seção',
    content: 'Conteúdo que quer pesquisar...'
}

Pronto! A busca já encontra automaticamente.

════════════════════════════════════════════════════════════

🎨 CORES (Dark Theme):
   Background: #06110a
   Verde: #22c55e
   Texto: #ffffff

════════════════════════════════════════════════════════════

❓ DÚVIDAS?

• Console diz erro 404? → Verifique os caminhos (js/ css/)
• Lunr não carrega? → Precisa de internet para CDN
• Modal não aparece? → F12 → Console → vê erros

Bom uso! 🔍🚀
