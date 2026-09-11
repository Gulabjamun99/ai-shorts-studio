import json
import re
from typing import Dict, Any, List
from backend.app.core.config import settings

class ContentTruthLayer:
    """
    Enforces strict factual boundaries.
    Never hallucinates unprovided prices, discounts, medical claims, statistics, or URLs.
    """
    def __init__(
        self,
        main_subject: str,
        main_objective: str,
        audience: str,
        required_visuals: List[str],
        required_actions: List[str],
        required_cta: str,
        verified_facts: List[str],
        forbidden_claims: List[str]
    ):
        self.main_subject = main_subject
        self.main_objective = main_objective
        self.audience = audience
        self.required_visuals = required_visuals
        self.required_actions = required_actions
        self.required_cta = required_cta
        self.verified_facts = verified_facts
        self.forbidden_claims = forbidden_claims

    def to_dict(self) -> Dict[str, Any]:
        return {
            "main_subject": self.main_subject,
            "main_objective": self.main_objective,
            "audience": self.audience,
            "required_visuals": self.required_visuals,
            "required_actions": self.required_actions,
            "required_cta": self.required_cta,
            "verified_facts": self.verified_facts,
            "forbidden_claims": self.forbidden_claims
        }


class ConceptEngine:
    """
    Analyzes raw user input, extracts structured objectives,
    and isolates verified facts from creative interpretations.
    """

    @staticmethod
    def analyze(
        concept: str,
        title: str = "",
        user_cta: str = "",
        language: str = "English",
        platform: str = "Both",
        style: str = "Tutorial"
    ) -> ContentTruthLayer:
        # Check for explicit numbers, prices, or URLs provided by user
        found_numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', concept)
        found_urls = re.findall(r'https?://\S+|www\.\S+', concept)
        
        # Derive primary subject
        subject_candidate = title if title else concept.split(".")[0]
        main_subject = subject_candidate[:80].strip()

        # Extract required visuals based on keywords
        words = set(re.findall(r'\b\w{4,}\b', concept.lower()))
        visual_elements = []
        action_elements = []

        if "clean" in words or "glass" in words or "spray" in words:
            visual_elements.extend(["Glass surface", "Spray solution", "Cleaning cloth or newspaper"])
            action_elements.extend(["Spray solution onto dirty surface", "Wipe smoothly with circular motion", "Reveal sparkling clean reflection"])
        elif "food" in words or "cook" in words or "recipe" in words:
            visual_elements.extend(["Fresh ingredients", "Cooking pan or utensil", "Plated delicious dish"])
            action_elements.extend(["Display fresh ingredients", "Cook and stir with precision", "Serve hot with final garnish"])
        elif "app" in words or "software" in words or "phone" in words:
            visual_elements.extend(["Smartphone display", "App interface", "Satisfied user tapping screen"])
            action_elements.extend(["Show common user frustration", "Open app and complete task in seconds", "Show successful result"])
        else:
            visual_elements.extend([f"{main_subject} in clear focus", "Demonstration action", "Impressive end result"])
            action_elements.extend(["Introduce the subject/challenge", "Demonstrate the core solution", "Showcase the final benefit"])

        # Anti-hallucination forbidden claims
        forbidden_claims = [
            "Do not invent fake prices or discounts not mentioned in raw concept.",
            "Do not fabricate medical or health guarantees.",
            "Do not invent statistics, awards, or customer testimonials.",
            "Do not fabricate phone numbers or unverified website domains."
        ]

        # CTA preservation
        cta = user_cta.strip() if user_cta else "Follow for more daily tips!"

        return ContentTruthLayer(
            main_subject=main_subject,
            main_objective=f"Educate and engage audience about {main_subject}",
            audience="Mobile social media viewers (Instagram & YouTube Shorts)",
            required_visuals=visual_elements,
            required_actions=action_elements,
            required_cta=cta,
            verified_facts=found_numbers + found_urls,
            forbidden_claims=forbidden_claims
        )
