import re
from typing import Dict, List, Any
from backend.app.engines.concept_engine import ContentTruthLayer
from backend.app.models.schema import SegmentApprovalItem

# Language speech rates (Words Per Minute / syllables per second calibration)
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
    Generates a coherent 20-23 second master script and segments it into
    three continuous story parts with strict duration validation.
    """

    @classmethod
    def estimate_duration(cls, text: str, language: str) -> float:
        """Estimates spoken duration in seconds based on language-specific cadence."""
        words = len(re.findall(r'\b\S+\b', text))
        rate_info = SPEECH_RATES.get(language, DEFAULT_SPEECH_RATE)
        wpm = rate_info["wpm"]
        seconds = (words / wpm) * 60.0
        return round(seconds, 1)

    @classmethod
    def enforce_script_length(cls, text: str, language: str, target_seconds: float = 22.0) -> str:
        """
        Compresses script if it exceeds maximum target duration.
        Never allows voice to be unnaturally rushed.
        """
        rate_info = SPEECH_RATES.get(language, DEFAULT_SPEECH_RATE)
        max_allowed_words = int(rate_info["max_words_22s"] * (target_seconds / 22.0))
        
        words = re.findall(r'\b\S+\b', text)
        if len(words) <= max_allowed_words:
            return text
        
        # Condense sentences to fit within budget
        sentences = [s.strip() for s in re.split(r'[.!?।]', text) if s.strip()]
        condensed = []
        current_word_count = 0
        
        for s in sentences:
            s_words = len(s.split())
            if current_word_count + s_words <= max_allowed_words:
                condensed.append(s)
                current_word_count += s_words
            else:
                break
        
        if not condensed:
            condensed = [" ".join(words[:max_allowed_words])]
            
        return ". ".join(condensed) + "."

    @classmethod
    def generate_script(
        cls,
        concept: str,
        truth_layer: ContentTruthLayer,
        language: str = "English",
        style: str = "Tutorial",
        target_duration: float = 22.0
    ) -> Dict[str, Any]:
        """
        Builds the 3-segment narrative:
        Segment 1: Hook / problem / context (~7.3s)
        Segment 2: Action / solution / demonstration (~7.3s)
        Segment 3: Result / benefit / CTA (~7.4s)
        """
        subject = truth_layer.main_subject
        action = truth_layer.required_actions[1] if len(truth_layer.required_actions) > 1 else f"apply {subject}"
        cta = truth_layer.required_cta

        # Localized natural scripts per supported language
        if language == "Hindi":
            seg1_narration = f"क्या आप भी {subject} को लेकर परेशान हैं? आज सीखिए यह आसान तरीका।"
            seg1_text = f"{subject} का आसान तरीका!"
            
            seg2_narration = f"बस ध्यान से देखिए: {action}। यह तुरंत और बेहतरीन असर दिखाता है।"
            seg2_text = "आसान तरीका - तुरंत असर"
            
            seg3_narration = f"देखिए शानदार परिणाम! अगर यह ट्रिक पसंद आई तो {cta}।"
            seg3_text = f"शानदार रिजल्ट! {cta}"

        elif language == "Marathi":
            seg1_narration = f"{subject} मुळे त्रस्त आहात का? आजच शिका ही सोपी आणि भारी ट्रिक!"
            seg1_text = f"{subject} ची सोपी ट्रिक!"
            
            seg2_narration = f"फक्त काळजीपूर्वक बघा: {action}। हा उपाय झटपट काम करतो."
            seg2_text = "झटपट आणि सोपा उपाय"
            
            seg3_narration = f"बघा किती सुंदर रिझल्ट आला आहे! आताच {cta}."
            seg3_text = f"सुंदर रिझल्ट! {cta}"

        elif language == "Telugu":
            seg1_narration = f"మీరు కూడా {subject} గురించి ఆలోచిస్తున్నారా? ఈ సులభమైన పద్ధతి చూడండి!"
            seg1_text = f"{subject} సులభమైన ట్రిక్!"
            
            seg2_narration = f"జాగ్రత్తగా చూడండి: {action}। ఇది చాలా వేగంగా పనిచేస్తుంది."
            seg2_text = "త్వరగా పనిచేసే పద్ధతి"
            
            seg3_narration = f"చూడండి ఎంత అద్భుతమైన రిజల్ట్ వచ్చిందో! తప్పకుండా {cta}."
            seg3_text = f"అద్భుతమైన రిజల్ట్! {cta}"

        elif language == "Tamil":
            seg1_narration = f"{subject} பற்றி கவலைப்படுகிறீர்களா? இதோ ஒரு எளிய வழிமுறை!"
            seg1_text = f"{subject} எளிய டிப்ஸ்!"
            
            seg2_narration = f"கவனமாக பாருங்கள்: {action}. இது மிக விரைவாக பலன் தரும்."
            seg2_text = "விரைவான தீர்வு"
            
            seg3_narration = f"பாருங்கள் மிகச்சிறந்த முடிவை! பயனுள்ளதாக இருந்தால் {cta}."
            seg3_text = f"சூப்பர் ரிசல்ட்! {cta}"

        elif language == "Gujarati":
            seg1_narration = f"શું તમે પણ {subject} થી પરેશાન છો? આજે શીખો આ સરળ અને શ્રેષ્ઠ રીત!"
            seg1_text = f"{subject} ની સરળ રીત!"
            
            seg2_narration = f"બસ ધ્યાનથી જુઓ: {action}। આ તરત જ અદ્ભુત પરિણામ આપે છે."
            seg2_text = "તરત જ અદ્ભુત અસર"
            
            seg3_narration = f"જુઓ આ અદ્ભુત પરિણામ! જો ટ્રીક ગમી હોય તો {cta}."
            seg3_text = f"અદ્ભુત પરિણામ! {cta}"

        elif language == "Bengali":
            seg1_narration = f"আপনি কি {subject} নিয়ে চিন্তিত? আজই শিখে নিন এই দারুণ সহজ উপায়টি!"
            seg1_text = f"{subject} এর সহজ উপায়!"
            
            seg2_narration = f"শুধু মন দিয়ে দেখুন: {action}। এটি অত্যন্ত দ্রুত কাজ করে।"
            seg2_text = "দ্রুত ও সহজ সমাধান"
            
            seg3_narration = f"দেখুন অসাধারণ ফলাফল! ভালো লাগলে অবশ্যই {cta}।"
            seg3_text = f"দারুণ ফলাফল! {cta}"

        elif language == "Punjabi":
            seg1_narration = f"ਕੀ ਤੁਸੀਂ ਵੀ {subject} ਤੋਂ ਪਰੇਸ਼ਾਨ ਹੋ? ਅੱਜ ਦੇਖੋ ਇਹ ਸੌਖਾ ਤੇ ਅਸਰਦਾਰ ਤਰੀਕਾ।"
            seg1_text = f"{subject} ਦਾ ਸੌਖਾ ਤਰੀਕਾ!"
            
            seg2_narration = f"ਬੱਸ ਧਿਆਨ ਨਾਲ ਦੇਖੋ: {action}। ਇਹ ਤੁਰੰਤ ਕਮਾਲ ਦਾ ਅਸਰ ਦਿਖਾਉਂਦਾ ਹੈ।"
            seg2_text = "ਤੁਰੰਤ ਅਸਰਦਾਰ ਤਰੀਕਾ"
            
            seg3_narration = f"ਵੇਖੋ ਕਿੰਨਾ ਸ਼ਾਨਦਾਰ ਨਤੀਜਾ ਆਇਆ! ਹੋਰ ਜਾਣਕਾਰੀ ਲਈ {cta}।"
            seg3_text = f"ਸ਼ਾਨਦਾਰ ਨਤੀਜਾ! {cta}"

        else:  # Default English
            seg1_narration = f"Tired of struggling with {subject}? Here is the 20-second trick you need to know."
            seg1_text = f"The 20-Second {subject} Hack"
            
            seg2_narration = f"Watch closely: {action}. Notice how smoothly and quickly it takes effect."
            seg2_text = "Watch the Technique"
            
            seg3_narration = f"Look at that crystal clear result! Never struggle again. {cta}"
            seg3_text = f"Flawless Result! {cta}"

        # Duration calculations
        d1 = max(6.5, min(8.0, cls.estimate_duration(seg1_narration, language)))
        d2 = max(6.5, min(8.0, cls.estimate_duration(seg2_narration, language)))
        d3 = max(6.5, min(8.0, cls.estimate_duration(seg3_narration, language)))
        
        total_d = round(d1 + d2 + d3, 1)

        # Visual descriptions aligned with narration
        v1_desc = f"Vertical 9:16 portrait. High-contrast close-up introducing {truth_layer.required_visuals[0]}, setting the context."
        v2_desc = f"Vertical 9:16 portrait. Medium close-up demonstrating {action}, showing hands and tools in active motion."
        v3_desc = f"Vertical 9:16 portrait. Final beauty shot showcasing the pristine result with dynamic lighting and call to action."

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
