# OPERAÇÃO GHOST — Drone Warfare

Protótipo jogável 3D para navegador, com Three.js carregado via CDN.

## Como testar
1. Abra `index.html` em um navegador moderno com conexão à internet.
2. A conexão é necessária para carregar o módulo Three.js do CDN.
3. Toque em **INICIAR MISSÃO**.

## Controles
- PC: WASD para mover, Espaço para subir, Shift para descer, mouse para olhar, clique para disparar pulso fictício, E para interagir e Esc para pausar.
- Celular: joystick no lado esquerdo, arraste no lado direito para olhar, botões subir/descer, PULSO e AÇÃO.
- VISÃO alterna entre normal, noturna e térmica estilizada.

## Publicação gratuita
Crie um repositório público no GitHub, envie `index.html` e ative **Settings → Pages → Deploy from a branch → main / root**. O jogo não usa backend, conta de jogador ou chaves de API. O GitHub Pages publica arquivos estáticos; a biblioteca Three.js é obtida por CDN.

## Limitações desta versão
- É um protótipo inicial, não um simulador militar realista.
- O cenário, os veículos e os efeitos usam geometria procedural simples.
- O combate é uma mecânica arcade fictícia.
- O som é sintetizado pelo navegador e pode depender de interação do usuário.
- A biblioteca Three.js precisa estar acessível via internet.
