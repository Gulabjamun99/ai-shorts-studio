import asyncio
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from sqlalchemy.future import select

from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.schema import (
    DBProject, DBProjectVersion, DBContentTruth, DBScript, DBMasterBlueprint,
    DBVideoSegment, DBVideoAssembly, DBQAResult, DBGenerationJob,
    JobStatus, SegmentApprovalItem, ScriptApprovalData, QAScorecard
)
from backend.app.engines.concept_engine import ConceptEngine
from backend.app.engines.script_engine import ScriptEngine
from backend.app.engines.blueprint_engine import BlueprintEngine
from backend.app.providers.factory import ProviderFactory
from backend.app.providers.voice_provider import VoiceProvider
from backend.app.video.ffmpeg_assembler import FFmpegAssembler
from backend.app.engines.qa_engine import VideoQAEngine

# Active WebSocket subscriber callbacks keyed by job_id
_job_listeners: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

def register_listener(job_id: str, callback: Callable[[Dict[str, Any]], None]):
    if job_id not in _job_listeners:
        _job_listeners[job_id] = []
    _job_listeners[job_id].append(callback)

def notify_listeners(job_id: str, payload: Dict[str, Any]):
    listeners = _job_listeners.get(job_id, [])
    for cb in listeners:
        try:
            cb(payload)
        except Exception:
            pass


class JobOrchestrator:
    """
    Coordinates the entire end-to-end video creation lifecycle:
    Concept -> Script -> Approval Gate -> Segment Generation -> Audio Sync -> Assembly -> QA -> Ready
    """

    @classmethod
    async def create_project_and_script(
        cls,
        title: str,
        concept: str,
        platform: str = "Both",
        language: str = "English",
        style: str = "Tutorial",
        voice_gender: str = "Female",
        voice_tone: str = "Friendly",
        target_duration: float = 22.0,
        aspect_ratio: str = "9:16",
        cta: str = "Follow for more daily tips!"
    ) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            project_id = str(uuid.uuid4())
            version_id = str(uuid.uuid4())
            job_id = str(uuid.uuid4())

            # 1. Create DBProject
            project = DBProject(
                id=project_id,
                title=title,
                platform=platform,
                language=language,
                style=style,
                voice_gender=voice_gender,
                voice_tone=voice_tone,
                aspect_ratio=aspect_ratio,
                target_duration=target_duration
            )
            session.add(project)

            # 2. Create DBProjectVersion
            version = DBProjectVersion(
                id=version_id,
                project_id=project_id,
                version_number=1,
                raw_concept=concept,
                status=JobStatus.ANALYZING.value
            )
            session.add(version)

            # 3. Create GenerationJob
            job = DBGenerationJob(
                id=job_id,
                project_id=project_id,
                version_id=version_id,
                current_state=JobStatus.ANALYZING.value,
                progress_pct=10
            )
            session.add(job)
            await session.commit()

            # 4. Extract Content Truth Layer
            truth_layer = ConceptEngine.analyze(
                concept=concept,
                title=title,
                user_cta=cta,
                language=language,
                platform=platform,
                style=style
            )
            db_truth = DBContentTruth(
                id=str(uuid.uuid4()),
                version_id=version_id,
                main_subject=truth_layer.main_subject,
                main_objective=truth_layer.main_objective,
                audience=truth_layer.audience,
                required_visuals=json.dumps(truth_layer.required_visuals),
                required_actions=json.dumps(truth_layer.required_actions),
                required_cta=truth_layer.required_cta,
                verified_facts=json.dumps(truth_layer.verified_facts),
                forbidden_claims=json.dumps(truth_layer.forbidden_claims)
            )
            session.add(db_truth)

            # 5. Generate Master Script & 3 Segments
            script_data = ScriptEngine.generate_script(
                concept=concept,
                truth_layer=truth_layer,
                language=language,
                style=style,
                target_duration=target_duration
            )

            db_script = DBScript(
                id=str(uuid.uuid4()),
                version_id=version_id,
                master_script=script_data["master_script"],
                language=language,
                estimated_duration=script_data["estimated_duration"],
                speech_rate_wpm=135.0,
                is_approved=False
            )
            session.add(db_script)

            # Store segments in DB
            for seg in script_data["segments"]:
                db_seg = DBVideoSegment(
                    id=str(uuid.uuid4()),
                    version_id=version_id,
                    segment_index=seg.segment_index,
                    duration_sec=seg.duration_sec,
                    narration=seg.narration,
                    on_screen_text=seg.on_screen_text,
                    visual_prompt=seg.visual_description,
                    status="WAITING_FOR_APPROVAL"
                )
                session.add(db_seg)

            # Update job state to WAITING_FOR_APPROVAL
            job.current_state = JobStatus.WAITING_FOR_APPROVAL.value
            job.progress_pct = 25
            version.status = JobStatus.WAITING_FOR_APPROVAL.value
            await session.commit()

            return {
                "project_id": project_id,
                "version_id": version_id,
                "job_id": job_id,
                "status": JobStatus.WAITING_FOR_APPROVAL.value,
                "script_approval_data": script_data
            }

    @classmethod
    async def approve_and_generate_video(
        cls,
        version_id: str,
        edited_script: Optional[str] = None,
        edited_segments: Optional[List[SegmentApprovalItem]] = None,
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> str:
        """Kicks off background video generation after user script approval."""
        async with AsyncSessionLocal() as session:
            q_job = await session.execute(select(DBGenerationJob).where(DBGenerationJob.version_id == version_id))
            job = q_job.scalars().first()
            if not job:
                raise ValueError("Generation job not found for version.")
            
            job.current_state = JobStatus.APPROVED.value
            job.progress_pct = 30
            await session.commit()
            job_id = job.id

        # Launch full generation pipeline asynchronously in background
        asyncio.create_task(
            cls._execute_generation_pipeline(
                job_id=job_id,
                version_id=version_id,
                edited_script=edited_script,
                edited_segments=edited_segments,
                provider_name=provider_name,
                api_key=api_key
            )
        )
        return job_id

    @classmethod
    async def _execute_generation_pipeline(
        cls,
        job_id: str,
        version_id: str,
        edited_script: Optional[str] = None,
        edited_segments: Optional[List[SegmentApprovalItem]] = None,
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        try:
            async with AsyncSessionLocal() as session:
                # Load Project, Version, Script, ContentTruth
                q_ver = await session.execute(select(DBProjectVersion).where(DBProjectVersion.id == version_id))
                version = q_ver.scalars().first()
                project = await session.get(DBProject, version.project_id)
                q_truth = await session.execute(select(DBContentTruth).where(DBContentTruth.version_id == version_id))
                db_truth = q_truth.scalars().first()
                q_script = await session.execute(select(DBScript).where(DBScript.version_id == version_id))
                db_script = q_script.scalars().first()
                job = await session.get(DBGenerationJob, job_id)

                # Update status
                job.current_state = JobStatus.GENERATING_REFERENCE.value
                job.progress_pct = 35
                notify_listeners(job_id, {"status": job.current_state, "progress": job.progress_pct})
                await session.commit()

                # Reconstruct TruthLayer
                truth_layer = ConceptEngine.analyze(
                    concept=version.raw_concept,
                    title=project.title,
                    user_cta=db_truth.required_cta,
                    language=project.language,
                    platform=project.platform,
                    style=project.style
                )

                # Reconstruct segments from DB or edited list
                q_segs = await session.execute(
                    select(DBVideoSegment).where(DBVideoSegment.version_id == version_id).order_by(DBVideoSegment.segment_index)
                )
                db_segments = q_segs.scalars().all()
                segments = [
                    SegmentApprovalItem(
                        segment_index=s.segment_index,
                        duration_sec=s.duration_sec,
                        narration=s.narration,
                        visual_description=s.visual_prompt,
                        on_screen_text=s.on_screen_text
                    )
                    for s in db_segments
                ]

                # Step 1: Create Master Video Blueprint
                blueprint = BlueprintEngine.create_blueprint(
                    truth_layer=truth_layer,
                    segments=segments,
                    style=project.style,
                    aspect_ratio=project.aspect_ratio
                )
                db_bp = DBMasterBlueprint(
                    id=str(uuid.uuid4()),
                    version_id=version_id,
                    character_id=blueprint.character_id,
                    character_desc=blueprint.character_desc,
                    product_id=blueprint.product_id,
                    product_desc=blueprint.product_desc,
                    environment_desc=blueprint.environment_desc,
                    camera_plan=blueprint.camera_plan,
                    lighting_plan=blueprint.lighting_plan
                )
                session.add(db_bp)
                await session.commit()

                # Step 2: Initialize Video Provider
                video_provider = ProviderFactory.get_video_provider(provider_name, api_key)
                
                # Step 3: Generate Segments 1, 2, 3 with Frame Continuity
                generated_results = []
                transition_frames = []
                previous_last_frame = None

                for i, seg_prompt_info in enumerate(blueprint.segment_prompts):
                    idx = seg_prompt_info["segment_index"]
                    state_enum = getattr(JobStatus, f"GENERATING_SEGMENT_{idx}")
                    job.current_state = state_enum.value
                    job.progress_pct = 40 + (idx * 12)
                    notify_listeners(job_id, {"status": job.current_state, "progress": job.progress_pct})
                    await session.commit()

                    res = await video_provider.generate_segment(
                        prompt=seg_prompt_info["prompt"],
                        duration_sec=seg_prompt_info["duration_sec"],
                        aspect_ratio=project.aspect_ratio,
                        resolution="1080p",
                        first_frame_path=previous_last_frame,
                        negative_prompt=seg_prompt_info["negative_prompt"]
                    )
                    generated_results.append(res)

                    # Track transition frames for QA
                    if previous_last_frame and res.first_frame_path:
                        transition_frames.append((previous_last_frame, res.first_frame_path))

                    previous_last_frame = res.last_frame_path

                    # Update segment record
                    for db_s in db_segments:
                        if db_s.segment_index == idx:
                            db_s.raw_video_path = str(res.video_path)
                            db_s.first_frame_path = str(res.first_frame_path) if res.first_frame_path else ""
                            db_s.last_frame_path = str(res.last_frame_path) if res.last_frame_path else ""
                            db_s.status = "COMPLETED"
                    await session.commit()

                # Step 4: Generate Neural Master Voice & Synchronized Subtitles
                job.current_state = JobStatus.VOICE_GENERATING.value
                job.progress_pct = 78
                notify_listeners(job_id, {"status": job.current_state, "progress": job.progress_pct})
                await session.commit()

                voice_res = await VoiceProvider.generate_speech(
                    text=db_script.master_script,
                    language=project.language,
                    gender=project.voice_gender,
                    segment_durations=[r.duration_sec for r in generated_results]
                )

                # Step 5: Video Assembly
                job.current_state = JobStatus.ASSEMBLING.value
                job.progress_pct = 85
                notify_listeners(job_id, {"status": job.current_state, "progress": job.progress_pct})
                await session.commit()

                final_video_path = await FFmpegAssembler.assemble_final_video(
                    segment_paths=[r.video_path for r in generated_results],
                    audio_path=voice_res.audio_path,
                    subtitles_path=voice_res.srt_subtitles_path
                )

                video_meta = await FFmpegAssembler.get_video_metadata(final_video_path)

                # Step 6: Automated Video QA
                job.current_state = JobStatus.QA.value
                job.progress_pct = 92
                notify_listeners(job_id, {"status": job.current_state, "progress": job.progress_pct})
                await session.commit()

                qa_scorecard = VideoQAEngine.run_qa(
                    final_video_meta=video_meta,
                    segments=segments,
                    blueprint_data=blueprint.to_dict(),
                    voice_result_meta={"language": project.language, "voice_id": voice_res.voice_id},
                    transition_frames=transition_frames,
                    target_duration=project.target_duration
                )

                # Store QA Result
                db_qa = DBQAResult(
                    id=str(uuid.uuid4()),
                    version_id=version_id,
                    overall_score=qa_scorecard.overall_score,
                    passed=qa_scorecard.passed,
                    category_scores=json.dumps(qa_scorecard.categories),
                    failure_reasons=json.dumps(qa_scorecard.failure_reasons),
                    repair_attempts=0
                )
                session.add(db_qa)

                # Store Assembly
                db_assembly = DBVideoAssembly(
                    id=str(uuid.uuid4()),
                    version_id=version_id,
                    final_video_path=str(final_video_path),
                    subtitles_path=str(voice_res.srt_subtitles_path),
                    audio_track_path=str(voice_res.audio_path),
                    resolution=f"{video_meta.get('width', 1080)}x{video_meta.get('height', 1920)}",
                    aspect_ratio=project.aspect_ratio,
                    duration_sec=video_meta.get("duration", 22.0),
                    status="READY" if qa_scorecard.passed else "FLAGGED"
                )
                session.add(db_assembly)

                # Finalize Job
                job.current_state = JobStatus.READY.value
                job.progress_pct = 100
                version.status = JobStatus.READY.value
                await session.commit()

                notify_listeners(job_id, {
                    "status": job.current_state,
                    "progress": 100,
                    "video_path": str(final_video_path),
                    "qa_score": qa_scorecard.overall_score
                })

        except Exception as e:
            async with AsyncSessionLocal() as session:
                job = await session.get(DBGenerationJob, job_id)
                if job:
                    job.current_state = JobStatus.FAILED.value
                    job.error_message = str(e)
                    await session.commit()
                notify_listeners(job_id, {"status": JobStatus.FAILED.value, "error": str(e)})
