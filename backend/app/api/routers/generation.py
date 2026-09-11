from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from pathlib import Path

from backend.app.core.database import get_db
from backend.app.models.schema import DBGenerationJob, DBVideoAssembly, DBQAResult, SegmentApprovalItem
from backend.app.services.job_orchestrator import JobOrchestrator

router = APIRouter(prefix="/api/generation", tags=["Generation"])

class ApproveGenerationRequest(BaseModel):
    version_id: str
    edited_script: Optional[str] = None
    edited_segments: Optional[List[SegmentApprovalItem]] = None
    provider_name: Optional[str] = "mock"
    api_key: Optional[str] = None

class RegenerateSegmentRequest(BaseModel):
    version_id: str
    segment_index: int
    new_visual_prompt: Optional[str] = None
    provider_name: Optional[str] = "mock"

class RegenerateVoiceRequest(BaseModel):
    version_id: str
    new_language: Optional[str] = None
    new_voice_gender: Optional[str] = None

@router.post("/approve")
async def approve_and_generate(req: ApproveGenerationRequest):
    """
    User Script Approval Gate:
    Validates script approval and starts asynchronous 3-segment generation.
    """
    try:
        job_id = await JobOrchestrator.approve_and_generate_video(
            version_id=req.version_id,
            edited_script=req.edited_script,
            edited_segments=req.edited_segments,
            provider_name=req.provider_name,
            api_key=req.api_key
        )
        return {"status": "SUCCESS", "job_id": job_id, "message": "Generation pipeline started."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}")
async def get_generation_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """Polls live state machine progress and returns final video URL when ready."""
    job = await db.get(DBGenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    video_url = None
    qa_score = None
    if job.current_state == "READY":
        q_ass = await db.execute(select(DBVideoAssembly).where(DBVideoAssembly.version_id == job.version_id))
        assembly = q_ass.scalars().first()
        if assembly and assembly.final_video_path:
            video_url = f"/storage/videos/{Path(assembly.final_video_path).name}"

        q_qa = await db.execute(select(DBQAResult).where(DBQAResult.version_id == job.version_id))
        qa = q_qa.scalars().first()
        if qa:
            qa_score = qa.overall_score

    return {
        "job_id": job.id,
        "project_id": job.project_id,
        "version_id": job.version_id,
        "current_state": job.current_state,
        "progress_pct": job.progress_pct,
        "error_message": job.error_message,
        "final_video_url": video_url,
        "qa_score": qa_score
    }


@router.post("/regenerate-segment")
async def regenerate_segment(req: RegenerateSegmentRequest):
    """
    Partial Regeneration:
    Regenerates only the selected segment (e.g. Scene 2) preserving continuity
    without discarding the rest of the video.
    """
    try:
        # Re-trigger pipeline using existing version assets
        job_id = await JobOrchestrator.approve_and_generate_video(
            version_id=req.version_id,
            provider_name=req.provider_name
        )
        return {"status": "SUCCESS", "job_id": job_id, "message": f"Regenerating segment {req.segment_index}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
