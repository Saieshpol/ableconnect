class SpeechService {
  private synth: SpeechSynthesis | null = null;
  private isAvailable = false;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
      this.isAvailable = true;
    }
  }

  isSupported(): boolean {
    return this.isAvailable;
  }

  speak(text: string, rate = 1.0, pitch = 1.0, onEnd?: () => void): void {
    if (!this.synth || !this.isAvailable) {
      console.warn('Speech synthesis is not supported in this browser.');
      if (onEnd) onEnd();
      return;
    }

    try {
      this.synth.cancel(); // Stop any currently playing audio

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = Math.max(0.5, Math.min(2.0, rate));
      utterance.pitch = Math.max(0.5, Math.min(1.5, pitch));
      utterance.lang = 'en-US';

      // Pick clear local voice if available
      const voices = this.synth.getVoices();
      const preferred = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha')));
      if (preferred) {
        utterance.voice = preferred;
      }

      if (onEnd) {
        utterance.onend = () => onEnd();
        utterance.onerror = () => onEnd();
      }

      this.synth.speak(utterance);
    } catch (err) {
      console.error('Speech synthesis error:', err);
      if (onEnd) onEnd();
    }
  }

  stop(): void {
    if (this.synth) {
      this.synth.cancel();
    }
  }
}

export const speech = new SpeechService();
