import React, { useState } from 'react';
import { api } from '../../services/api';
import { speech } from '../../services/speech';
import { Smile, Heart, Moon, HelpCircle, Frown, AlertCircle, Sparkles, X, Check } from 'lucide-react';

interface EmotionCheckinModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (emotion: string) => void;
}

export const EmotionCheckinModal: React.FC<EmotionCheckinModalProps> = ({ isOpen, onClose, onComplete }) => {
  const [selectedEmotion, setSelectedEmotion] = useState<string | null>(null);
  const [energyLevel, setEnergyLevel] = useState<number>(3);
  const [notes, setNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const emotions = [
    { key: 'happy', label: 'Happy', icon: <Smile className="w-10 h-10 text-emerald-500" />, bg: 'bg-emerald-50 border-emerald-300' },
    { key: 'calm', label: 'Calm', icon: <Heart className="w-10 h-10 text-teal-500" />, bg: 'bg-teal-50 border-teal-300' },
    { key: 'tired', label: 'Tired', icon: <Moon className="w-10 h-10 text-slate-500" />, bg: 'bg-slate-50 border-slate-300' },
    { key: 'confused', label: 'Confused', icon: <HelpCircle className="w-10 h-10 text-amber-500" />, bg: 'bg-amber-50 border-amber-300' },
    { key: 'sad', label: 'Sad', icon: <Frown className="w-10 h-10 text-blue-500" />, bg: 'bg-blue-50 border-blue-300' },
    { key: 'anxious', label: 'Overwhelmed', icon: <AlertCircle className="w-10 h-10 text-rose-500" />, bg: 'bg-rose-50 border-rose-300' },
  ];

  const handleSelect = (key: string, label: string) => {
    setSelectedEmotion(key);
    speech.speak(`I feel ${label}`);
  };

  const handleSubmit = async () => {
    if (!selectedEmotion) return;
    setIsSubmitting(true);
    try {
      await api.submitEmotionCheckin(selectedEmotion, notes, energyLevel);
      onComplete(selectedEmotion);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="emotion-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in"
    >
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 relative border border-slate-200 shadow-2xl space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-teal-50 text-teal-600 rounded-xl">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 id="emotion-title" className="font-extrabold text-xl text-slate-900">
                Daily Emotion Check-in
              </h3>
              <p className="text-xs text-slate-500">
                How are you feeling right now? (Optional)
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            title="Skip or Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Emotions Big Grid */}
        <div className="grid grid-cols-3 gap-3">
          {emotions.map((item) => (
            <button
              key={item.key}
              onClick={() => handleSelect(item.key, item.label)}
              className={`flex flex-col items-center justify-center p-4 rounded-2xl border-2 transition-all cursor-pointer ${
                selectedEmotion === item.key
                  ? 'border-teal-600 bg-teal-50 ring-4 ring-teal-500/20 scale-105'
                  : `${item.bg} hover:scale-102`
              }`}
            >
              <div className="mb-2">{item.icon}</div>
              <span className="font-bold text-sm text-slate-900">{item.label}</span>
            </button>
          ))}
        </div>

        {/* Energy Scale */}
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
            Energy Level: {energyLevel} / 5
          </label>
          <input
            type="range"
            min="1"
            max="5"
            value={energyLevel}
            onChange={(e) => setEnergyLevel(parseInt(e.target.value))}
            className="w-full accent-teal-600 cursor-pointer h-2 bg-slate-200 rounded-lg"
          />
          <div className="flex justify-between text-[11px] text-slate-500 mt-1 font-medium">
            <span>Low Energy</span>
            <span>Balanced</span>
            <span>High Energy</span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center justify-between gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-600 hover:bg-slate-100 text-sm font-semibold transition-colors"
          >
            Skip for Now
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!selectedEmotion || isSubmitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm shadow-sm transition-all disabled:opacity-40"
          >
            <Check className="w-4 h-4" />
            <span>{isSubmitting ? 'Saving...' : 'Share Check-in'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
