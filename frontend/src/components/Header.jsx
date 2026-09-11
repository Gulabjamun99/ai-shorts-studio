import React from 'react';
import { Film, Activity, Sparkles, Video, Settings2, PlusCircle } from 'lucide-react';

export default function Header({ onNewProject, onOpenAdmin, activeProvider = 'mock' }) {
  return (
    <header className="bg-[#111827] border-b border-gray-800 sticky top-0 z-40 px-6 py-4 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-3 cursor-pointer" onClick={onNewProject}>
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-md shadow-blue-500/20">
          <Film className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent">
              AI Shorts & Reels Studio
            </h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Veo 3.1 Ready
            </span>
          </div>
          <p className="text-xs text-gray-400">20-23s Vertical One-Story Video Engine</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800/80 border border-gray-700 text-xs text-gray-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Provider: <strong className="text-white uppercase">{activeProvider}</strong></span>
        </div>

        <button
          onClick={onOpenAdmin}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-medium border border-gray-700 transition"
          title="System Metrics & Observability"
        >
          <Activity className="w-4 h-4 text-emerald-400" />
          <span className="hidden md:inline">Observability</span>
        </button>

        <button
          onClick={onNewProject}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/30 transition"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Short</span>
        </button>
      </div>
    </header>
  );
}
