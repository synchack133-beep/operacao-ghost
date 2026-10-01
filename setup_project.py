import os

files = {}

files['package.json'] = '''{
  "name": "operacao-ghost",
  "version": "2.0.0",
  "type": "module",
  "scripts": { "dev": "vite", "build": "vite build" },
  "devDependencies": { "vite": "^5.1.0" },
  "dependencies": { "three": "^0.162.0" }
}'''

files['README.md'] = '''# OPERAÇÃO GHOST - Tactical Drone Recon 3D

Jogo 3D de simulação e reconhecimento tático com drone desenvolvido em WebGL / Three.js com suporte completo a PC e dispositivos móveis (Touch UI).

## 🎮 Controles
- **Teclado / Mouse**: WASD (Mover), Espaço (Subir), Shift (Descer), E (Hackear Terminal), Mouse (Rotacionar Câmera).
- **Dispositivos Móveis**: Joystick virtual (Esquerda), Arrasto na tela (Câmera), Botões táticos t-btn (Direita).

## ⚙️ Edição e Parâmetros
Todas as configurações de velocidade, bateria, altitudes, câmera e missões estão centralizadas no arquivo:
`src/config/gameConfig.js`
'''

print("Criando diretórios e arquivos da arquitetura modular...")
os.makedirs('src/config', exist_ok=True)
os.makedirs('src/core', exist_ok=True)
os.makedirs('src/player', exist_ok=True)
os.makedirs('src/camera', exist_ok=True)
os.makedirs('src/input', exist_ok=True)
os.makedirs('src/world', exist_ok=True)
os.makedirs('src/gameplay', exist_ok=True)
os.makedirs('src/audio', exist_ok=True)
os.makedirs('src/ui', exist_ok=True)

print("Estrutura gerada com sucesso!")
