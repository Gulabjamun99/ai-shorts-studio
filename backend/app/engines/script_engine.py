import re
import json
from typing import Dict, List, Any, Optional
from backend.app.engines.concept_engine import ContentTruthLayer
from backend.app.models.schema import SegmentApprovalItem

SPEECH_RATES: Dict[str, Dict[str, float]] = {
    "English": {"wpm": 138.0, "max_words_22s": 50, "min_words_20s": 42},
    "Hindi": {"wpm": 125.0, "max_words_22s": 46, "min_words_20s": 38},
    "Marathi": {"wpm": 120.0, "max_words_22s": 44, "min_words_20s": 36},
    "Telugu": {"wpm": 115.0, "max_words_22s": 40, "min_words_20s": 32},
    "Tamil": {"wpm": 115.0, "max_words_22s": 40, "min_words_20s": 32},
    "Bengali": {"wpm": 122.0, "max_words_22s": 44, "min_words_20s": 36},
    "Gujarati": {"wpm": 120.0, "max_words_22s": 42, "min_words_20s": 35},
    "Kannada": {"wpm": 115.0, "max_words_22s": 40, "min_words_20s": 32},
    "Malayalam": {"wpm": 110.0, "max_words_22s": 38, "min_words_20s": 30},
    "Punjabi": {"wpm": 125.0, "max_words_22s": 45, "min_words_20s": 37},
}

DEFAULT_SPEECH_RATE = {"wpm": 130.0, "max_words_22s": 48, "min_words_20s": 40}


class ScriptEngine:
    """
    Generates a coherent, meaningful 20-23 second master script tailored
    to the user's actual concept sentences and intent (Hook -> Solution -> Result/CTA).
    """

    @classmethod
    def estimate_duration(cls, text: str, language: str) -> float:
        words = len(re.findall(r'\b\S+\b', text))
        rate_info = SPEECH_RATES.get(language, DEFAULT_SPEECH_RATE)
        wpm = rate_info["wpm"]
        return round((words / wpm) * 60.0, 1)

    @classmethod
    def generate_script(
        cls,
        concept: str,
        truth_layer: ContentTruthLayer,
        language: str = "English",
        style: str = "Tutorial",
        target_duration: float = 22.0
    ) -> Dict[str, Any]:
        # Extract meaningful concept clauses from raw input
        clean_concept = re.sub(r'https?://\S+', '', concept).strip()
        sentences = [s.strip() for s in re.split(r'[.!?।\n]+', clean_concept) if len(s.strip()) > 3]

        subject = truth_layer.main_subject
        cta = truth_layer.required_cta.strip()
        if not cta:
            cta = "Follow for more daily tips!"

        # Classify intent: App/Product promo, Tip/Tutorial, or Story
        is_app = bool(re.search(r'\b(app|application|download|install|play store|ios|android|features)\b', concept, re.I))
        is_service = bool(re.search(r'\b(service|company|interior|design|architect|booking|consult)\b', concept, re.I))
        is_promo = is_app or is_service or "promot" in style.lower() or "advertis" in style.lower()

        # Build meaningful 3-segment narrative
        if language == "Hindi":
            if is_app or is_service:
                seg1_narration = f"क्या आप भी {subject} के लिए एक भरोसेमंद और आसान समाधान ढूंढ रहे हैं?"
                seg1_text = f"{subject} का बेस्ट सोल्यूशन!"
                
                body_desc = sentences[0] if sentences else "यह आपको देता है सबसे तेज और वेरिफाइड सर्विस"
                seg2_narration = f"अब सब कुछ होगा आसान! {body_desc[:60]}। सिर्फ एक क्लिक में अपने सारे काम पूरे करें।"
                seg2_text = "आसान और तेज सर्विस"

                seg3_narration = f"तो देर किस बात की? आज ही {cta}!"
                seg3_text = f"अभी डाउनलोड करें! {cta[:25]}"
            else:
                seg1_narration = f"क्या आप जानते हैं {subject} का यह सबसे आसान और असरदार सीक्रेट?"
                seg1_text = f"{subject} सीक्रेट हैक!"
                
                body_desc = sentences[0] if sentences else "इसे आजमाकर देखें"
                seg2_narration = f"बस ध्यान से देखिए: {body_desc[:60]}। यह तरीका तुरंत और बेहतरीन काम करता है।"
                seg2_text = "तुरंत असरदार तरीका"

                seg3_narration = f"देखिए कितना शानदार रिजल्ट आया है! अगर यह टिप पसंद आई तो {cta}।"
                seg3_text = f"शानदार रिजल्ट! {cta[:25]}"

        elif language == "Marathi":
            if is_app or is_service:
                seg1_narration = f"तुम्हीही {subject} साठी एक सोपा आणि खात्रीशीर पर्याय शोधत आहात का?"
                seg1_text = f"{subject} चा बेस्ट पर्याय!"
                
                body_desc = sentences[0] if sentences else "हे देईल तुम्हाला झटपट सेवा"
                seg2_narration = f"आता काळजी सोडा! {body_desc[:60]}। घरबसल्या सर्व कामे चुटकीसरशी पूर्ण करा."
                seg2_text = "झटपट आणि सोपी सेवा"

                seg3_narration = f"मग वाट कसली बघताय? आजच {cta}!"
                seg3_text = f"आजच ट्राय करा! {cta[:25]}"
            else:
                seg1_narration = f"{subject} ची ही सोपी ट्रिक तुम्हाला माहीत आहे का?"
                seg1_text = f"{subject} सोपी ट्रिक!"

                body_desc = sentences[0] if sentences else "हा उपाय करून पहा"
                seg2_narration = f"काळजीपूर्वक बघा: {body_desc[:60]}। हा उपाय अगदी झटपट काम करतो."
                seg2_text = "झटपट रिझल्ट"

                seg3_narration = f"बघा किती सुंदर रिझल्ट आला आहे! ही माहिती आवडली असेल तर {cta}."
                seg3_text = f"सुंदर रिझल्ट! {cta[:25]}"

        else: # Default English
            if is_app or is_service:
                seg1_narration = f"Looking for the ultimate, hassle-free way to handle {subject}?"
                seg1_text = f"The Smart {subject} Solution"
                
                body_desc = sentences[0] if sentences else "get verified results in seconds"
                seg2_narration = f"Here is the game changer: {body_desc[:65]}. Everything you need right at your fingertips."
                seg2_text = "Instant Convenience"

                seg3_narration = f"Transform your experience today. {cta}!"
                seg3_text = f"Get Started Today! {cta[:25]}"
            else:
                seg1_narration = f"Tired of struggling with {subject}? Here is the 20-second trick you need to know."
                seg1_text = f"The 20-Second {subject} Hack"

                body_desc = sentences[0] if sentences else "apply the technique smoothly"
                seg2_narration = f"Watch closely: {body_desc[:65]}. Notice how smoothly and quickly it takes effect."
                seg2_text = "Watch the Technique"

                seg3_narration = f"Look at that crystal clear result! Never struggle again. {cta}"
                seg3_text = f"Flawless Result! {cta[:25]}"

        d1 = max(6.5, min(8.0, cls.estimate_duration(seg1_narration, language)))
        d2 = max(6.5, min(8.0, cls.estimate_duration(seg2_narration, language)))
        d3 = max(6.5, min(8.0, cls.estimate_duration(seg3_narration, language)))
        total_d = round(d1 + d2 + d3, 1)

        v1_desc = f"Vertical 9:16 portrait. High-energy opening hook showcasing {subject} in dynamic close-up."
        v2_desc = f"Vertical 9:16 portrait. Smooth motion demonstration showcasing active solution and clear details."
        v3_desc = f"Vertical 9:16 portrait. High-impact resolution showing final outcome with clear call-to-action text."

        segments = [
            SegmentApprovalItem(
                segment_index=1,
                duration_sec=d1,
                narration=seg1_narration,
                visual_description=v1_desc,
                on_screen_text=seg1_text
            ),
            SegmentApprovalItem(
                segment_index=2,
                duration_sec=d2,
                narration=seg2_narration,
                visual_description=v2_desc,
                on_screen_text=seg2_text
            ),
            SegmentApprovalItem(
                segment_index=3,
                duration_sec=d3,
                narration=seg3_narration,
                visual_description=v3_desc,
                on_screen_text=seg3_text
            ),
        ]

        master_script = f"{seg1_narration} {seg2_narration} {seg3_narration}"

        return {
            "master_script": master_script,
            "language": language,
            "estimated_duration": total_d,
            "segments": segments
        }
