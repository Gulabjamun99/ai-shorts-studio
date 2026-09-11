import datetime
import enum
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel, Field

Base = declarative_base()


class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    ANALYZING = "ANALYZING"
    SCRIPT_GENERATED = "SCRIPT_GENERATED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"
    GENERATING_REFERENCE = "GENERATING_REFERENCE"
    GENERATING_SEGMENT_1 = "GENERATING_SEGMENT_1"
    GENERATING_SEGMENT_2 = "GENERATING_SEGMENT_2"
    GENERATING_SEGMENT_3 = "GENERATING_SEGMENT_3"
    VOICE_GENERATING = "VOICE_GENERATING"
    ASSEMBLING = "ASSEMBLING"
    QA = "QA"
    REPAIRING = "REPAIRING"
    READY = "READY"
    FAILED = "FAILED"


class PlatformType(str, enum.Enum):
    REELS = "Instagram Reels"
    SHORTS = "YouTube Shorts"
    BOTH = "Both"


class VideoStyle(str, enum.Enum):
    REALISTIC = "Realistic"
    CINEMATIC = "Cinematic"
    PRODUCT_AD = "Product advertisement"
    EDUCATIONAL = "Educational"
    TUTORIAL = "Tutorial"
    EXPLAINER = "Explainer"
    PROMOTIONAL = "Social media promotional"
    UGC = "UGC-style"
    CORPORATE = "Professional corporate"
    ANIMATED = "Animated"


class VoiceGender(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    NEUTRAL = "Neutral"


# --- SQLAlchemy DB Models ---

class DBProject(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    platform = Column(String(50), default="Both")
    language = Column(String(50), default="English")
    style = Column(String(50), default="Realistic")
    voice_gender = Column(String(20), default="Female")
    voice_tone = Column(String(50), default="Friendly")
    aspect_ratio = Column(String(10), default="9:16")
    target_duration = Column(Float, default=22.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    versions = relationship("DBProjectVersion", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("DBAsset", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("DBGenerationJob", back_populates="project", cascade="all, delete-orphan")


class DBProjectVersion(Base):
    __tablename__ = "project_versions"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    version_number = Column(Integer, default=1)
    raw_concept = Column(Text, nullable=False)
    status = Column(String(50), default=JobStatus.QUEUED.value)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    project = relationship("DBProject", back_populates="versions")
    content_truth = relationship("DBContentTruth", uselist=False, back_populates="version", cascade="all, delete-orphan")
    script = relationship("DBScript", uselist=False, back_populates="version", cascade="all, delete-orphan")
    blueprint = relationship("DBMasterBlueprint", uselist=False, back_populates="version", cascade="all, delete-orphan")
    segments = relationship("DBVideoSegment", back_populates="version", cascade="all, delete-orphan", order_by="DBVideoSegment.segment_index")
    assembly = relationship("DBVideoAssembly", uselist=False, back_populates="version", cascade="all, delete-orphan")
    qa_result = relationship("DBQAResult", uselist=False, back_populates="version", cascade="all, delete-orphan")


class DBContentTruth(Base):
    __tablename__ = "content_truths"
    
    id = Column(String(36), primary_key=True, index=True)
    version_id = Column(String(36), ForeignKey("project_versions.id"), nullable=False)
    main_subject = Column(String(255), default="")
    main_objective = Column(String(255), default="")
    audience = Column(String(255), default="")
    required_visuals = Column(Text, default="[]")  # JSON list
    required_actions = Column(Text, default="[]")  # JSON list
    required_cta = Column(String(255), default="")
    verified_facts = Column(Text, default="[]")    # JSON list
    forbidden_claims = Column(Text, default="[]")  # Anti-hallucination bounds
    
    version = relationship("DBProjectVersion", back_populates="content_truth")


class DBScript(Base):
    __tablename__ = "scripts"
    
    id = Column(String(36), primary_key=True, index=True)
    version_id = Column(String(36), ForeignKey("project_versions.id"), nullable=False)
    master_script = Column(Text, nullable=False)
    language = Column(String(50), default="English")
    estimated_duration = Column(Float, default=22.0)
    speech_rate_wpm = Column(Float, default=140.0)
    is_approved = Column(Boolean, default=False)
    user_edits = Column(Text, default="")
    
    version = relationship("DBProjectVersion", back_populates="script")


class DBMasterBlueprint(Base):
    __tablename__ = "master_blueprints"
    
    id = Column(String(36), primary_key=True, index=True)
    version_id = Column(String(36), ForeignKey("project_versions.id"), nullable=False)
    character_id = Column(String(100), default="NONE")
    character_desc = Column(Text, default="")
    product_id = Column(String(100), default="NONE")
    product_desc = Column(Text, default="")
    environment_desc = Column(Text, default="")
    camera_plan = Column(Text, default="")
    lighting_plan = Column(Text, default="")
    
    version = relationship("DBProjectVersion", back_populates="blueprint")


class DBVideoSegment(Base):
    __tablename__ = "video_segments"
    
    id = Column(String(36), primary_key=True, index=True)
    version_id = Column(String(36), ForeignKey("project_versions.id"), nullable=False)
    segment_index = Column(Integer, nullable=False)  # 1, 2, 3
    duration_sec = Column(Float, default=7.5)
    narration = Column(Text, default="")
    on_screen_text = Column(String(255), default="")
    visual_prompt = Column(Text, default="")
    first_frame_path = Column(String(500), default="")
    last_frame_path = Column(String(500), default="")
    raw_video_path = Column(String(500), default="")
    status = Column(String(50), default="PENDING")
    
    version = relationship("DBProjectVersion", back_populates="segments")


class DBVideoAssembly(Base):
    __tablename__ = "video_assemblies"
    
    id = Column(String(36), primary_key=True, index=True)
    version_id = Column(String(36), ForeignKey("project_versions.id"), nullable=False)
    final_video_path = Column(String(500), default="")
    subtitles_path = Column(String(500), default="")
    audio_track_path = Column(String(500), default="")
    resolution = Column(String(50), default="1080x1920")
    aspect_ratio = Column(String(20), default="9:16")
    duration_sec = Column(Float, default=22.0)
    status = Column(String(50), default="PENDING")
    
    version = relationship("DBProjectVersion", back_populates="assembly")


class DBQAResult(Base):
    __tablename__ = "qa_results"
    
    id = Column(String(36), primary_key=True, index=True)
    version_id = Column(String(36), ForeignKey("project_versions.id"), nullable=False)
    overall_score = Column(Float, default=0.0)
    passed = Column(Boolean, default=False)
    category_scores = Column(Text, default="{}")     # JSON Dict
    failure_reasons = Column(Text, default="[]")     # JSON List
    repair_attempts = Column(Integer, default=0)
    
    version = relationship("DBProjectVersion", back_populates="qa_result")


class DBAsset(Base):
    __tablename__ = "assets"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    asset_type = Column(String(50), default="IMAGE")  # LOGO, PRODUCT, CHARACTER_REF, SCREENSHOT
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), default="")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    project = relationship("DBProject", back_populates="assets")


class DBGenerationJob(Base):
    __tablename__ = "generation_jobs"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    version_id = Column(String(36), nullable=False)
    current_state = Column(String(50), default=JobStatus.QUEUED.value)
    progress_pct = Column(Integer, default=0)
    error_message = Column(Text, default="")
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    
    project = relationship("DBProject", back_populates="jobs")


class DBProviderConnection(Base):
    __tablename__ = "provider_connections"
    
    id = Column(String(36), primary_key=True, index=True)
    provider_name = Column(String(50), nullable=False)  # GEMINI, VERTEX, YOUTUBE, INSTAGRAM
    encrypted_credentials = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# --- Pydantic API Schemas ---

class CreateProjectRequest(BaseModel):
    title: str = Field(..., example="5-Second Kitchen Glass Cleaning Trick")
    concept: str = Field(..., example="White vinegar and newspaper trick to make glass surfaces crystal clear in 20 seconds.")
    platform: PlatformType = PlatformType.BOTH
    language: str = "English"
    style: VideoStyle = VideoStyle.TUTORIAL
    voice_gender: VoiceGender = VoiceGender.FEMALE
    voice_tone: str = "Friendly"
    target_duration: float = 22.0
    aspect_ratio: str = "9:16"
    cta: Optional[str] = "Try it today & subscribe!"


class SegmentApprovalItem(BaseModel):
    segment_index: int
    duration_sec: float
    narration: str
    visual_description: str
    on_screen_text: str


class ScriptApprovalData(BaseModel):
    master_script: str
    language: str
    estimated_duration: float
    segments: List[SegmentApprovalItem]


class ApproveScriptRequest(BaseModel):
    is_approved: bool = True
    edited_script: Optional[str] = None
    edited_segments: Optional[List[SegmentApprovalItem]] = None


class JobStatusResponse(BaseModel):
    job_id: str
    project_id: str
    version_id: str
    current_state: JobStatus
    progress_pct: int
    error_message: Optional[str] = None
    final_video_url: Optional[str] = None
    qa_score: Optional[float] = None


class QAScorecard(BaseModel):
    overall_score: float
    passed: bool
    categories: Dict[str, float]
    failure_reasons: List[str]
    repair_attempts: int


class PublishRequest(BaseModel):
    platform: str  # 'youtube' or 'instagram'
    title: str
    description: str
    tags: List[str] = []
    privacy: str = "public"
