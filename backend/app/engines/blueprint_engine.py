import uuid
from typing import Dict, Any, List, Optional
from backend.app.engines.concept_engine import ContentTruthLayer
from backend.app.models.schema import SegmentApprovalItem

class MasterVideoBlueprint:
    """
    Acts as the single source of truth for all three video generations,
    ensuring character, product, environment, camera, and lighting continuity.
    """
    def __init__(
        self,
        character_id: str,
        character_desc: str,
        product_id: str,
        product_desc: str,
        environment_desc: str,
        camera_plan: str,
        lighting_plan: str,
        segment_prompts: List[Dict[str, Any]]
    ):
        self.character_id = character_id
        self.character_desc = character_desc
        self.product_id = product_id
        self.product_desc = product_desc
        self.environment_desc = environment_desc
        self.camera_plan = camera_plan
        self.lighting_plan = lighting_plan
        self.segment_prompts = segment_prompts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "character_desc": self.character_desc,
            "product_id": self.product_id,
            "product_desc": self.product_desc,
            "environment_desc": self.environment_desc,
            "camera_plan": self.camera_plan,
            "lighting_plan": self.lighting_plan,
            "segment_prompts": self.segment_prompts
        }


class BlueprintEngine:
    """
    Synthesizes the Master Video Blueprint from the approved script,
    user assets, and Content Truth Layer.
    """

    @classmethod
    def create_blueprint(
        cls,
        truth_layer: ContentTruthLayer,
        segments: List[SegmentApprovalItem],
        style: str = "Realistic",
        aspect_ratio: str = "9:16",
        has_character: bool = True,
        has_product: bool = True,
        uploaded_assets: Optional[List[Dict[str, Any]]] = None
    ) -> MasterVideoBlueprint:
        # 1. Establish persistent Character ID & Profile
        if has_character:
            char_id = f"CHAR_{uuid.uuid4().hex[:8].upper()}"
            char_desc = (
                "Warm, relatable expert host in their early 30s with neat grooming, "
                "wearing a modern casual fitted denim overshirt over a plain neutral grey tee. "
                "Natural friendly demeanor, expressive eyes, clear confident hand gestures."
            )
        else:
            char_id = "NONE"
            char_desc = "First-person perspective, focusing exclusively on hands and tools without full face."

        # 2. Establish persistent Product ID & Profile
        if has_product:
            prod_id = f"PROD_{uuid.uuid4().hex[:8].upper()}"
            prod_desc = (
                f"{truth_layer.main_subject} - clearly defined container/tool, modern sleek ergonomic design, "
                "crisp consistent color palette and clean contours."
            )
        else:
            prod_id = "NONE"
            prod_desc = "Standard household surfaces and natural materials."

        # 3. Environment & Lighting Plan
        env_desc = (
            "Modern, bright minimalist interior space with clean architectural lines, "
            "polished warm surfaces, subtle blurred indoor background with houseplants."
        )
        lighting_plan = (
            "Soft directional 5600K daylight key light from 45-degree angle, "
            "warm subtle rim light separating subject from background, zero harsh shadows."
        )
        camera_plan = (
            "Vertical 9:16 portrait framing, shallow depth-of-field (f/2.8 lens equivalent), "
            "smooth subtle push-in camera motion, eye-level framing."
        )

        # 4. Generate Highly Specific Production Prompts for Segments 1, 2, and 3
        prompts = []
        for seg in segments:
            idx = seg.segment_index
            if idx == 1:
                start_state = "Subject introduces problem, holding focus on the scene."
                end_state = "Hands bring tool into frame, poised to begin demonstration."
                motion = "Slow push-in toward the problem area."
                prompt_text = (
                    f"9:16 vertical short. {style} style. {env_desc} {lighting_plan} "
                    f"{char_desc if has_character else ''} {prod_desc if has_product else ''} "
                    f"Scene begins with {start_state}. Camera executes {motion}. "
                    f"Action: {seg.visual_description}. "
                    f"Scene concludes precisely as {end_state}. Photorealistic, pristine 1080x1920 vertical composition, 24fps."
                )
            elif idx == 2:
                start_state = "Exact continuation: hands already in position from previous scene."
                end_state = "Action finishes cleanly, revealing transformation."
                motion = "Steady medium-close framing tracking the hands."
                prompt_text = (
                    f"9:16 vertical short. {style} style. Seamless continuation from Scene 1 in exact same {env_desc} "
                    f"under exact same {lighting_plan} {char_desc if has_character else ''} {prod_desc if has_product else ''} "
                    f"Starting state: {start_state} Camera executes {motion}. "
                    f"Action: {seg.visual_description}. "
                    f"Ending state: {end_state}. Maintain continuous wardrobe, hair, and object position. Photorealistic, 1080x1920, 24fps."
                )
            else:  # idx == 3
                start_state = "Exact continuation: sparkling clean transformed result now clearly visible."
                end_state = "Subject smiles and gestures confidently toward camera for CTA."
                motion = "Gentle pull-back to wider framed beauty shot."
                prompt_text = (
                    f"9:16 vertical short. {style} style. Seamless continuation from Scene 2 in exact same {env_desc} "
                    f"under exact same {lighting_plan} {char_desc if has_character else ''} "
                    f"Starting state: {start_state} Camera executes {motion}. "
                    f"Action: {seg.visual_description}. "
                    f"Ending state: {end_state}. Warm satisfying resolution, premium cinematic finish, 1080x1920, 24fps."
                )

            prompts.append({
                "segment_index": idx,
                "duration_sec": seg.duration_sec,
                "prompt": prompt_text,
                "negative_prompt": "distorted hands, extra fingers, cartoonish, oversaturated, blurry, bad lighting, text artifact, jitter, flickering, sudden background shift",
                "start_state": start_state,
                "end_state": end_state,
                "camera_movement": motion
            })

        return MasterVideoBlueprint(
            character_id=char_id,
            character_desc=char_desc,
            product_id=prod_id,
            product_desc=prod_desc,
            environment_desc=env_desc,
            camera_plan=camera_plan,
            lighting_plan=lighting_plan,
            segment_prompts=prompts
        )
