import React, { useEffect, useState } from 'react';
import { Activity, X, Database, Film, CheckCircle, AlertTriangle, HardDrive, Cpu } from 'lucide-react';
import { getAdminMetrics } from '../services/api';

export default function AdminMetricsModal({ onClose }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminMetrics()
      .then(data => setMetrics(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#111827] border border-gray-700 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-6 animate-in fade-in zoom-in-95">
        
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-bold text-white">System Observability & Metrics</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="py-12 flex justify-center text-xs text-gray-400">Loading metrics...</div>
        ) : metrics ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-3">
                <span className="text-[11px] text-gray-400 flex items-center gap-1 mb-1">
                  <Film className="w-3.5 h-3.5 text-blue-400" /> Total Projects
                </span>
                <span className="text-xl font-bold font-mono text-white">{metrics.total_projects}</span>
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-3">
                <span className="text-[11px] text-gray-400 flex items-center gap-1 mb-1">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> Generation Success
                </span>
                <span className="text-xl font-bold font-mono text-emerald-400">{metrics.success_rate_pct}%</span>
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-3">
                <span className="text-[11px] text-gray-400 flex items-center gap-1 mb-1">
                  <HardDrive className="w-3.5 h-3.5 text-purple-400" /> Storage Used
                </span>
                <span className="text-xl font-bold font-mono text-purple-400">{metrics.storage_usage_mb} MB</span>
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-3">
                <span className="text-[11px] text-gray-400 flex items-center gap-1 mb-1">
                  <Database className="w-3.5 h-3.5 text-yellow-400" /> QA Pass Rate
                </span>
                <span className="text-xl font-bold font-mono text-white">{metrics.qa_pass_rate_pct}%</span>
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-3">
                <span className="text-[11px] text-gray-400 flex items-center gap-1 mb-1">
                  <Activity className="w-3.5 h-3.5 text-emerald-400" /> Average QA Score
                </span>
                <span className="text-xl font-bold font-mono text-white">{metrics.qa_avg_score}%</span>
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-3">
                <span className="text-[11px] text-gray-400 flex items-center gap-1 mb-1">
                  <Cpu className="w-3.5 h-3.5 text-cyan-400" /> Default Provider
                </span>
                <span className="text-xs font-bold font-mono text-cyan-300 uppercase">{metrics.active_provider}</span>
              </div>
            </div>

            <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-3 text-xs text-gray-400 space-y-1">
              <div className="flex justify-between">
                <span>Model Targeted:</span>
                <strong className="text-gray-200">{metrics.default_model}</strong>
              </div>
              <div className="flex justify-between">
                <span>Aspect Ratio & Resolution:</span>
                <strong className="text-gray-200">1080x1920 (9:16 portrait) @ 24fps</strong>
              </div>
              <div className="flex justify-between">
                <span>FFmpeg Post-Production Engine:</span>
                <strong className="text-emerald-400">v8.0.1 (libass + freetype active)</strong>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-xs text-red-400">Failed to load system metrics.</div>
        )}

        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 font-bold text-xs"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
