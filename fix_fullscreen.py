import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Adicionar Meta Tags para Forçar Modo App Mobile
meta_tags = '''  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'''

if '<meta name="viewport"' in html:
    html = re.sub(r'<meta name="viewport"[^>]*>', meta_tags, html, count=1)

# 2. Injetar Regras de CSS com Margem de Segurança (Safe Area)
css_fix = '''
<style>
  html, body {
    overflow: hidden !important;
    position: fixed;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    touch-action: none;
  }

  /* Recuo de segurança para a barra do navegador não cobrir a interface */
  body {
    padding-top: max(10px, env(safe-area-inset-top));
    padding-bottom: max(15px, env(safe-area-inset-bottom));
    padding-left: max(10px, env(safe-area-inset-left));
    padding-right: max(10px, env(safe-area-inset-right));
  }

  /* Botão de Tela Cheia no topo */
  #fs-btn {
    position: absolute;
    top: max(10px, env(safe-area-inset-top));
    right: max(10px, env(safe-area-inset-right));
    z-index: 99999;
    background: rgba(0, 0, 0, 0.85);
    color: #00ffcc;
    border: 1px solid #00ffcc;
    padding: 6px 12px;
    font-size: 11px;
    font-family: monospace;
    border-radius: 4px;
    font-weight: bold;
  }
</style>
'''

if '</head>' in html:
    html = html.replace('</head>', css_fix + '\n</head>')

# 3. Adicionar Função JS para Alternar Tela Cheia
fs_script = '''
<button id="fs-btn" onclick="goFullscreen()">📺 TELA CHEIA</button>
<script>
function goFullscreen() {
  const doc = document.documentElement;
  if (!document.fullscreenElement && !document.webkitFullscreenElement) {
    if (doc.requestFullscreen) {
      doc.requestFullscreen();
    } else if (doc.webkitRequestFullscreen) {
      doc.webkitRequestFullscreen();
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    }
  }
}
</script>
'''

if '</body>' in html:
    html = html.replace('</body>', fs_script + '\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Ajuste de Tela Cheia e Layout aplicado com sucesso!")
