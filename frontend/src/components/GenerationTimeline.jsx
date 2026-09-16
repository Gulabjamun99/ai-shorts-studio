import React from 'react';
import { Loader2, CheckCircle2, Video, Music, Layers, ShieldCheck, Film } from 'lucide-react';

const PIPELINE_STEPS = [
  { key: 'GENERATING_REFERENCE', label: 'Reference & Themes', icon: Film, desc: 'Locking visual continuity and scene themes' },
  { key: 'GENERATING_SEGMENT_1', label: 'Scene 1: Hook', icon: Video, desc: 'Generating hook & problem statement' },
  { key: 'GENERATING_SEGMENT_2', label: 'Scene 2: Demonstration', icon: Video, desc: 'Generating smooth technique & demonstration' },
  { key: 'GENERATING_SEGMENT_3', label: 'Scene 3: Execution & Tip', icon: Video, desc: 'Generating results, execution & smart tip' },
  { key: 'GENERATING_SEGMENT_4', label: 'Scene 4: Payoff & CTA', icon: Video, desc: 'Delivering final payoff and Call to Action' },
  { key: 'VOICE_GENERATING', label: 'Neural Audio & Voiceover', icon: Music, desc: 'Master narration & synchronized speech synthesis' },
  { key: 'ASSEMBLING', label: 'Vids Assembly & Motion', icon: Layers, desc: 'Concatenating 9:16 vertical stream with Ken Burns motion' },
  { key: 'QA', label: '12-Point QA Gate', icon: ShieldCheck, desc: 'Auditing continuity, audio sync, & compliance' }
];

export default function GenerationTimeline({ currentStatus, progress = 0, errorMessage }) {
  const getStepStatus = (stepKey, index) => {
    const stepKeys = PIPELINE_STEPS.map(s => s.key);
    const currentIndex = stepKeys.indexOf(currentStatus);

    if (currentStatus === 'READY') return 'completed';
    if (currentStatus === 'FAILED') return index <= currentIndex ? 'failed' : 'pending';
    if (currentIndex === -1) return 'pending';

    if (index < currentIndex) return 'completed';
    if (index === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 sm:p-8 max-w-3xl mx-auto shadow-2xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
            AI Video Generation Pipeline
          </h3>
          <p className="text-xs text-gray-400 mt-1">
            Generating continuous Google Vids-style 9:16 vertical short...
          </p>
        </div>
        <span className="text-xl font-extrabold font-mono text-blue-400 bg-blue-950/50 px-3 py-1 rounded-xl border border-blue-800/40">
          {progress}%
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-900 rounded-full h-2.5 overflow-hidden border border-gray-800">
        <div
          className="bg-gradient-to-r from-blue-600 via-indigo-500 to-emerald-500 h-2.5 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${Math.max(5, progress)}%` }}
        ></div>
      </div>

      {/* Pipeline Stepper */}
      <div className="space-y-3 pt-2">
        {PIPELINE_STEPS.map((step, idx) => {
          const status = getStepStatus(step.key, idx);
          const Icon = step.icon;

          return (
            <div
              key={step.key}
              className={`flex items-center gap-4 p-3 rounded-xl border transition-all ${
                status === 'active'
                  ? 'bg-blue-950/20 border-blue-500/50 shadow-md shadow-blue-500/5'
                  : status === 'completed'
                  ? 'bg-gray-900/40 border-gray-800/80 text-gray-300'
                  : 'bg-gray-950/20 border-gray-900 text-gray-600'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                  status === 'active'
                    ? 'bg-blue-600 text-white animate-pulse'
                    : status === 'completed'
                    ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-gray-800 text-gray-500'
                }`}
              >
                {status === 'completed' ? (
                  <CheckCircle2 className="w-4 h-4" />
                ) : status === 'active' ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className={`text-xs font-semibold ${status === 'active' ? 'text-white' : ''}`}>
                    {step.label}
                  </h4>
                  <span className="text-[10px] uppercase font-bold tracking-wider text-gray-500">
                    Step {idx + 1}
                  </span>
                </div>
                <p className="text-[11px] text-gray-400 truncate mt-0.5">{step.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      {errorMessage && (
        <div className="p-3 bg-red-950/40 border border-red-800/60 rounded-xl text-xs text-red-300">
          <strong>Error encountered:</strong> {errorMessage}
        </div>
      )}
    </div>
  );
}
