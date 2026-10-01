import { eventBus } from '../core/EventBus.js';
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
    this.btnStart.addEventListener('click', () => {
      soundManager.init();
      this.modalStart.style.display = 'none';
      this.hud.style.display = 'block';
      this.touchOverlay.show(true);
      gameStateMachine.setState(STATES.PLAYING);
    });

    this.btnRestart.addEventListener('click', () => {
      this.modalEnd.style.display = 'none';
      this.hud.style.display = 'block';
      this.touchOverlay.show(true);
      eventBus.emit('resetPlayer');
      eventBus.emit('resetMission');
      gameStateMachine.setState(STATES.PLAYING);
    });

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
      this.showEndScreen('MISSÃO CUMPRIDA!', 'Todos os dados sigilosos foram coletados com sucesso e o drone retornou à base.');
    });
  }

  showEndScreen(title, message) {
    this.hud.style.display = 'none';
    this.touchOverlay.show(false);
    document.getElementById('end-title').innerText = title;
    document.getElementById('end-message').innerText = message;
    this.modalEnd.style.display = 'flex';
  }
}
