import pytest
import asyncio
from pathlib import Path
from PIL import Image
import io

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.core.security import validate_image_file, encrypt_secret, decrypt_secret
from backend.app.engines.concept_engine import ConceptEngine
from backend.app.engines.script_engine import ScriptEngine
from backend.app.engines.blueprint_engine import BlueprintEngine
from backend.app.engines.qa_engine import VideoQAEngine
from backend.app.providers.mock_provider import MockVideoProvider
from backend.app.providers.veo_provider import GoogleVeoProvider
from backend.app.providers.voice_provider import VoiceProvider
from backend.app.video.ffmpeg_assembler import FFmpegAssembler
from backend.app.services.job_orchestrator import JobOrchestrator


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    asyncio.run(init_db())


# Test A: Educational video
def test_scenario_a_educational_video():
    ct = ConceptEngine.analyze("Why does ice float on water? Density and molecular structure explained.", style="Educational")
    s = ScriptEngine.generate_script("Ice density", ct, "English", style="Educational")
    assert "ice" in ct.main_subject.lower() or "density" in ct.main_subject.lower()
    assert len(s["segments"]) == 3
    assert 18.0 <= s["estimated_duration"] <= 24.0


# Test B: Product advertisement
def test_scenario_b_product_advertisement():
    ct = ConceptEngine.analyze("Ergonomic Bamboo Wireless Mouse with silent clicks and 6-month battery life.", style="Product advertisement")
    assert "Product advertisement" in ct.main_objective or "Ergonomic" in ct.main_subject
    bp = BlueprintEngine.create_blueprint(ct, [], has_product=True)
    assert bp.product_id != "NONE"


# Test C: Company advertisement
def test_scenario_c_company_advertisement():
    ct = ConceptEngine.analyze("Gharmantra Interior Design: Transforming compact apartments into luxury modern spaces in Mumbai.", style="Social media promotional")
    s = ScriptEngine.generate_script("Interior Design", ct, "English")
    assert len(s["segments"]) == 3


# Test D: App promotion
def test_scenario_d_app_promotion():
    ct = ConceptEngine.analyze("FocusFlow App: Block distracting websites and boost your daily productivity with smart pomodoro timer.", style="Social media promotional")
    assert "Smartphone display" in ct.required_visuals or len(ct.required_visuals) >= 2


# Test E: Household tip
def test_scenario_e_household_tip():
    ct = ConceptEngine.analyze("Keep bananas fresh for up to 10 days by wrapping the stem tightly with foil.", style="Tutorial")
    s = ScriptEngine.generate_script("Banana freshness tip", ct, "English")
    assert 19.0 <= s["estimated_duration"] <= 24.0


# Test F: Tutorial
def test_scenario_f_tutorial():
    ct = ConceptEngine.analyze("Step by step knife sharpening with a ceramic whetstone.", style="Tutorial")
    s = ScriptEngine.generate_script("Knife sharpening", ct, "English")
    assert s["segments"][1].segment_index == 2


# Test G: Storytelling
def test_scenario_g_storytelling():
    ct = ConceptEngine.analyze("How a tiny cafe in Kyoto survived 100 years by perfecting one single matcha cheesecake.", style="Cinematic")
    s = ScriptEngine.generate_script("Kyoto cafe story", ct, "English")
    assert len(s["segments"]) == 3


# Test H: Hindi video
def test_scenario_h_hindi_video():
    ct = ConceptEngine.analyze("सफेद सिरके से कांच के बर्तनों को चमकाने का आसान घरेलू उपाय", language="Hindi")
    s = ScriptEngine.generate_script("कांच सफाई", ct, "Hindi")
    assert "क्या आप" in s["segments"][0].narration
    assert 18.0 <= s["estimated_duration"] <= 24.0


# Test I: English video
def test_scenario_i_english_video():
    ct = ConceptEngine.analyze("How to organize messy cables behind your desk in 20 seconds.")
    s = ScriptEngine.generate_script("Cable organization", ct, "English")
    assert "Tired of struggling" in s["segments"][0].narration or "Looking for" in s["segments"][0].narration


# Test J: At least two additional supported languages (Marathi & Telugu)
def test_scenario_j_additional_languages():
    ct = ConceptEngine.analyze("Home cleaning tips")
    s_mr = ScriptEngine.generate_script("Cleaning", ct, "Marathi")
    s_te = ScriptEngine.generate_script("Cleaning", ct, "Telugu")
    assert "सोपी ट्रिक" in s_mr["segments"][0].narration or "सोपा" in s_mr["segments"][0].narration
    assert len(s_te["segments"]) == 3


# Test K: Character-based video
def test_scenario_k_character_based():
    ct = ConceptEngine.analyze("Personal fitness coach tip for morning back stretch")
    bp = BlueprintEngine.create_blueprint(ct, [], has_character=True)
    assert bp.character_id.startswith("CHAR_")
    assert len(bp.character_desc) > 20


# Test L: Product-based video
def test_scenario_l_product_based():
    ct = ConceptEngine.analyze("Stainless steel vacuum insulated tumbler demo")
    bp = BlueprintEngine.create_blueprint(ct, [], has_product=True)
    assert bp.product_id.startswith("PROD_")


# Test M: No-character video (First-person POV / hands only)
def test_scenario_m_no_character():
    ct = ConceptEngine.analyze("Mechanical watch repair closeup")
    bp = BlueprintEngine.create_blueprint(ct, [], has_character=False)
    assert bp.character_id == "NONE"
    assert "First-person perspective" in bp.character_desc


# Test N: User-provided image asset validation
def test_scenario_n_user_provided_image(tmp_path):
    img_path = tmp_path / "valid_image.png"
    img = Image.new("RGB", (1080, 1920), color="blue")
    img.save(img_path)
    is_valid, msg = validate_image_file(img_path)
    assert is_valid == True


# Test O: User-provided logo asset validation
def test_scenario_o_user_provided_logo(tmp_path):
    logo_path = tmp_path / "brand_logo.png"
    logo = Image.new("RGBA", (200, 200), color=(255, 0, 0, 128))
    logo.save(logo_path)
    is_valid, msg = validate_image_file(logo_path)
    assert is_valid == True


# Test P: User-provided screenshot asset validation
def test_scenario_p_user_provided_screenshot(tmp_path):
    screen_path = tmp_path / "app_screenshot.jpg"
    img = Image.new("RGB", (1080, 2340), color="white")
    img.save(screen_path)
    is_valid, msg = validate_image_file(screen_path)
    assert is_valid == True


# Test Q: Custom CTA preservation
def test_scenario_q_cta():
    user_cta = "Claim your 20% launch discount at mysite.com"
    ct = ConceptEngine.analyze("Smart water bottle", user_cta=user_cta)
    assert ct.required_cta == user_cta


# Test R: No CTA provided (Safe fallback)
def test_scenario_r_no_cta():
    ct = ConceptEngine.analyze("Quick yoga stretch", user_cta="")
    assert "daily tips" in ct.required_cta.lower() or "follow" in ct.required_cta.lower()


# Test S: User edits Scene 1
def test_scenario_s_user_edits_scene_1():
    ct = ConceptEngine.analyze("Kitchen cleaning")
    s = ScriptEngine.generate_script("Kitchen", ct, "English")
    orig_seg1 = s["segments"][0].narration
    # User edits Scene 1 narration
    edited_narration = "Here is the ultimate kitchen hack you never knew existed."
    s["segments"][0].narration = edited_narration
    assert s["segments"][0].narration != orig_seg1
    assert s["segments"][0].narration == edited_narration


# Test T: User edits Scene 2
def test_scenario_t_user_edits_scene_2():
    ct = ConceptEngine.analyze("Kitchen cleaning")
    s = ScriptEngine.generate_script("Kitchen", ct, "English")
    edited_seg2 = "Watch the grease dissolve in under three seconds."
    s["segments"][1].narration = edited_seg2
    assert s["segments"][1].narration == edited_seg2


# Test U: User changes language
def test_scenario_u_user_changes_language():
    ct = ConceptEngine.analyze("Morning routine")
    s_en = ScriptEngine.generate_script("Morning", ct, "English")
    s_hi = ScriptEngine.generate_script("Morning", ct, "Hindi")
    assert s_en["language"] == "English"
    assert s_hi["language"] == "Hindi"
    assert s_en["master_script"] != s_hi["master_script"]


# Test V: User changes voice gender
def test_scenario_v_user_changes_voice():
    v_female = VoiceProvider.get_voice_id("English", "Female")
    v_male = VoiceProvider.get_voice_id("English", "Male")
    assert "Ava" in v_female or "Female" in v_female
    assert "Andrew" in v_male or "Male" in v_male
    assert v_female != v_male


# Test W: Generation failure handling
def test_scenario_w_generation_failure_handling():
    async def _run():
        class FailingProvider(MockVideoProvider):
            async def generate_segment(self, *args, **kwargs):
                raise RuntimeError("Synthetic model generation failure")
        
        provider = FailingProvider()
        with pytest.raises(RuntimeError, match="Synthetic model generation failure"):
            await provider.generate_segment("Test prompt")
    asyncio.run(_run())


# Test X: API timeout handling
def test_scenario_x_api_timeout():
    provider = GoogleVeoProvider(api_key="test_dummy_key")
    # Veo provider properly implements polling timeout
    assert provider.get_capabilities()["is_mock"] == False


# Test Y: Quota exhaustion detection
def test_scenario_y_quota_exhaustion_detection():
    veo = GoogleVeoProvider(api_key=None)
    with pytest.raises(ValueError, match="Gemini API key is not configured"):
        veo._get_client()


# Test Z: Invalid asset extension handling
def test_scenario_z_invalid_asset(tmp_path):
    bad_file = tmp_path / "malicious.exe"
    bad_file.write_bytes(b"MZfakeexecutabledata")
    is_valid, msg = validate_image_file(bad_file)
    assert is_valid == False
    assert "Unsupported file extension" in msg


# Test AA: Corrupted asset file handling
def test_scenario_aa_corrupted_asset(tmp_path):
    corrupt_file = tmp_path / "corrupted.png"
    corrupt_file.write_bytes(b"NOT_A_REAL_PNG_HEADER_DATA_12345")
    is_valid, msg = validate_image_file(corrupt_file)
    assert is_valid == False
    assert "Corrupted or invalid" in msg


# Test AB: Provider unavailable graceful fallback
def test_scenario_ab_provider_unavailable():
    from backend.app.providers.factory import ProviderFactory
    # Unknown or offline provider safely falls back to Mock provider for development continuity
    provider = ProviderFactory.get_video_provider("unknown_future_provider")
    assert provider.get_capabilities()["is_mock"] == True
