import React, { useState, useEffect } from 'react';
import {
  Sparkles, Upload, Image as ImageIcon, ChevronDown, ChevronUp,
  Key, Sliders, AlertCircle, CheckCircle2, Smartphone, Globe, Bell, Edit3, Trash2, Video, Clock
} from 'lucide-react';

const LANGUAGES = [
  'English', 'Hindi', 'Marathi', 'Telugu', 'Tamil',
  'Bengali', 'Gujarati', 'Kannada', 'Malayalam', 'Punjabi'
];

const STYLES = [
  'Tutorial', 'Educational', 'Product advertisement', 'Realistic',
  'Cinematic', 'Social media promotional', 'UGC-style', 'Professional corporate', 'Animated'
];

export default function CreateProjectForm({ onSubmit, loading }) {
  const [title, setTitle] = useState('');
  const [concept, setConcept] = useState('');
  const [platform, setPlatform] = useState('Both');
  const [language, setLanguage] = useState('Hindi');
  const [style, setStyle] = useState('Tutorial');
  const [voiceGender, setVoiceGender] = useState('Female');
  const [voiceTone, setVoiceTone] = useState('Friendly');
  const [provider, setProvider] = useState('mock');
  const [targetDuration, setTargetDuration] = useState(48.0);
  
  // Persistent Gemini API Key
  const [apiKey, setApiKey] = useState('');
  const [keySaved, setKeySaved] = useState(false);

  // CTA Builder State
  const [ctaType, setCtaType] = useState('app'); // 'app' | 'website' | 'subscribe' | 'custom'
  const [appName, setAppName] = useState('GharMantra');
  const [appStore, setAppStore] = useState('Google Play Store');
  const [appLink, setAppLink] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('www.gharmantra.com');
  const [customCta, setCustomCta] = useState('');

  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Asset uploads
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [assetType, setAssetType] = useState('LOGO');

  // Load saved API Key from localStorage on mount
  useEffect(() => {
    try {
      const savedKey = localStorage.getItem('ai_shorts_studio_gemini_key');
      if (savedKey) {
        setApiKey(savedKey);
        setKeySaved(true);
      }
    } catch (e) {}
  }, []);

  const handleApiKeyChange = (val) => {
    setApiKey(val);
    try {
      if (val.trim()) {
        localStorage.setItem('ai_shorts_studio_gemini_key', val.trim());
        setKeySaved(true);
      } else {
        localStorage.removeItem('ai_shorts_studio_gemini_key');
        setKeySaved(false);
      }
    } catch (e) {}
  };

  const handleClearApiKey = () => {
    setApiKey('');
    setKeySaved(false);
    try {
      localStorage.removeItem('ai_shorts_studio_gemini_key');
    } catch (e) {}
  };

  // Compute final formatted CTA
  const getComputedCta = () => {
    if (ctaType === 'app') {
      const linkPart = appLink.trim() ? ` (Link: ${appLink.trim()})` : '';
      if (language === 'Hindi') {
        return `और अधिक जानकारी के लिए, ${appStore} से ${appName} ऐप डाउनलोड करें${linkPart}!`;
      } else if (language === 'Marathi') {
        return `अधिक माहितीसाठी, ${appStore} वरून ${appName} ॲप आजच डाउनलोड करा${linkPart}!`;
      } else {
        return `For more details, download the ${appName} app from ${appStore}${linkPart}!`;
      }
    } else if (ctaType === 'website') {
      const site = websiteUrl.trim() || 'our website';
      if (language === 'Hindi') {
        return `पूरी जानकारी और डिटेल्स के लिए हमारी वेबसाइट ${site} पर विजिट करें!`;
      } else if (language === 'Marathi') {
        return `अधिक तपशिलांसाठी आमच्या वेबसाइट ${site} ला भेट द्या!`;
      } else {
        return `For complete details and guides, visit our website at ${site}!`;
      }
    } else if (ctaType === 'subscribe') {
      if (language === 'Hindi') {
        return `ऐसे ही काम के और उपयोगी टिप्स के लिए अभी फॉलो और सब्सक्राइब करें!`;
      } else if (language === 'Marathi') {
        return `अशाच उपयुक्त टिप्ससाठी आताच फॉलो आणि सबस्क्राईब करा!`;
      } else {
        return `Follow and subscribe for more daily smart tips!`;
      }
    } else {
      return customCta.trim() || 'Follow for more daily tips!';
    }
  };

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

    const finalCta = getComputedCta();

    onSubmit({
      title: title.trim() || concept.slice(0, 40) + '...',
      concept: concept.trim(),
      platform,
      language,
      style,
      voice_gender: voiceGender,
      voice_tone: voiceTone,
      cta: finalCta,
      provider,
      target_duration: targetDuration,
      apiKey: apiKey.trim(),
      assets: uploadedFiles
    });
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-2xl p-6 sm:p-8 shadow-xl max-w-4xl mx-auto">
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800/80 pb-5">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-blue-500" />
            Create AI Short / Reel (Up to 50s)
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Google Vids Style Engine: Real HD action video clips + studio Hindi voiceover.
          </p>
        </div>

        {/* Saved API Key Quick Status Badge */}
        <div className="flex items-center gap-2 bg-gray-900/90 border border-gray-700/60 rounded-xl px-3 py-2 text-xs">
          <Key className="w-4 h-4 text-amber-400 shrink-0" />
          <div className="flex flex-col">
            <span className="text-[10px] uppercase font-bold text-gray-400">Gemini AI Key:</span>
            {keySaved ? (
              <span className="text-emerald-400 font-medium flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 inline" /> Key Saved in Browser
              </span>
            ) : (
              <span className="text-gray-400 text-[11px]">Free Local NLP Mode</span>
            )}
          </div>
        </div>
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
            placeholder="e.g. 5-Second Kitchen Cleaning Trick ya GharMantra App Feature"
            className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          />
        </div>

        {/* Concept */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider">
              What video do you want to create? (Topic, Steps, Recipe) <span className="text-red-400">*</span>
            </label>
            <span className="text-[11px] text-gray-400">100% Concept-Matched Script</span>
          </div>
          <textarea
            rows={5}
            required
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            placeholder="Aap jo bhi concept ya tutorial banana chahte hain yahan likhein. Agar steps (1, 2, 3...) ya ingredients hain toh unhe bhi likhein — script me wahi exact steps shamil honge!"
            className="w-full bg-gray-900 border border-gray-700 rounded-xl p-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition leading-relaxed"
          />
        </div>

        {/* Call to Action (CTA) Studio */}
        <div className="bg-gray-900/80 border border-blue-500/30 rounded-2xl p-4 sm:p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-blue-300 uppercase tracking-wider flex items-center gap-1.5">
              <Smartphone className="w-4 h-4 text-blue-400" />
              Call to Action (CTA) Setup
            </span>
            <span className="text-[11px] text-gray-400">Video ke aakhiri scene me yahi dikhega aur bola jayega</span>
          </div>

          {/* CTA Type Tabs */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
            <button
              type="button"
              onClick={() => setCtaType('app')}
              className={`px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 border transition ${
                ctaType === 'app'
                  ? 'bg-blue-600 border-blue-400 text-white shadow-md shadow-blue-600/30'
                  : 'bg-gray-800/80 border-gray-700 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              App Download
            </button>

            <button
              type="button"
              onClick={() => setCtaType('website')}
              className={`px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 border transition ${
                ctaType === 'website'
                  ? 'bg-blue-600 border-blue-400 text-white shadow-md shadow-blue-600/30'
                  : 'bg-gray-800/80 border-gray-700 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Globe className="w-3.5 h-3.5" />
              Visit Website
            </button>

            <button
              type="button"
              onClick={() => setCtaType('subscribe')}
              className={`px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 border transition ${
                ctaType === 'subscribe'
                  ? 'bg-blue-600 border-blue-400 text-white shadow-md shadow-blue-600/30'
                  : 'bg-gray-800/80 border-gray-700 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Bell className="w-3.5 h-3.5" />
              Follow / Subscribe
            </button>

            <button
              type="button"
              onClick={() => setCtaType('custom')}
              className={`px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 border transition ${
                ctaType === 'custom'
                  ? 'bg-blue-600 border-blue-400 text-white shadow-md shadow-blue-600/30'
                  : 'bg-gray-800/80 border-gray-700 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Edit3 className="w-3.5 h-3.5" />
              Custom Text
            </button>
          </div>

          {/* Conditional CTA Inputs */}
          {ctaType === 'app' && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] text-gray-300 font-medium mb-1">App Name</label>
                <input
                  type="text"
                  value={appName}
                  onChange={(e) => setAppName(e.target.value)}
                  placeholder="GharMantra"
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] text-gray-300 font-medium mb-1">Store Name</label>
                <select
                  value={appStore}
                  onChange={(e) => setAppStore(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white"
                >
                  <option value="Google Play Store">Google Play Store</option>
                  <option value="Apple App Store">Apple App Store</option>
                  <option value="Play Store & App Store">Both Stores</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] text-gray-300 font-medium mb-1">App Store Link (Optional)</label>
                <input
                  type="text"
                  value={appLink}
                  onChange={(e) => setAppLink(e.target.value)}
                  placeholder="https://play.google.com/store/apps/..."
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white"
                />
              </div>
            </div>
          )}

          {ctaType === 'website' && (
            <div>
              <label className="block text-[11px] text-gray-300 font-medium mb-1">Website URL or Domain</label>
              <input
                type="text"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="e.g. www.gharmantra.com ya link in bio"
                className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white"
              />
            </div>
          )}

          {ctaType === 'custom' && (
            <div>
              <label className="block text-[11px] text-gray-300 font-medium mb-1">Custom CTA Message</label>
              <input
                type="text"
                value={customCta}
                onChange={(e) => setCustomCta(e.target.value)}
                placeholder="Aap jo bhi Call to Action bolna chahte hain yahan type karein"
                className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white"
              />
            </div>
          )}

          {/* Live Preview Box */}
          <div className="mt-3 bg-gray-950/80 border border-gray-800 rounded-lg px-3 py-2 flex items-center gap-2">
            <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider shrink-0">Live CTA Preview:</span>
            <span className="text-xs text-gray-200 italic truncate">"{getComputedCta()}"</span>
          </div>
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

        {/* Video Engine Mode Selector */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-300 flex items-center gap-2">
              <Video className="w-4 h-4 text-emerald-400" />
              AI Video Generation Engine
            </span>
            <span className="text-[10px] text-gray-400">Choose Video Mode</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
            <button
              type="button"
              onClick={() => setProvider('mock')}
              className={`p-3 rounded-xl border text-left transition flex items-start gap-3 ${
                provider === 'mock'
                  ? 'bg-blue-600/15 border-blue-500 shadow-md text-white'
                  : 'bg-gray-950/60 border-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              <Sparkles className={`w-5 h-5 mt-0.5 shrink-0 ${provider === 'mock' ? 'text-blue-400' : 'text-gray-500'}`} />
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-white">Instant Studio Mode</span>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Free & Fast</span>
                </div>
                <p className="text-[11px] text-gray-400 mt-1">
                  Realistic vertical 9:16 video with HeyGen AI Presenter & synchronized voiceover. Instant render.
                </p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setProvider('veo')}
              className={`p-3 rounded-xl border text-left transition flex items-start gap-3 ${
                provider === 'veo'
                  ? 'bg-purple-600/15 border-purple-500 shadow-md text-white'
                  : 'bg-gray-950/60 border-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              <Video className={`w-5 h-5 mt-0.5 shrink-0 ${provider === 'veo' ? 'text-purple-400' : 'text-gray-500'}`} />
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-white">Google Veo 3.1 Mode</span>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">Photorealistic AI</span>
                </div>
                <p className="text-[11px] text-gray-400 mt-1">
                  Uses Google's official Veo video model with your Gemini API key for deep AI frame synthesis.
                </p>
              </div>
            </button>
          </div>
        </div>

        {/* Target Video Duration Selector (Up to 50s) */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-300 flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              Target Reel Duration
            </span>
            <span className="text-[10px] text-cyan-400 font-bold">Google Vids Style: 45–50s Recommended</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-2">
            <button
              type="button"
              onClick={() => setTargetDuration(48.0)}
              className={`p-3 rounded-xl border text-left transition flex items-center justify-between ${
                targetDuration >= 40
                  ? 'bg-cyan-600/15 border-cyan-500 text-white shadow-md'
                  : 'bg-gray-950/60 border-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              <div>
                <span className="text-xs font-bold block text-white">45–50 Seconds</span>
                <span className="text-[10px] text-gray-400">In-Depth Action (Recommended)</span>
              </div>
              <span className="text-[10px] bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 px-1.5 py-0.5 rounded font-bold">50s</span>
            </button>

            <button
              type="button"
              onClick={() => setTargetDuration(32.0)}
              className={`p-3 rounded-xl border text-left transition flex items-center justify-between ${
                targetDuration >= 28 && targetDuration < 40
                  ? 'bg-blue-600/15 border-blue-500 text-white shadow-md'
                  : 'bg-gray-950/60 border-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              <div>
                <span className="text-xs font-bold block text-white">30–35 Seconds</span>
                <span className="text-[10px] text-gray-400">Standard Short / Reel</span>
              </div>
              <span className="text-[10px] bg-blue-500/20 text-blue-300 border border-blue-500/30 px-1.5 py-0.5 rounded font-bold">30s</span>
            </button>

            <button
              type="button"
              onClick={() => setTargetDuration(22.0)}
              className={`p-3 rounded-xl border text-left transition flex items-center justify-between ${
                targetDuration < 28
                  ? 'bg-purple-600/15 border-purple-500 text-white shadow-md'
                  : 'bg-gray-950/60 border-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              <div>
                <span className="text-xs font-bold block text-white">20–25 Seconds</span>
                <span className="text-[10px] text-gray-400">Quick Hack</span>
              </div>
              <span className="text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-1.5 py-0.5 rounded font-bold">20s</span>
            </button>
          </div>
        </div>

        {/* Gemini API Key Management (Persistent) */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-300 flex items-center gap-2">
              <Key className="w-4 h-4 text-amber-400" />
              Google Gemini API Key (Saved Automatically in Browser)
            </span>
            {keySaved && (
              <button
                type="button"
                onClick={handleClearApiKey}
                className="text-[11px] text-red-400 hover:text-red-300 flex items-center gap-1"
                title="Remove API Key from this browser"
              >
                <Trash2 className="w-3 h-3" /> Clear Saved Key
              </button>
            )}
          </div>
          <div className="flex gap-2">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => handleApiKeyChange(e.target.value)}
              placeholder="AIzaSy... (Aapki key browser me safe save rahegi, baar baar nahi daalna padega)"
              className="flex-1 bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <p className="text-[10px] text-gray-500 mt-1.5">
            {keySaved ? (
              <span className="text-emerald-400">✓ Key browser me save ho chuki hai. Har baar naye video me auto-use hogi!</span>
            ) : (
              <span>Agar key nahi hai toh bhi koi baat nahi, Smart Free NLP Engine se video generate ho jayega!</span>
            )}
          </p>
        </div>

        {/* Optional Asset Uploads */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-gray-300 flex items-center gap-2">
              <ImageIcon className="w-4 h-4 text-indigo-400" />
              Upload Assets (Optional: Logo, Product Photo, Brand Badge)
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

