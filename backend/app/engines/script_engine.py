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


def parse_concept_structure(concept: str) -> Dict[str, Any]:
    lines = [line.strip() for line in concept.splitlines() if line.strip()]
    items: List[str] = []
    steps: List[str] = []
    tips: List[str] = []
    cta_candidates: List[str] = []
    header: str = ""

    item_section = False
    step_section = False
    tip_section = False

    for line in lines:
        if re.search(r'(https?://\S+|play\.google\.com|download|ऐप डाउनलोड|एप डाउनलोड)', line, re.I):
            clean_line = re.sub(r'https?://\S+', '', line).strip()
            if clean_line:
                cta_candidates.append(clean_line)
            continue

        if re.search(r'^(?:💡\s*)?(?:स्मार्ट\s*टिप|टिप|tip|smart\s*tip|pro\s*tip)[:\s-]', line, re.I):
            tip_text = re.sub(r'^(?:💡\s*)?(?:स्मार्ट\s*टिप|टिप|tip|smart\s*tip|pro\s*tip)[:\s-]*', '', line, flags=re.I).strip()
            if tip_text:
                tips.append(tip_text)
            tip_section = True
            item_section = False
            step_section = False
            continue

        if re.search(r'^(?:सामग्री|\(?\s*required\s*items\s*\)?|items|ingredients)', line, re.I):
            item_text = re.sub(r'^(?:सामग्री|\(?\s*required\s*items\s*\)?|items|ingredients|[:\s\(\)-])+', '', line, flags=re.I).strip()
            if item_text and len(item_text) > 2 and item_text not in ["():", "()"]:
                items.append(item_text)
            item_section = True
            step_section = False
            tip_section = False
            continue

        if re.search(r'^(?:चरण|\(?\s*steps\s*\)?|instructions)', line, re.I):
            step_section = True
            item_section = False
            tip_section = False
            continue

        step_match = re.match(r'^(?:चरण\s*\d+[:.-]?|\d+[.)]\s*|step\s*\d+[:.-]?)\s*(.*)', line, re.I)
        if step_match:
            step_body = step_match.group(1).strip()
            if step_body:
                steps.append(step_body)
            step_section = True
            item_section = False
            continue

        if item_section:
            clean_it = re.sub(r'^(?:सामग्री|\(?\s*required\s*items\s*\)?|items|ingredients|[:\s\(\)-])+', '', line, flags=re.I).strip()
            if clean_it and len(clean_it) > 2 and clean_it not in ["():", "()"]:
                items.append(clean_it)
        elif step_section and len(steps) > 0:
            steps[-1] += " " + line
        elif tip_section and len(tips) > 0:
            tips[-1] += " " + line
        else:
            if not header:
                header = line

    return {
        "header": header,
        "items": items,
        "steps": steps,
        "tips": tips,
        "cta": " ".join(cta_candidates).strip()
    }


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
        parsed = parse_concept_structure(concept)
        clean_concept = re.sub(r'https?://\S+', '', concept).strip()
        sentences = [s.strip() for s in re.split(r'[.!?।\n]+', clean_concept) if len(s.strip()) > 3]

        subject = truth_layer.main_subject
        cta = truth_layer.required_cta.strip()
        if not cta:
            cta = "Follow for more daily tips!"
        if parsed["cta"]:
            cta = parsed["cta"]

        has_steps = len(parsed["steps"]) >= 2

        # Classify intent: App/Product promo, Tip/Tutorial, or Story
        is_app = bool(re.search(r'\b(app|application|download|install|play store|ios|android|features|gharmantra)\b', concept, re.I))
        is_service = bool(re.search(r'\b(service|company|interior|design|architect|booking|consult)\b', concept, re.I))

        # Build meaningful 3-segment narrative strictly matching user's actual concept
        if language == "Hindi":
            if has_steps:
                items_clean = [re.sub(r'^(?:सामग्री|\(?\s*required\s*items\s*\)?|items|ingredients|[:\s\(\)-])+', '', it, flags=re.I).strip() for it in parsed["items"]]
                items_clean = [it for it in items_clean if it and len(it) > 2 and it not in ["():", "()"]]
                items_str = ", ".join(items_clean) if items_clean else ""

                natural_subject = subject
                natural_subject = re.sub(r'बनाएं$', 'बनाना', natural_subject)
                natural_subject = re.sub(r'करें$', 'करना', natural_subject)
                natural_subject = re.sub(r'सीखें$', 'सीखना', natural_subject)
                natural_subject = re.sub(r'हटाएं$', 'हटाना', natural_subject)
                natural_subject = re.sub(r'चमकाएं$', 'चमकाना', natural_subject)

                if re.search(r'(करें|करना|सीखें|बनाएं|बनाना|हटाएं|हटाना|चमकाएं|चमकाना)$', subject):
                    if items_str:
                        seg1_narration = f"क्या आप भी {natural_subject} चाहते हैं? यह आसान घरेलू ट्रिक जरूर आजमाएं! इसके लिए आपको चाहिए: {items_str}।"
                    else:
                        seg1_narration = f"क्या आप भी {natural_subject} चाहते हैं? यह आसान ट्रिक आपकी लाइफ को बहुत आसान बना देगी!"
                else:
                    if items_str:
                        seg1_narration = f"क्या आप भी {subject} का सबसे आसान और असरदार तरीका ढूंढ रहे हैं? इसके लिए आपको चाहिए: {items_str}।"
                    else:
                        seg1_narration = f"क्या आप भी {subject} का सबसे आसान और असरदार तरीका ढूंढ रहे हैं? यह आसान घरेलू ट्रिक जरूर आजमाएं!"
                seg1_text = f"{subject[:30]}! ✨"

                # Combine actual user steps in exact chronological order (up to 4 steps)
                step_parts = []
                for idx, st in enumerate(parsed["steps"][:4], start=1):
                    cleaned_st = re.sub(r'^(?:चरण\s*\d+[:.-]?|\d+[.)]\s*|step\s*\d+[:.-]?)\s*', '', st, flags=re.I).strip()
                    cleaned_st = re.sub(r'[।.]+$', '', cleaned_st).strip()
                    step_parts.append(f"स्टेप {idx}: {cleaned_st}")
                seg2_narration = "। ".join(step_parts) + "।"
                first_step_short = re.sub(r'^(?:चरण\s*\d+[:.-]?|\d+[.)]\s*|step\s*\d+[:.-]?)\s*', '', parsed["steps"][0], flags=re.I).strip()[:24]
                seg2_text = f"स्टेप 1: {first_step_short} 🧽"

                raw_tip = parsed["tips"][0] if parsed["tips"] else "यह आसान तरीका बिना किसी मेहनत के तुरंत बेहतरीन असर दिखाता है"
                tip_clean = re.sub(r'[।.\s]+$', '', raw_tip).strip()
                seg3_narration = f"स्मार्ट टिप: {tip_clean}। और अधिक जानकारी के लिए, {cta}!"
                seg3_text = f"{cta[:30]} 📲"

            elif is_app or is_service:
                seg1_narration = f"क्या आप भी {subject} के लिए एक भरोसेमंद और आसान समाधान ढूंढ रहे हैं?"
                seg1_text = f"{subject[:25]} का बेस्ट सोल्यूशन!"
                
                body_desc = sentences[0] if sentences else "यह आपको देता है सबसे तेज और वेरिफाइड सर्विस"
                seg2_narration = f"अब सब कुछ होगा आसान! {body_desc[:65]}। सिर्फ एक क्लिक में अपने सारे काम पूरे करें।"
                seg2_text = "आसान और तेज सर्विस"

                seg3_narration = f"तो देर किस बात की? {cta}!"
                seg3_text = f"{cta[:30]} 📲"
            else:
                seg1_narration = f"क्या आप जानते हैं {subject} का यह सबसे आसान और असरदार सीक्रेट?"
                seg1_text = f"{subject[:25]} सीक्रेट हैक!"
                
                body_desc = sentences[0] if sentences else "इसे आजमाकर देखें"
                seg2_narration = f"बस ध्यान से देखिए: {body_desc[:65]}। यह तरीका तुरंत और बेहतरीन काम करता है।"
                seg2_text = "तुरंत असरदार तरीका"

                seg3_narration = f"देखिए कितना शानदार रिजल्ट आया है! अगर यह पसंद आया तो {cta}।"
                seg3_text = f"शानदार रिजल्ट! {cta[:25]}"

        elif language == "Marathi":
            if has_steps:
                items_clean = [it.replace("सामग्री", "").strip() for it in parsed["items"] if it.strip()]
                items_str = ", ".join(items_clean) if items_clean else ""

                if items_str:
                    seg1_narration = f"{subject} चा सर्वात सोपा आणि परिणामकारक उपाय! यासाठी तुम्हाला लागेल: {items_str}."
                else:
                    seg1_narration = f"{subject} चा सर्वात सोपा आणि परिणामकारक उपाय नक्की वापरून पहा!"
                seg1_text = f"{subject[:30]}! ✨"

                step_parts = []
                for idx, st in enumerate(parsed["steps"][:3], start=1):
                    cleaned_st = re.sub(r'^(?:चरण\s*\d+[:.-]?|\d+[.)]\s*|step\s*\d+[:.-]?)\s*', '', st, flags=re.I).strip()
                    step_parts.append(f"पायरी {idx}: {cleaned_st}")
                seg2_narration = "। ".join(step_parts) + "।"
                seg2_text = "सोप्या स्टेप्स फॉलो करा 🧽"

                tip_str = parsed["tips"][0] if parsed["tips"] else "हा उपाय तुमचे काम अतिशय सोपे आणि जलद करेल"
                seg3_narration = f"स्मार्ट टिप: {tip_str}. अधिक माहितीसाठी, {cta}!"
                seg3_text = f"{cta[:30]} 📲"
            elif is_app or is_service:
                seg1_narration = f"तुम्हीही {subject} साठी एक सोपा आणि खात्रीशीर पर्याय शोधत आहात का?"
                seg1_text = f"{subject[:25]} चा बेस्ट पर्याय!"
                
                body_desc = sentences[0] if sentences else "हे देईल तुम्हाला झटपट सेवा"
                seg2_narration = f"आता काळजी सोडा! {body_desc[:60]}। घरबसल्या सर्व कामे चुटकीसरशी पूर्ण करा."
                seg2_text = "झटपट आणि सोपी सेवा"

                seg3_narration = f"मग वाट कसली बघताय? {cta}!"
                seg3_text = f"{cta[:30]}"
            else:
                seg1_narration = f"{subject} ची ही सोपी ट्रिक तुम्हाला माहीत आहे का?"
                seg1_text = f"{subject[:25]} सोपी ट्रिक!"

                body_desc = sentences[0] if sentences else "हा उपाय करून पहा"
                seg2_narration = f"काळजीपूर्वक बघा: {body_desc[:60]}। हा उपाय अगदी झटपट काम करतो."
                seg2_text = "झटपट रिझल्ट"

                seg3_narration = f"बघा किती सुंदर रिझल्ट आला आहे! ही माहिती आवडली असेल तर {cta}."
                seg3_text = f"सुंदर रिझल्ट! {cta[:25]}"

        else: # Default English
            if has_steps:
                items_clean = [it.replace("Items", "").replace("Required Items", "").strip() for it in parsed["items"] if it.strip()]
                items_str = ", ".join(items_clean) if items_clean else ""

                if items_str:
                    seg1_narration = f"Looking for the easiest and most effective way to do {subject}? All you need is: {items_str}."
                else:
                    seg1_narration = f"Looking for the easiest and most effective way to do {subject}? This genius trick will save your day!"
                seg1_text = f"{subject[:30]} ✨"

                step_parts = []
                for idx, st in enumerate(parsed["steps"][:3], start=1):
                    cleaned_st = re.sub(r'^(?:step\s*\d+[:.-]?|\d+[.)]\s*)\s*', '', st, flags=re.I).strip()
                    step_parts.append(f"Step {idx}: {cleaned_st}")
                seg2_narration = ". ".join(step_parts) + "."
                seg2_text = f"Follow the Steps 🧽"

                tip_str = parsed["tips"][0] if parsed["tips"] else "This method saves time and delivers flawless results every single time"
                seg3_narration = f"Pro Tip: {tip_str}. For more details, {cta}!"
                seg3_text = f"{cta[:30]} 📲"

            elif is_app or is_service:
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
