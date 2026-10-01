import { GAME_CONFIG } from '../config/gameConfig.js';
import { eventBus } from '../core/EventBus.js';
import { gameStateMachine, STATES } from '../core/GameState.js';
import { soundManager } from '../audio/SoundManager.js';

export class MissionManager {
  constructor(environment) {
    this.environment = environment;
    this.collectedCount = 0;
    this.totalIntel = GAME_CONFIG.MISSION.totalIntelCount;

    eventBus.on('actionTriggered', () => this.tryCollectIntel());
  }

  reset() {
    this.collectedCount = 0;
    GAME_CONFIG.MISSION.intelLocations.forEach(loc => loc.collected = false);
    eventBus.emit('intelUpdated', { collected: 0, total: this.totalIntel });
  }

  checkPlayerProximity(playerPos) {
    if (!gameStateMachine.isPlaying()) return;

    GAME_CONFIG.MISSION.intelLocations.forEach((loc) => {
      if (loc.collected) return;
      const dist = Math.hypot(playerPos.x - loc.x, playerPos.z - loc.z);
      if (dist < 3.5 && playerPos.y < 4.0) {
        eventBus.emit('nearIntel', loc.id);
      }
    });

    if (this.collectedCount >= this.totalIntel) {
      const ext = GAME_CONFIG.MISSION.extractionZone;
      const distExt = Math.hypot(playerPos.x - ext.x, playerPos.z - ext.z);
      if (distExt < ext.radius) {
        soundManager.playVictory();
        gameStateMachine.setState(STATES.VICTORY);
        eventBus.emit('missionComplete');
      }
    }
  }

  tryCollectIntel() {
    eventBus.emit('checkProximityAndCollect');
  }

  collect(id) {
    const loc = GAME_CONFIG.MISSION.intelLocations.find(l => l.id === id);
    if (loc && !loc.collected) {
      loc.collected = true;
      this.collectedCount++;
      soundManager.playIntelCollected();
      eventBus.emit('intelUpdated', { collected: this.collectedCount, total: this.totalIntel });

      const mesh = this.environment.intelMeshes.find(m => m.userData.id === id);
      if (mesh) mesh.visible = false;
    }
  }
}
