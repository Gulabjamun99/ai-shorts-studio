import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import CreateProjectForm from './components/CreateProjectForm';
import ScriptApprovalModal from './components/ScriptApprovalModal';
import GenerationTimeline from './components/GenerationTimeline';
import VideoPlayerWithQA from './components/VideoPlayerWithQA';
import PublishModal from './components/PublishModal';
import AdminMetricsModal from './components/AdminMetricsModal';

import {
  createProject,
  approveAndGenerate,
  getGenerationStatus,
  getProject,
  listProjects,
  uploadAsset,
  regenerateSegment
} from './services/api';

export default function App() {
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [scriptApprovalData, setScriptApprovalData] = useState(null);
  const [pendingVersionId, setPendingVersionId] = useState(null);
  const [pendingProjectId, setPendingProjectId] = useState(null);
  
  // Generation state
  const [activeJobId, setActiveJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [jobProgress, setJobProgress] = useState(0);
  const [jobError, setJobError] = useState(null);
  const [generating, setGenerating] = useState(false);
  
  // Modals
  const [showAdminModal, setShowAdminModal] = useState(false);
  const [showPublishModal, setShowPublishModal] = useState(false);

  // Form loading
  const [creatingScript, setCreatingScript] = useState(false);
  const [approvingScript, setApprovingScript] = useState(false);

  // Load existing projects list on mount
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const list = await listProjects();
      setProjects(list);
    } catch (err) {
      console.error(err);
    }
  };

  // Poll active generation job status
  useEffect(() => {
    if (!activeJobId || !generating) return;

    const interval = setInterval(async () => {
      try {
        const res = await getGenerationStatus(activeJobId);
        setJobStatus(res.current_state);
        setJobProgress(res.progress_pct || 0);
        
        if (res.current_state === 'READY') {
          setGenerating(false);
          clearInterval(interval);
          // Reload project details to show final video
          const pId = res.project_id || pendingProjectId;
          if (pId) {
            const updated = await getProject(pId);
            setCurrentProject(updated);
            loadProjects();
          }
        } else if (res.current_state === 'FAILED') {
          setGenerating(false);
          setJobError(res.error_message || 'Video generation failed.');
          clearInterval(interval);
        }
      } catch (e) {
        console.error('Status poll error:', e);
      }
    }, 1200);

    return () => clearInterval(interval);
  }, [activeJobId, generating, pendingProjectId]);

  // Handle Initial Concept Submission -> Generates Master Script
  const handleCreateProject = async (formData) => {
    setCreatingScript(true);
    setJobError(null);
    try {
      const res = await createProject({
        title: formData.title,
        concept: formData.concept,
        platform: formData.platform,
        language: formData.language,
        style: formData.style,
        voice_gender: formData.voice_gender,
        voice_tone: formData.voice_tone,
        cta: formData.cta,
        apiKey: formData.apiKey
      });

      // Upload any assets attached
      if (formData.assets && formData.assets.length > 0) {
        for (const item of formData.assets) {
          const form = new FormData();
          form.append('project_id', res.project_id);
          form.append('asset_type', item.type);
          form.append('file', item.file);
          await uploadAsset(form);
        }
      }

      setPendingProjectId(res.project_id);
      setPendingVersionId(res.version_id);
      setScriptApprovalData(res.script_approval_data);
      loadProjects();
    } catch (err) {
      alert(`Error creating project: ${err.message}`);
    } finally {
      setCreatingScript(false);
    }
  };

  // Handle Script Approval -> Triggers Generation Pipeline
  const handleApproveScript = async ({ masterScript, segments }) => {
    if (!pendingVersionId) return;
    setApprovingScript(true);
    try {
      const res = await approveAndGenerate({
        project_id: pendingProjectId,
        version_id: pendingVersionId,
        edited_script: masterScript,
        edited_segments: segments,
        provider_name: 'mock'
      });

      setScriptApprovalData(null);
      setActiveJobId(res.job_id);
      setGenerating(true);
      setJobProgress(30);
      setJobStatus('APPROVED');
    } catch (err) {
      alert(`Error approving script: ${err.message}`);
    } finally {
      setApprovingScript(false);
    }
  };

  // Handle Partial Scene Re-roll
  const handleRegenerateSegment = async (segIndex) => {
    if (!currentProject?.version?.id) return;
    setGenerating(true);
    setJobProgress(40);
    setJobStatus(`GENERATING_SEGMENT_${segIndex}`);
    try {
      const res = await regenerateSegment({
        project_id: currentProject.project.id,
        version_id: currentProject.version.id,
        segment_index: segIndex,
        provider_name: 'mock'
      });
      setActiveJobId(res.job_id);
    } catch (err) {
      alert(`Error regenerating scene: ${err.message}`);
      setGenerating(false);
    }
  };

  const handleSelectProject = async (pId) => {
    try {
      const data = await getProject(pId);
      setCurrentProject(data);
      setGenerating(false);
      setActiveJobId(null);
    } catch (err) {
      alert('Failed to load project');
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] flex flex-col text-gray-100">
      <Header
        onNewProject={() => {
          setCurrentProject(null);
          setScriptApprovalData(null);
          setGenerating(false);
        }}
        onOpenAdmin={() => setShowAdminModal(true)}
      />

      <main className="flex-1 p-4 sm:p-8 max-w-7xl mx-auto w-full space-y-8">
        
        {/* Project Selector Bar */}
        {projects.length > 0 && !generating && (
          <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-gray-800 text-xs">
            <span className="text-gray-500 font-semibold uppercase tracking-wider shrink-0 mr-2">
              Recent Shorts:
            </span>
            {projects.map((p) => (
              <button
                key={p.id}
                onClick={() => handleSelectProject(p.id)}
                className={`px-3 py-1.5 rounded-lg border shrink-0 transition flex items-center gap-2 ${
                  currentProject?.project?.id === p.id
                    ? 'bg-blue-600/20 border-blue-500 text-blue-300 font-semibold'
                    : 'bg-gray-900 border-gray-800 text-gray-400 hover:text-white'
                }`}
              >
                <span>{p.title}</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-gray-800 text-gray-400 uppercase">
                  {p.language}
                </span>
              </button>
            ))}
          </div>
        )}

        {/* View 1: Video Player & QA Scorecard (if current project is READY) */}
        {currentProject && currentProject.assembly?.final_video_url && !generating ? (
          <VideoPlayerWithQA
            videoUrl={currentProject.assembly.final_video_url}
            subtitlesUrl={currentProject.assembly.subtitles_url}
            qaData={currentProject.qa}
            metadata={{
              title: currentProject.project.title,
              duration_sec: currentProject.assembly.duration_sec,
              language: currentProject.project.language,
              platform: currentProject.project.platform
            }}
            onRegenerateSegment={handleRegenerateSegment}
            onPublish={() => setShowPublishModal(true)}
          />
        ) : generating ? (
          /* View 2: Live Generation Stepper */
          <GenerationTimeline
            currentStatus={jobStatus}
            progress={jobProgress}
            errorMessage={jobError}
          />
        ) : (
          /* View 3: Creation Form */
          <CreateProjectForm
            onSubmit={handleCreateProject}
            loading={creatingScript}
          />
        )}

      </main>

      {/* Script Review & Approval Gate Modal */}
      {scriptApprovalData && (
        <ScriptApprovalModal
          scriptData={scriptApprovalData}
          onApprove={handleApproveScript}
          onRegenerate={() => setScriptApprovalData(null)}
          onClose={() => setScriptApprovalData(null)}
          approving={approvingScript}
        />
      )}

      {/* Social Publishing Modal */}
      {showPublishModal && (
        <PublishModal
          videoMetadata={currentProject?.project}
          videoUrl={currentProject?.assembly?.final_video_url}
          onClose={() => setShowPublishModal(false)}
        />
      )}

      {/* Admin Metrics Modal */}
      {showAdminModal && (
        <AdminMetricsModal
          onClose={() => setShowAdminModal(false)}
        />
      )}

      <footer className="py-6 border-t border-gray-900 text-center text-xs text-gray-500">
        AI Shorts & Reels Creation Studio • 20–23s Vertical One-Story Engine • Powered by Google Veo & FFmpeg
      </footer>
    </div>
  );
}
