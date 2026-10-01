import os

# Atualiza index.html para garantir pointer-events e estilo de toque
index_path = 'index.html'
if os.path.exists(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Injeta melhorias no CSS do botão
    old_btn_css = ".btn-main { display: inline-block;"
    new_btn_css = ".btn-main { display: inline-block; pointer-events: auto !important; touch-action: manipulation; -webkit-tap-highlight-color: transparent; "
    if old_btn_css in content:
        content = content.replace(old_btn_css, new_btn_css)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

# Atualiza UIManager.js para escutar eventos touchstart e click simultaneamente
ui_path = 'src/ui/UIManager.js'
ui_code = '''import { eventBus } from '../core/EventBus.js';
import { gameStateMachine, STATES } from '../core/GameState.js';
import { soundManager } from '../audio/SoundManager.js';

export class UIManager {
  constructor(touchOverlay) {
    this.touchOverlay = touchOverlay;
    
    this.hud = document.getElementById('hud');
    this.modalStart = document.getElementById('modal-start');
    this.modalEnd = document.getElementById('modal-end');
    
    this.energyBar = document.getElementById('energy-bar');
    this.healthBar = document.getElementById('health-bar');
    this.intelCountText = document.getElementById('intel-count');
    this.missionStatusText = document.getElementById('mission-status');

    this.btnStart = document.getElementById('btn-start');
    this.btnRestart = document.getElementById('btn-restart');

    this.initEvents();
  }

  initEvents() {
    const startMission = (e) => {
      if (e) e.preventDefault();
      soundManager.init();
      if (this.modalStart) this.modalStart.style.display = 'none';
      if (this.hud) this.hud.style.display = 'block';
      this.touchOverlay.show(true);
      gameStateMachine.setState(STATES.PLAYING);
    };

    const restartMission = (e) => {
      if (e) e.preventDefault();
      if (this.modalEnd) this.modalEnd.style.display = 'none';
      if (this.hud) this.hud.style.display = 'block';
      this.touchOverlay.show(true);
      eventBus.emit('resetPlayer');
      eventBus.emit('resetMission');
      gameStateMachine.setState(STATES.PLAYING);
    };

    if (this.btnStart) {
      this.btnStart.addEventListener('click', startMission);
      this.btnStart.addEventListener('touchstart', startMission, { passive: false });
    }

    if (this.btnRestart) {
      this.btnRestart.addEventListener('click', restartMission);
      this.btnRestart.addEventListener('touchstart', restartMission, { passive: false });
    }

    eventBus.on('energyUpdated', (val) => {
      if (this.energyBar) this.energyBar.style.width = `${Math.max(0, val)}%`;
    });

    eventBus.on('healthUpdated', (val) => {
      if (this.healthBar) this.healthBar.style.width = `${Math.max(0, val)}%`;
    });

    eventBus.on('intelUpdated', (data) => {
      if (this.intelCountText) this.intelCountText.innerText = `DADOS: ${data.collected} / ${data.total}`;
      if (data.collected >= data.total) {
        if (this.missionStatusText) {
          this.missionStatusText.innerText = "RETORNE À ZONA DE EXTRAÇÃO!";
          this.missionStatusText.style.color = "#00ff96";
        }
      }
    });

    eventBus.on('playerDied', (reason) => {
      this.showEndScreen('FALHA NA MISSÃO', reason);
    });

    eventBus.on('missionComplete', () => {
      this.showEndScreen('MISSÃO CUMPRIDA!', 'Todos os dados sigilosos foram coletados com sucesso.');
    });
  }

  showEndScreen(title, message) {
    if (this.hud) this.hud.style.display = 'none';
    this.touchOverlay.show(false);
    const endTitle = document.getElementById('end-title');
    const endMsg = document.getElementById('end-message');
    if (endTitle) endTitle.innerText = title;
    if (endMsg) endMsg.innerText = message;
    if (this.modalEnd) this.modalEnd.style.display = 'flex';
  }
}
'''

with open(ui_path, 'w', encoding='utf-8') as f:
    f.write(ui_code)

print("Ajustes de touch aplicados com sucesso!")
