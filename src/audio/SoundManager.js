export class SoundManager {
  constructor() {
    this.ctx = null;
    this.isMuted = false;
    this.motorOsc = null;
    this.motorGain = null;
    this.isInitialized = false;
  }

  init() {
    if (this.isInitialized) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      this.ctx = new AudioCtx();

      this.motorOsc = this.ctx.createOscillator();
      this.motorGain = this.ctx.createGain();
      const filter = this.ctx.createBiquadFilter();

      this.motorOsc.type = 'sawtooth';
      this.motorOsc.frequency.setValueAtTime(60, this.ctx.currentTime);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(350, this.ctx.currentTime);

      this.motorGain.gain.setValueAtTime(0.08, this.ctx.currentTime);

      this.motorOsc.connect(filter);
      filter.connect(this.motorGain);
      this.motorGain.connect(this.ctx.destination);

      this.motorOsc.start();
      this.isInitialized = true;
    } catch (e) {
      console.warn('AudioContext init error', e);
    }
  }

  resume() {
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  updateMotor(throttle, speed) {
    if (!this.isInitialized || this.isMuted || !this.ctx) return;
    const baseFreq = 65 + Math.abs(throttle) * 70 + (speed / 60) * 80;
    this.motorOsc.frequency.setTargetAtTime(baseFreq, this.ctx.currentTime, 0.05);
  }

  playExplosion() {
    if (!this.isInitialized || this.isMuted || !this.ctx) return;
    const now = this.ctx.currentTime;
    
    const bufferSize = this.ctx.sampleRate * 0.8;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2 - 1;
    }

    const whiteNoise = this.ctx.createBufferSource();
    whiteNoise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(800, now);
    filter.frequency.exponentialRampToValueAtTime(40, now + 0.7);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.4, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);

    whiteNoise.connect(filter);
    filter.connect(gain);
    gain.connect(this.ctx.destination);

    whiteNoise.start(now);
  }

  playLaunch() {
    if (!this.isInitialized || this.isMuted || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(300, now);
    osc.frequency.exponentialRampToValueAtTime(1200, now + 0.25);

    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 0.3);
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    if (this.motorGain) {
      this.motorGain.gain.setValueAtTime(this.isMuted ? 0 : 0.08, this.ctx ? this.ctx.currentTime : 0);
    }
    return this.isMuted;
  }
}

export const soundManager = new SoundManager();