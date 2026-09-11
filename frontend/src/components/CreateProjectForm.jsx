import React, { useState } from 'react';
import { Sparkles, Upload, Image as ImageIcon, ChevronDown, ChevronUp, Key, Sliders, AlertCircle, CheckCircle2 } from 'lucide-react';

const LANGUAGES = [
  'English', 'Hindi', 'Marathi', 'Telugu', 'Tamil',
  'Bengali', 'Gujarati', 'Kannada', 'Malayalam', 'Punjabi'
];

const STYLES = [
  'Tutorial', 'Educational', 'Product advertisement', 'Realistic',
  'Cinematic', 'Social media promotional', 'UGC-style', 'Professional corporate', 'Animated'
];

const TONES = [
  'Friendly', 'Professional', 'Energetic', 'Emotional', 'Conversational', 'Promotional'
];

export default function CreateProjectForm({ onSubmit, loading }) {
  const [title, setTitle] = useState('');
  const [concept, setConcept] = useState('');
  const [platform, setPlatform] = useState('Both');
  const [language, setLanguage] = useState('English');
  const [style, setStyle] = useState('Tutorial');
  const [voiceGender, setVoiceGender] = useState('Female');
  const [voiceTone, setVoiceTone] = useState('Friendly');
  const [cta, setCta] = useState('Follow for more daily tips!');
  const [provider, setProvider] = useState('mock');
  const [apiKey, setApiKey] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Asset uploads
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [assetType, setAssetType] = useState('LOGO');

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    const newItems = files.map(file => ({
      file,
      name: file.name,
      type: assetType,
      preview: URL.createObjectURL(file)
    }));
    setUploadedFiles(prev => [...prev, ...newItems]);
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!concept.trim()) return;
    onSubmit({
      title: title.trim() || concept.slice(0, 40) + '...',
      concept: concept.trim(),
      platform,
      language,
      style,
      voice_gender: voiceGender,
      voice_tone: voiceTone,
      cta: cta.trim(),
      provider,
      apiKey: apiKey.trim(),
      assets: uploadedFiles
    });
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 sm:p-8 shadow-xl max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-blue-500" />
          Create a 20-Second Short / Reel
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Enter your topic or product concept. The engine builds a 3-segment narrative and submits it for your script approval.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
            Video Title or Topic
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. 5-Second Microwave Steam Cleaning Trick"
            className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          />
        </div>

        {/* Concept */}
        <div>
          <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
            What video do you want to create? <span className="text-red-400">*</span>
          </label>
          <textarea
            rows={4}
            required
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            placeholder="Describe your tutorial, tip, product ad, or story. Example: Slice a fresh lemon into a bowl of water, microwave for 3 minutes, and wipe away all grease effortlessly with a clean cloth."
            className="w-full bg-gray-900 border border-gray-700 rounded-xl p-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          />
        </div>

        {/* Core Selectors: Language, Style, Platform, Voice */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              {LANGUAGES.map(lang => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">Style</label>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              {STYLES.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">Voice Gender</label>
            <select
              value={voiceGender}
              onChange={(e) => setVoiceGender(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="Female">Female Voice</option>
              <option value="Male">Male Voice</option>
              <option value="Neutral">Neutral Voice</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">Platform</label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="Both">Both (Shorts & Reels)</option>
              <option value="Instagram Reels">Instagram Reels</option>
              <option value="YouTube Shorts">YouTube Shorts</option>
            </select>
          </div>
        </div>

        {/* Optional Asset Uploads */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-gray-300 flex items-center gap-2">
              <ImageIcon className="w-4 h-4 text-indigo-400" />
              Upload Assets (Optional: Brand Logo, Product Photo, Character Ref)
            </span>
            <div className="flex gap-2 text-xs">
              {['LOGO', 'PRODUCT', 'CHARACTER_REF'].map(t => (
                <button
                  type="button"
                  key={t}
                  onClick={() => setAssetType(t)}
                  className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                    assetType === t ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'
                  }`}
                >
                  {t.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <label className="border-2 border-dashed border-gray-700 hover:border-indigo-500 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer transition bg-gray-950/40">
            <Upload className="w-5 h-5 text-gray-400 mb-1" />
            <span className="text-xs text-gray-300">Click to upload as <strong>{assetType}</strong> (PNG, JPG, WEBP)</span>
            <span className="text-[10px] text-gray-500">Max size 25MB • Up to 3 reference images</span>
            <input
              type="file"
              accept="image/png, image/jpeg, image/webp"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>

          {uploadedFiles.length > 0 && (
            <div className="flex flex-wrap gap-3 mt-3">
              {uploadedFiles.map((item, idx) => (
                <div key={idx} className="relative group bg-gray-800 rounded-lg p-1.5 border border-gray-700 flex items-center gap-2 text-xs">
                  <img src={item.preview} alt={item.name} className="w-8 h-8 rounded object-cover" />
                  <div className="pr-4">
                    <p className="text-white text-[11px] font-medium truncate max-w-[120px]">{item.name}</p>
                    <span className="text-[9px] text-indigo-400 uppercase font-bold">{item.type}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFile(idx)}
                    className="absolute right-1 top-1 text-gray-400 hover:text-red-400 text-xs px-1"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Advanced Options Accordion */}
        <div className="border border-gray-800 rounded-xl overflow-hidden bg-gray-900/40">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full px-4 py-3 flex items-center justify-between text-xs font-semibold text-gray-400 hover:text-gray-200 transition"
          >
            <span className="flex items-center gap-2">
              <Sliders className="w-4 h-4" />
              Advanced Options (CTA, Video Engine Provider, Gemini API Key)
            </span>
            {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showAdvanced && (
            <div className="p-4 border-t border-gray-800 space-y-4 text-xs">
              <div>
                <label className="block text-gray-300 mb-1 font-medium">Custom Call to Action (CTA)</label>
                <input
                  type="text"
                  value={cta}
                  onChange={(e) => setCta(e.target.value)}
                  placeholder="e.g. Subscribe for more daily home tips!"
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-300 mb-1 font-medium">Video Engine Provider</label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white"
                  >
                    <option value="mock">Local Deterministic Provider (Free / Dev / Testing)</option>
                    <option value="veo">Google Veo 3.1 (Official Gemini API Key)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-300 mb-1 font-medium flex items-center gap-1.5">
                    <Key className="w-3.5 h-3.5 text-yellow-400" />
                    Gemini API Key (Optional for live Veo)
                  </label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="AIzaSy..."
                    className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white"
                  />
                  <p className="text-[10px] text-gray-500 mt-1">
                    Keys are processed server-side only. Zero password or session cookie scraping.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !concept.trim()}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              <span>Analyzing Concept & Crafting Master Script...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              <span>Generate Master Script (Free Approval Gate)</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
