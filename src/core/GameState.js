import { eventBus } from './EventBus.js';

export const STATES = {
  MENU: 'MENU',
  PLAYING: 'PLAYING',
  PAUSED: 'PAUSED',
  VICTORY: 'VICTORY',
  GAMEOVER: 'GAMEOVER'
};

export class GameStateMachine {
  constructor() {
    this.currentState = STATES.MENU;
  }
  setState(newState) {
    if (this.currentState === newState) return;
    const previousState = this.currentState;
    this.currentState = newState;
    eventBus.emit('gameStateChanged', { state: newState, previousState });
  }
  isPlaying() {
    return this.currentState === STATES.PLAYING;
  }
}
export const gameStateMachine = new GameStateMachine();
