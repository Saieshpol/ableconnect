import React, { useState } from 'react';
import { api } from '../../services/api';
import { speech } from '../../services/speech';
import { SimplifyResult } from '../../types';
import {
  X, Sparkles, Volume2, Copy, Check, ArrowRight, BookOpen,
  Edit3, Send, CheckCircle2, Clock, Eye, AlertCircle, Info
} from 'lucide-react';

interface InstructionSimplifierModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const InstructionSimplifierModal: React.FC<InstructionSimplifierModalProps> = ({ isOpen, onClose }) => {
  const [inputText, setInputText] = useState(
    'Complete the exercise in your notebook and submit it before the end of the session.'
  );
  const [result, setResult] = useState<SimplifyResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleSimplify = async () => {
    if (!inputText.trim()) return;
    setIsLoading(true);
    try {
      const data = await api.simplifyInstruction(inputText);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSpeakAudio = () => {
    if (result?.audio_ready_text) {
      speech.speak(result.audio_ready_text);
    }
  };

  const handleCopy = () => {
    if (!result) return;
    const textToCopy = result.steps.map(s => `${s.step_number}. ${s.text}`).join('\n');
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderStepIcon = (iconName: string) => {
    switch (iconName) {
      case 'book-open': return <BookOpen className="w-5 h-5 text-teal-600" />;
      case 'edit-3': return <Edit3 className="w-5 h-5 text-indigo-600" />;
      case 'send': return <Send className="w-5 h-5 text-cyan-600" />;
      case 'eye': return <Eye className="w-5 h-5 text-purple-600" />;
      case 'clock': return <Clock className="w-5 h-5 text-amber-600" />;
      default: return <CheckCircle2 className="w-5 h-5 text-emerald-600" />;
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="simplifier-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto"
    >
      <div className="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 relative border border-slate-200 shadow-2xl my-8">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          aria-label="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-teal-50 text-teal-600 rounded-xl">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h3 id="simplifier-title" className="text-xl font-bold text-slate-900">
              Teacher Instruction Simplifier
            </h3>
            <p className="text-xs text-slate-500">
              Break complex instructions into step-by-step, plain-language items with visual cues.
            </p>
          </div>
        </div>

        {/* Input Text Area */}
        <div className="space-y-2 mb-4">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600">
            Original Classroom Instruction
          </label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={3}
            className="w-full p-3.5 border border-slate-300 rounded-2xl text-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none"
            placeholder="Type or paste standard assignment instructions here..."
          />
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400">
              Rule-based engine with optional AI enhancement. Always teacher-reviewable.
            </span>
            <button
              onClick={handleSimplify}
              disabled={isLoading || !inputText.trim()}
              className="flex items-center gap-2 px-5 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all disabled:opacity-50 cursor-pointer"
            >
              <Sparkles className="w-4 h-4" />
              <span>{isLoading ? 'Breaking Down...' : 'Simplify Steps'}</span>
            </button>
          </div>
        </div>

        {/* Simplified Output Breakdown */}
        {result && (
          <div className="mt-6 pt-5 border-t border-slate-100 space-y-4 animate-in fade-in">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-teal-800 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-teal-600" />
                <span>Accessible Sequential Steps ({result.method_used === 'ai_provider' ? 'AI Enhanced' : 'Rule-Based Engine'})</span>
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleSpeakAudio}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
                  title="Listen to steps read aloud"
                >
                  <Volume2 className="w-3.5 h-3.5 text-teal-600" />
                  <span>Read Aloud</span>
                </button>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
                  title="Copy formatted steps"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            </div>

            <div className="space-y-2">
              {result.steps.map((step) => (
                <div
                  key={step.step_number}
                  className="flex items-center gap-3 p-3.5 rounded-xl border border-teal-200/80 bg-teal-50/40 shadow-2xs"
                >
                  <div className="w-8 h-8 rounded-lg bg-teal-600 text-white flex items-center justify-center font-extrabold text-sm shrink-0">
                    {step.step_number}
                  </div>
                  <div className="p-2 bg-white rounded-lg shadow-2xs shrink-0">
                    {renderStepIcon(step.icon)}
                  </div>
                  <span className="font-bold text-slate-800 text-sm grow">
                    {step.text}
                  </span>
                </div>
              ))}
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 flex items-center gap-2">
              <Info className="w-4 h-4 text-slate-400 shrink-0" />
              <span>
                Summary: {result.simplified_summary}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
