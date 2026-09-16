import React, { useState } from 'react';
import { CheckCircle, Edit3, RotateCw, Clock, Video, FileText, AlertTriangle, Layers } from 'lucide-react';

export default function ScriptApprovalModal({
  scriptData,
  onApprove,
  onRegenerate,
  onClose,
  approving
}) {
  if (!scriptData) return null;

  const [isEditing, setIsEditing] = useState(false);
  const [masterScript, setMasterScript] = useState(scriptData.master_script || '');
  const [segments, setSegments] = useState(scriptData.segments || []);

  const handleSegmentChange = (index, field, value) => {
    const updated = [...segments];
    updated[index] = { ...updated[index], [field]: value };
    setSegments(updated);
    
    // Update master script text accordingly
    const newMaster = updated.map(s => s.narration).join(' ');
    setMasterScript(newMaster);
  };

  const handleApprove = () => {
    onApprove({
      masterScript,
      segments
    });
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#111827] border border-gray-700 rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="px-6 py-4 bg-gray-900 border-b border-gray-800 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-400" />
                Script Review & Approval Gate
              </h3>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Non-Negotiable Step
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Review and customize your ~{scriptData.estimated_duration || 48}s script before generating video segments.
            </p>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-gray-800 border border-gray-700 text-xs text-white">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>Est. ~{scriptData.estimated_duration || 48}s</span>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-sm">
          
          {/* Master Script Box */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-400" />
                Master Script ({scriptData.language})
              </span>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
              >
                <Edit3 className="w-3.5 h-3.5" />
                {isEditing ? 'Done Editing' : 'Edit Script'}
              </button>
            </div>

            {isEditing ? (
              <textarea
                rows={3}
                value={masterScript}
                onChange={(e) => setMasterScript(e.target.value)}
                className="w-full bg-gray-950 border border-gray-700 rounded-lg p-3 text-xs text-white focus:outline-none focus:border-blue-500"
              />
            ) : (
              <p className="text-gray-200 text-xs leading-relaxed bg-gray-950/60 rounded-lg p-3 border border-gray-800">
                "{masterScript}"
              </p>
            )}
          </div>

          {/* Segments Breakdown */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">
              {segments.length} Continuous Generation Segments (Google Vids Style)
            </h4>

            {segments.map((seg, idx) => (
              <div key={idx} className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-xs">
                      {seg.segment_index}
                    </span>
                    <span className="font-semibold text-white text-xs">
                      {idx === 0
                        ? 'Hook & Problem'
                        : idx === 1
                        ? 'Action & Demonstration'
                        : idx === 2
                        ? (segments.length >= 4 ? 'Results & Smart Tip' : 'Result & Call to Action')
                        : 'Payoff & Call to Action'}
                    </span>
                  </div>
                  <span className="text-[11px] text-gray-400 bg-gray-800 px-2 py-0.5 rounded">
                    ~{seg.duration_sec}s
                  </span>
                </div>

                {/* Narration */}
                <div>
                  <label className="block text-[11px] font-medium text-gray-400 mb-1">Narration / Spoken Voice</label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={seg.narration}
                      onChange={(e) => handleSegmentChange(idx, 'narration', e.target.value)}
                      className="w-full bg-gray-950 border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white"
                    />
                  ) : (
                    <p className="text-xs text-gray-200 bg-gray-950/40 px-2.5 py-1.5 rounded border border-gray-800/80">
                      {seg.narration}
                    </p>
                  )}
                </div>

                {/* Visual Directive */}
                <div>
                  <label className="block text-[11px] font-medium text-gray-400 mb-1 flex items-center gap-1.5">
                    <Video className="w-3.5 h-3.5 text-indigo-400" />
                    Visual Camera & Action Directive
                  </label>
                  <p className="text-[11px] text-gray-300 italic bg-gray-950/40 px-2.5 py-1.5 rounded border border-gray-800/80">
                    {seg.visual_description}
                  </p>
                </div>

                {/* On-screen text */}
                <div>
                  <label className="block text-[11px] font-medium text-gray-400 mb-1">On-Screen Caption / Graphic</label>
                  <p className="text-[11px] font-mono text-emerald-400 bg-gray-950/40 px-2.5 py-1 rounded border border-gray-800/80">
                    "{seg.on_screen_text}"
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-start gap-2.5 bg-blue-950/30 border border-blue-800/50 rounded-xl p-3 text-xs text-blue-200">
            <AlertTriangle className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <p>
              Once approved, the engine establishes character & product references, generates all 3 video segments with frame continuity, and synchronizes the audio.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 bg-gray-900 border-t border-gray-800 flex items-center justify-between">
          <button
            type="button"
            onClick={onRegenerate}
            disabled={approving}
            className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 hover:text-white px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition"
          >
            <RotateCw className="w-3.5 h-3.5" />
            Regenerate Script
          </button>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={approving}
              className="text-xs font-semibold text-gray-400 hover:text-white px-4 py-2"
            >
              Cancel
            </button>

            <button
              type="button"
              onClick={handleApprove}
              disabled={approving}
              className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold px-5 py-2.5 rounded-xl shadow-lg shadow-emerald-600/30 transition disabled:opacity-50"
            >
              {approving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Starting Generation Pipeline...</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>Approve Script & Create Video</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
