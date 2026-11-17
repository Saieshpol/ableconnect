import React, { createContext, useContext, useState, useEffect } from 'react';
import { speech } from '../services/speech';

interface AccessibilityContextType {
  highContrast: boolean;
  toggleHighContrast: () => void;
  fontScale: number; // 1.0, 1.15, 1.3
  setFontScale: (scale: number) => void;
  increaseFontScale: () => void;
  decreaseFontScale: () => void;
  reducedMotion: boolean;
  toggleReducedMotion: () => void;
  speechEnabled: boolean;
  toggleSpeech: () => void;
  speakText: (text: string) => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export const AccessibilityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [highContrast, setHighContrast] = useState<boolean>(() => {
    return localStorage.getItem('able_high_contrast') === 'true';
  });

  const [fontScale, setFontScaleState] = useState<number>(() => {
    const saved = localStorage.getItem('able_font_scale');
    return saved ? parseFloat(saved) : 1.0;
  });

  const [reducedMotion, setReducedMotion] = useState<boolean>(() => {
    return localStorage.getItem('able_reduced_motion') === 'true';
  });

  const [speechEnabled, setSpeechEnabled] = useState<boolean>(() => {
    const saved = localStorage.getItem('able_speech_enabled');
    return saved !== null ? saved === 'true' : true;
  });

  useEffect(() => {
    // Apply contrast class to body
    if (highContrast) {
      document.body.classList.add('high-contrast');
    } else {
      document.body.classList.remove('high-contrast');
    }
    localStorage.setItem('able_high_contrast', String(highContrast));
  }, [highContrast]);

  useEffect(() => {
    // Apply font-scale CSS variable
    document.documentElement.style.setProperty('--font-scale', String(fontScale));
    localStorage.setItem('able_font_scale', String(fontScale));
  }, [fontScale]);

  useEffect(() => {
    if (reducedMotion) {
      document.body.classList.add('reduced-motion');
    } else {
      document.body.classList.remove('reduced-motion');
    }
    localStorage.setItem('able_reduced_motion', String(reducedMotion));
  }, [reducedMotion]);

  useEffect(() => {
    localStorage.setItem('able_speech_enabled', String(speechEnabled));
  }, [speechEnabled]);

  const toggleHighContrast = () => setHighContrast(prev => !prev);
  const toggleReducedMotion = () => setReducedMotion(prev => !prev);
  const toggleSpeech = () => setSpeechEnabled(prev => !prev);

  const setFontScale = (scale: number) => {
    const bounded = Math.max(0.9, Math.min(1.4, scale));
    setFontScaleState(bounded);
  };

  const increaseFontScale = () => {
    setFontScaleState(prev => (prev < 1.3 ? Number((prev + 0.1).toFixed(2)) : prev));
  };

  const decreaseFontScale = () => {
    setFontScaleState(prev => (prev > 0.9 ? Number((prev - 0.1).toFixed(2)) : prev));
  };

  const speakText = (text: string) => {
    if (speechEnabled) {
      speech.speak(text);
    }
  };

  return (
    <AccessibilityContext.Provider
      value={{
        highContrast,
        toggleHighContrast,
        fontScale,
        setFontScale,
        increaseFontScale,
        decreaseFontScale,
        reducedMotion,
        toggleReducedMotion,
        speechEnabled,
        toggleSpeech,
        speakText,
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = (): AccessibilityContextType => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};
