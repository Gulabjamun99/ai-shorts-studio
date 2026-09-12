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
        
        # Derive primary subject cleanly from title or first concept line
        first_line = concept.strip().splitlines()[0] if concept.strip() else "Smart Hack"
        subject_candidate = title.strip() if title and title.strip() else first_line
        main_subject = re.sub(r'[।.:!?]+$', '', subject_candidate).strip()[:80]

        # Extract required visuals dynamically based on concept words
        concept_lower = concept.lower()
        visual_elements = []
        action_elements = []

        if "microwave" in concept_lower or "माइक्रोवेव" in concept:
            visual_elements.extend(["Microwave interior with greasy stains", "Bowl with water and sliced lemon", "Steam softening grime", "Clean wiped surface"])
            action_elements.extend(["Place lemon water bowl in microwave", "Heat on high to generate steam", "Wipe clean with cloth effortlessly"])
        elif "शीशे" in concept or "खिड़की" in concept or "window" in concept_lower:
            visual_elements.extend(["Window glass surface", "Cleaning solution spray bottle", "Wiping cloth"])
            action_elements.extend(["Spray solution onto dirty glass", "Wipe smoothly in circular motion", "Reveal crystal clean reflection"])
        elif "food" in concept_lower or "cook" in concept_lower or "recipe" in concept_lower or "खाना" in concept:
            visual_elements.extend(["Fresh ingredients", "Cooking pan or utensil", "Plated delicious dish"])
            action_elements.extend(["Display fresh ingredients", "Cook and stir with precision", "Serve hot with final garnish"])
        elif "app" in concept_lower or "software" in concept_lower or "phone" in concept_lower or "डाउनलोड" in concept:
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
