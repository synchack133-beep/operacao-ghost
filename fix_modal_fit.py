import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# CSS para forçar o painel a caber na tela horizontal do celular
responsive_modal_css = '''
<style>
  /* Ajuste de emergência para telas horizontais baixas (Celulares em Landscape) */
  @media screen and (max-height: 500px) {
    #modal, .modal, #instructions-modal, #start-modal, div[class*="modal"], div[id*="modal"] {
      position: fixed !important;
      top: 50% !important;
      left: 50% !important;
      transform: translate(-50%, -50%) !important;
      width: 90vw !important;
      max-width: 580px !important;
      max-height: 94vh !important;
      padding: 10px 16px !important;
      margin: 0 !important;
      box-sizing: border-box !important;
      overflow-y: auto !important;
      -webkit-overflow-scrolling: touch !important;
    }

    #modal h1, .modal h1, #modal h2, .modal h2 {
      font-size: 15px !important;
      margin: 2px 0 4px 0 !important;
    }

    #modal p, .modal p, #modal div, .modal div {
      font-size: 11px !important;
      line-height: 1.25 !important;
      margin: 3px 0 !important;
    }

    /* Garante que a área dos botões fique visível */
    #modal button, .modal button, .btn, #start-btn, button {
      padding: 6px 16px !important;
      font-size: 12px !important;
      margin: 6px 4px 2px 4px !important;
      display: inline-block !important;
    }
  }
</style>
'''

if '</head>' in html:
    html = html.replace('</head>', responsive_modal_css + '\n</head>')
else:
    html = responsive_modal_css + html

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Painel ajustado com sucesso!")
