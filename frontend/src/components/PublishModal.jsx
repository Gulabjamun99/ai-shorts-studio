import React, { useState } from 'react';
import { Share2, CheckCircle2, Download, AlertCircle, X, Video } from 'lucide-react';
import { publishVideo } from '../services/api';

const YoutubeIcon = () => (
  <svg className="w-4 h-4 text-red-500 fill-current" viewBox="0 0 24 24">
    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
  </svg>
);

const InstagramIcon = () => (
  <svg className="w-4 h-4 text-pink-500 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
    <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
    <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
  </svg>
);

export default function PublishModal({ videoMetadata, videoUrl, onClose }) {
  const [platform, setPlatform] = useState('youtube');
  const [title, setTitle] = useState(videoMetadata?.title || 'Amazing 20-Second Life Hack');
  const [description, setDescription] = useState('Learn this incredible 20-second hack today!');
  const [tags, setTags] = useState('shorts, reels, lifehack, viral, tutorial');
  const [publishing, setPublishing] = useState(false);
  const [result, setResult] = useState(null);

  const handlePublish = async (e) => {
    e.preventDefault();
    setPublishing(true);
    try {
      const res = await publishVideo({
        platform,
        title,
        description,
        tags: tags.split(',').map(t => t.trim()).filter(Boolean)
      });
      setResult(res);
    } catch (err) {
      setResult({ status: 'ERROR', message: err.message });
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#111827] border border-gray-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95">
        
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Share2 className="w-5 h-5 text-purple-400" />
            Publish to Shorts / Reels
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {result ? (
          <div className="space-y-4 py-4 text-center">
            <div className="w-12 h-12 rounded-full bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h4 className="text-white font-bold text-sm">{result.status === 'PUBLISHED' ? 'Published!' : 'Ready for Upload'}</h4>
            <p className="text-xs text-gray-400 max-w-md mx-auto">{result.message}</p>

            {result.suggested_title && (
              <div className="text-left bg-gray-900 border border-gray-800 rounded-xl p-3 text-xs space-y-2">
                <div>
                  <span className="text-gray-500 font-semibold block">Suggested Title:</span>
                  <span className="text-gray-200">{result.suggested_title}</span>
                </div>
                <div>
                  <span className="text-gray-500 font-semibold block">Suggested Caption & Hashtags:</span>
                  <span className="text-gray-200">{result.suggested_description}</span>
                </div>
              </div>
            )}

            <div className="pt-2 flex justify-center gap-3">
              <a
                href={videoUrl}
                download="short_for_upload.mp4"
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs"
              >
                <Download className="w-4 h-4" />
                Download Ready MP4
              </a>
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 font-bold text-xs"
              >
                Close
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handlePublish} className="space-y-4 text-xs">
            {/* Platform Selector */}
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setPlatform('youtube')}
                className={`flex items-center justify-center gap-2 py-2.5 rounded-xl border font-semibold transition ${
                  platform === 'youtube'
                    ? 'bg-red-600/10 border-red-500 text-red-400'
                    : 'bg-gray-900 border-gray-800 text-gray-400'
                }`}
              >
                <YoutubeIcon />
                YouTube Shorts
              </button>

              <button
                type="button"
                onClick={() => setPlatform('instagram')}
                className={`flex items-center justify-center gap-2 py-2.5 rounded-xl border font-semibold transition ${
                  platform === 'instagram'
                    ? 'bg-pink-600/10 border-pink-500 text-pink-400'
                    : 'bg-gray-900 border-gray-800 text-gray-400'
                }`}
              >
                <InstagramIcon />
                Instagram Reels
              </button>
            </div>

            <div>
              <label className="block text-gray-400 mb-1 font-medium">Video Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white"
              />
            </div>

            <div>
              <label className="block text-gray-400 mb-1 font-medium">Description / Caption</label>
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white"
              />
            </div>

            <div>
              <label className="block text-gray-400 mb-1 font-medium">Hashtags (comma separated)</label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white"
              />
            </div>

            <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-3 text-[11px] text-gray-400 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" />
              <span>
                Uploads are handled exclusively via official platform APIs. If OAuth credentials are not connected, the app provides your optimized MP4 with copy-paste captions for one-click manual posting.
              </span>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={publishing}
                className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold transition disabled:opacity-50"
              >
                {publishing ? 'Publishing...' : 'Publish Video'}
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  );
}
