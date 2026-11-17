import React, { useState, useEffect } from 'react';
import { CommunicationBoard, CommunicationSymbol } from '../../types';
import { api } from '../../services/api';
import { speech } from '../../services/speech';
import { useAccessibility } from '../../context/AccessibilityContext';
import {
  Volume2, Trash2, Send, CheckCircle2, Sparkles, Coffee,
  Heart, Smile, Frown, HelpCircle, Moon, AlertCircle, User,
  Check, X, LifeBuoy, Bath, Droplet, Clock
} from 'lucide-react';

interface AACBoardProps {
  onSentToTeacher?: (sentence: string) => void;
}

export const AACBoard: React.FC<AACBoardProps> = ({ onSentToTeacher }) => {
  const [boards, setBoards] = useState<CommunicationBoard[]>([]);
  const [activeBoardIndex, setActiveBoardIndex] = useState(0);
  const [selectedTokens, setSelectedTokens] = useState<CommunicationSymbol[]>([]);
  const [synthesizedSentence, setSynthesizedSentence] = useState<string>('');
  const [isSending, setIsSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState(false);
  const { speakText } = useAccessibility();

  useEffect(() => {
    const fetchBoards = async () => {
      const data = await api.getBoards();
      setBoards(data);
    };
    fetchBoards();
  }, []);

  // Update synthesized sentence whenever tokens change
  useEffect(() => {
    const updateSentence = async () => {
      if (selectedTokens.length === 0) {
        setSynthesizedSentence('');
        return;
      }
      try {
        const labels = selectedTokens.map(t => t.label);
        const res = await api.synthesizeSentence(labels);
        setSynthesizedSentence(res.sentence);
      } catch {
        setSynthesizedSentence(selectedTokens.map(t => t.speech_text).join(' '));
      }
    };
    updateSentence();
  }, [selectedTokens]);

  const handleCardClick = (symbol: CommunicationSymbol) => {
    // Audio feedback for individual card
    speech.speak(symbol.speech_text);
    setSelectedTokens(prev => [...prev, symbol]);
  };

  const handleRemoveToken = (index: number) => {
    setSelectedTokens(prev => prev.filter((_, i) => i !== index));
  };

  const handleClearAll = () => {
    setSelectedTokens([]);
    setSynthesizedSentence('');
    speakText("Cleared");
  };

  const handleSpeakSentence = () => {
    if (synthesizedSentence) {
      speech.speak(synthesizedSentence);
    }
  };

  const handleSendToTeacher = async () => {
    if (!synthesizedSentence) return;
    setIsSending(true);
    try {
      await api.submitRequest('custom', synthesizedSentence);
      speech.speak("Sent to teacher: " + synthesizedSentence);
      setSendSuccess(true);
      if (onSentToTeacher) onSentToTeacher(synthesizedSentence);
      setTimeout(() => {
        setSendSuccess(false);
        setSelectedTokens([]);
        setSynthesizedSentence('');
      }, 2500);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSending(false);
    }
  };

  const renderIcon = (iconName: string) => {
    switch (iconName) {
      case 'help-circle': return <HelpCircle className="w-8 h-8" />;
      case 'coffee': return <Coffee className="w-8 h-8" />;
      case 'bath': return <Bath className="w-8 h-8" />;
      case 'droplet': return <Droplet className="w-8 h-8" />;
      case 'clock': return <Clock className="w-8 h-8" />;
      case 'smile': return <Smile className="w-8 h-8" />;
      case 'heart': return <Heart className="w-8 h-8" />;
      case 'moon': return <Moon className="w-8 h-8" />;
      case 'frown': return <Frown className="w-8 h-8" />;
      case 'alert-circle': return <AlertCircle className="w-8 h-8" />;
      case 'user': return <User className="w-8 h-8" />;
      case 'life-buoy': return <LifeBuoy className="w-8 h-8" />;
      case 'check': return <Check className="w-8 h-8" />;
      case 'check-circle': return <CheckCircle2 className="w-8 h-8" />;
      case 'x': return <X className="w-8 h-8" />;
      default: return <Sparkles className="w-8 h-8" />;
    }
  };

  const currentBoard = boards[activeBoardIndex];

  return (
    <div className="bg-white rounded-3xl p-4 sm:p-6 shadow-sm border border-slate-200 space-y-6">
      {/* 1. Sentence Strip Area */}
      <div className="bg-slate-50 border-2 border-teal-500/40 rounded-2xl p-4 shadow-inner min-h-[100px] flex flex-col justify-between">
        <div className="flex items-center justify-between gap-2 mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-teal-800 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-teal-600" />
            <span>Sentence Strip</span>
          </span>
          {selectedTokens.length > 0 && (
            <button
              onClick={handleClearAll}
              className="text-xs font-semibold text-rose-600 hover:text-rose-700 flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-rose-50 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          )}
        </div>

        {/* Selected Tokens Horizontal List */}
        <div className="flex flex-wrap items-center gap-2 min-h-[50px]">
          {selectedTokens.length === 0 ? (
            <p className="text-slate-400 italic text-sm select-none">
              Tap picture cards below to build a sentence...
            </p>
          ) : (
            selectedTokens.map((token, idx) => (
              <button
                key={`${token.id}-${idx}`}
                onClick={() => handleRemoveToken(idx)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border-2 border-teal-500 shadow-xs hover:border-rose-400 group transition-all"
                title="Tap to remove"
              >
                <span className="font-extrabold text-slate-800 text-base">{token.label}</span>
                <X className="w-3.5 h-3.5 text-slate-400 group-hover:text-rose-500" />
              </button>
            ))
          )}
        </div>

        {/* Synthesized Output & Action Buttons */}
        {synthesizedSentence && (
          <div className="mt-3 pt-3 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
            <div className="text-lg font-bold text-slate-900 bg-white px-3 py-1.5 rounded-xl border border-slate-200 grow">
              "{synthesizedSentence}"
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleSpeakSentence}
                className="flex items-center gap-2 px-4 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-sm shadow-sm transition-all"
                title="Speak sentence out loud"
              >
                <Volume2 className="w-5 h-5" />
                <span>Speak</span>
              </button>
              <button
                onClick={handleSendToTeacher}
                disabled={isSending || sendSuccess}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-sm shadow-sm transition-all ${
                  sendSuccess
                    ? 'bg-emerald-600 text-white'
                    : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                }`}
                title="Send sentence to teacher"
              >
                {sendSuccess ? (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    <span>Sent!</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>{isSending ? 'Sending...' : 'Send to Teacher'}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 2. Board Tabs (Categories) */}
      <div className="flex flex-wrap items-center gap-2">
        {boards.map((board, idx) => (
          <button
            key={board.id}
            onClick={() => {
              setActiveBoardIndex(idx);
              speakText(board.title);
            }}
            className={`px-4 py-2.5 rounded-2xl font-bold text-sm transition-all ${
              activeBoardIndex === idx
                ? 'bg-teal-600 text-white shadow-md shadow-teal-600/20 scale-102'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            {board.title}
          </button>
        ))}
      </div>

      {/* 3. Visual Picture Cards Grid */}
      {currentBoard && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 sm:gap-4">
          {currentBoard.symbols.map((symbol) => (
            <button
              key={symbol.id}
              onClick={() => handleCardClick(symbol)}
              className={`flex flex-col items-center justify-center p-4 sm:p-5 rounded-2xl border-2 transition-all transform hover:-translate-y-1 active:scale-95 shadow-xs hover:shadow-md cursor-pointer select-none text-center ${symbol.bg_color} ${symbol.border_color} focus:ring-4 focus:ring-teal-400/50`}
              style={{ minHeight: '120px' }}
            >
              <div className="text-slate-800 mb-2 transform group-hover:scale-110 transition-transform">
                {renderIcon(symbol.icon_name)}
              </div>
              <span className="font-extrabold text-base sm:text-lg text-slate-900 leading-tight">
                {symbol.label}
              </span>
              <span className="text-[11px] font-medium text-slate-500 mt-1 line-clamp-1">
                "{symbol.speech_text}"
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
