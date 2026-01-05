#!/usr/bin/env python3
"""
RégimA Client Skin Assessment System

A practical intake and assessment tool for skincare practitioners to:
1. Capture client information and history
2. Assess skin type through guided questions
3. Identify concerns and map to Zone Concept pillars
4. Generate client profiles for treatment protocols

Integrates with treatment_protocol_builder.py to generate personalized routines.
"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import uuid

# Import from protocol builder for shared types
from treatment_protocol_builder import (
    SkinType, SkinConcern, ZonePillar, ClientProfile,
    ProtocolBuilder, CONCERN_ZONE_MAP
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FitzpatrickType(Enum):
    """Fitzpatrick skin phototypes for sun sensitivity assessment."""
    TYPE_I = "type_1"    # Very fair, always burns, never tans
    TYPE_II = "type_2"   # Fair, usually burns, tans minimally
    TYPE_III = "type_3"  # Medium, sometimes burns, tans uniformly
    TYPE_IV = "type_4"   # Olive, rarely burns, tans well
    TYPE_V = "type_5"    # Brown, very rarely burns, tans very easily
    TYPE_VI = "type_6"   # Dark brown/black, never burns


class LifestyleFactors(Enum):
    """Lifestyle factors affecting skin health."""
    HIGH_STRESS = "high_stress"
    POOR_SLEEP = "poor_sleep"
    SMOKER = "smoker"
    HIGH_ALCOHOL = "high_alcohol"
    POOR_DIET = "poor_diet"
    LOW_WATER_INTAKE = "low_water_intake"
    HIGH_SUN_EXPOSURE = "high_sun_exposure"
    POLLUTION_EXPOSURE = "pollution_exposure"
    SCREEN_TIME = "screen_time"  # Blue light exposure
    ACTIVE_LIFESTYLE = "active_lifestyle"
    HORMONAL_CHANGES = "hormonal_changes"


class MedicalCondition(Enum):
    """Medical conditions relevant to skincare."""
    DIABETES = "diabetes"
    THYROID_DISORDER = "thyroid_disorder"
    AUTOIMMUNE = "autoimmune"
    HORMONAL_IMBALANCE = "hormonal_imbalance"
    ALLERGIES = "allergies"
    ECZEMA_HISTORY = "eczema_history"
    PSORIASIS_HISTORY = "psoriasis_history"
    ROSACEA_DIAGNOSED = "rosacea_diagnosed"
    ACNE_HISTORY = "acne_history"
    SKIN_CANCER_HISTORY = "skin_cancer_history"
    PREGNANCY = "pregnancy"
    BREASTFEEDING = "breastfeeding"


class CurrentProduct(Enum):
    """Types of products client may currently use."""
    RETINOIDS = "retinoids"
    AHA_BHA = "aha_bha"
    VITAMIN_C = "vitamin_c"
    BENZOYL_PEROXIDE = "benzoyl_peroxide"
    PRESCRIPTION_TOPICAL = "prescription_topical"
    ORAL_MEDICATION = "oral_medication"
    NOTHING = "nothing"
    BASIC_CLEANSER_MOISTURIZER = "basic_cleanser_moisturizer"


@dataclass
class SkinAssessmentAnswers:
    """Stores answers from the skin assessment questionnaire."""
    # Basic info
    age_range: str = ""
    gender: str = ""

    # Skin type indicators
    morning_skin_feel: str = ""  # tight/dry, normal, oily, combination
    pore_visibility: str = ""    # minimal, t-zone only, all over
    midday_shine: str = ""       # none, t-zone, all over
    reaction_to_products: str = "" # rarely, sometimes, often

    # Concern indicators (1-5 scale or yes/no)
    fine_lines_concern: int = 0
    wrinkle_concern: int = 0
    firmness_concern: int = 0
    pigmentation_concern: int = 0
    redness_concern: int = 0
    acne_concern: int = 0
    texture_concern: int = 0
    hydration_concern: int = 0
    sensitivity_concern: int = 0
    dullness_concern: int = 0
    pore_concern: int = 0
    dark_circles_concern: int = 0

    # Sun behavior
    sun_reaction: str = ""  # always burns, sometimes burns, rarely burns, never burns
    tanning_ability: str = "" # never, slightly, moderately, easily

    # History
    previous_professional_treatments: List[str] = field(default_factory=list)
    product_reactions: List[str] = field(default_factory=list)
    ingredient_allergies: List[str] = field(default_factory=list)


@dataclass
class FullClientAssessment:
    """Complete client assessment record."""
    assessment_id: str
    client_id: str
    date: str
    practitioner: str

    # Personal info
    name: str
    email: str
    phone: str = ""
    date_of_birth: str = ""

    # Assessment results
    skin_type: SkinType = SkinType.NORMAL
    fitzpatrick_type: FitzpatrickType = FitzpatrickType.TYPE_III
    primary_concerns: List[SkinConcern] = field(default_factory=list)
    secondary_concerns: List[SkinConcern] = field(default_factory=list)
    zone_focus: List[ZonePillar] = field(default_factory=list)

    # Health & lifestyle
    medical_conditions: List[MedicalCondition] = field(default_factory=list)
    lifestyle_factors: List[LifestyleFactors] = field(default_factory=list)
    current_products: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)

    # Assessment data
    answers: SkinAssessmentAnswers = field(default_factory=SkinAssessmentAnswers)

    # Goals
    treatment_goals: List[str] = field(default_factory=list)
    budget_range: str = ""
    time_commitment: str = ""  # minimal, moderate, dedicated

    # Practitioner notes
    visual_observations: str = ""
    practitioner_notes: str = ""
    contraindications: List[str] = field(default_factory=list)

    # Consent
    photo_consent: bool = False
    marketing_consent: bool = False
    treatment_consent: bool = False

    def to_client_profile(self) -> ClientProfile:
        """Convert assessment to ClientProfile for protocol builder."""
        return ClientProfile(
            client_id=self.client_id,
            name=self.name,
            date_of_birth=self.date_of_birth,
            skin_type=self.skin_type,
            concerns=self.primary_concerns + self.secondary_concerns,
            allergies=self.allergies,
            current_products=self.current_products,
            medical_conditions=[m.value for m in self.medical_conditions],
            goals=self.treatment_goals,
            notes=self.practitioner_notes
        )


# =============================================================================
# Assessment Questions
# =============================================================================

SKIN_TYPE_QUESTIONS = [
    {
        "id": "morning_feel",
        "question": "How does your skin feel when you wake up (before washing)?",
        "options": [
            ("tight_dry", "Tight and dry"),
            ("normal", "Comfortable, neither dry nor oily"),
            ("slightly_oily", "Slightly oily in T-zone"),
            ("oily", "Oily all over")
        ]
    },
    {
        "id": "pore_visibility",
        "question": "How visible are your pores?",
        "options": [
            ("minimal", "Barely visible anywhere"),
            ("tzone", "Visible mainly in T-zone (nose, forehead, chin)"),
            ("cheeks_too", "Visible on cheeks as well"),
            ("large_all", "Large and visible all over")
        ]
    },
    {
        "id": "midday_shine",
        "question": "By midday, does your skin become shiny?",
        "options": [
            ("never", "Never, it stays matte or feels dry"),
            ("tzone_only", "Only in the T-zone"),
            ("mostly", "Yes, on most of my face"),
            ("very", "Very shiny, I need to blot often")
        ]
    },
    {
        "id": "product_reaction",
        "question": "How often does your skin react to new products?",
        "options": [
            ("rarely", "Rarely - I can try most products without issues"),
            ("sometimes", "Sometimes - certain ingredients cause reactions"),
            ("often", "Often - I have to be very careful with products"),
            ("always", "Almost always - my skin is very reactive")
        ]
    },
    {
        "id": "hydration",
        "question": "Does your skin ever feel dehydrated or tight after cleansing?",
        "options": [
            ("always", "Yes, always"),
            ("sometimes", "Sometimes"),
            ("rarely", "Rarely"),
            ("never", "Never")
        ]
    }
]

CONCERN_QUESTIONS = [
    {
        "id": "ageing",
        "question": "Rate your concern about signs of ageing (fine lines, wrinkles, loss of firmness):",
        "scale": 5,  # 1-5 scale
        "maps_to": [SkinConcern.FINE_LINES, SkinConcern.WRINKLES, SkinConcern.LOSS_OF_FIRMNESS]
    },
    {
        "id": "pigmentation",
        "question": "Rate your concern about uneven skin tone, dark spots, or pigmentation:",
        "scale": 5,
        "maps_to": [SkinConcern.PIGMENTATION, SkinConcern.UNEVEN_TONE]
    },
    {
        "id": "acne",
        "question": "Rate your concern about acne, breakouts, or congestion:",
        "scale": 5,
        "maps_to": [SkinConcern.ACNE, SkinConcern.ENLARGED_PORES]
    },
    {
        "id": "sensitivity",
        "question": "Rate your concern about redness, sensitivity, or irritation:",
        "scale": 5,
        "maps_to": [SkinConcern.REDNESS, SkinConcern.SENSITIVITY, SkinConcern.IRRITATION]
    },
    {
        "id": "texture",
        "question": "Rate your concern about skin texture (roughness, dullness):",
        "scale": 5,
        "maps_to": [SkinConcern.ROUGH_TEXTURE, SkinConcern.DULLNESS]
    },
    {
        "id": "hydration",
        "question": "Rate your concern about dryness or dehydration:",
        "scale": 5,
        "maps_to": [SkinConcern.DRYNESS, SkinConcern.DEHYDRATION]
    },
    {
        "id": "eyes",
        "question": "Rate your concern about the eye area (dark circles, puffiness, crow's feet):",
        "scale": 5,
        "maps_to": [SkinConcern.DARK_CIRCLES, SkinConcern.PUFFINESS, SkinConcern.FINE_LINES]
    }
]

FITZPATRICK_QUESTIONS = [
    {
        "id": "sun_reaction",
        "question": "What happens when you spend time in the sun without protection?",
        "options": [
            ("always_burn", "I always burn, never tan"),
            ("usually_burn", "I usually burn, tan minimally"),
            ("sometimes_burn", "I sometimes burn, then tan"),
            ("rarely_burn", "I rarely burn, tan easily"),
            ("very_rarely_burn", "I very rarely burn, tan very easily"),
            ("never_burn", "I never burn")
        ]
    },
    {
        "id": "natural_color",
        "question": "What is your natural skin color (unexposed areas)?",
        "options": [
            ("very_fair", "Very fair/pale"),
            ("fair", "Fair"),
            ("medium", "Medium/beige"),
            ("olive", "Olive"),
            ("brown", "Brown"),
            ("dark_brown", "Dark brown/black")
        ]
    }
]


# =============================================================================
# Assessment Engine
# =============================================================================

class SkinAssessmentEngine:
    """
    Engine for conducting client skin assessments.

    Features:
    - Guided questionnaire for skin type determination
    - Concern identification and prioritization
    - Fitzpatrick type assessment
    - Zone Concept pillar mapping
    - Integration with Protocol Builder
    """

    def __init__(self, data_path: Optional[Path] = None):
        self.base_path = Path(__file__).parent.parent
        self.data_path = data_path or self.base_path / "data"
        self.data_path.mkdir(exist_ok=True)

        self._assessments: Dict[str, FullClientAssessment] = {}
        self._load_assessments()

        logger.info("SkinAssessmentEngine initialized")

    def _load_assessments(self) -> None:
        """Load existing assessments from storage."""
        assessments_file = self.data_path / "client_assessments.json"
        if assessments_file.exists():
            try:
                with open(assessments_file, 'r') as f:
                    data = json.load(f)
                    for a in data.get('assessments', []):
                        # Reconstruct enums
                        a['skin_type'] = SkinType(a['skin_type'])
                        a['fitzpatrick_type'] = FitzpatrickType(a['fitzpatrick_type'])
                        a['primary_concerns'] = [SkinConcern(c) for c in a['primary_concerns']]
                        a['secondary_concerns'] = [SkinConcern(c) for c in a['secondary_concerns']]
                        a['zone_focus'] = [ZonePillar(z) for z in a['zone_focus']]
                        a['medical_conditions'] = [MedicalCondition(m) for m in a['medical_conditions']]
                        a['lifestyle_factors'] = [LifestyleFactors(l) for l in a['lifestyle_factors']]
                        a['answers'] = SkinAssessmentAnswers(**a['answers'])

                        assessment = FullClientAssessment(**a)
                        self._assessments[assessment.assessment_id] = assessment
                logger.info(f"Loaded {len(self._assessments)} existing assessments")
            except Exception as e:
                logger.warning(f"Could not load assessments: {e}")

    def save_assessments(self) -> None:
        """Save assessments to storage."""
        assessments_file = self.data_path / "client_assessments.json"

        data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "assessments": []
        }

        for assessment in self._assessments.values():
            a_dict = asdict(assessment)
            # Convert enums to strings
            a_dict['skin_type'] = assessment.skin_type.value
            a_dict['fitzpatrick_type'] = assessment.fitzpatrick_type.value
            a_dict['primary_concerns'] = [c.value for c in assessment.primary_concerns]
            a_dict['secondary_concerns'] = [c.value for c in assessment.secondary_concerns]
            a_dict['zone_focus'] = [z.value for z in assessment.zone_focus]
            a_dict['medical_conditions'] = [m.value for m in assessment.medical_conditions]
            a_dict['lifestyle_factors'] = [l.value for l in assessment.lifestyle_factors]
            data['assessments'].append(a_dict)

        with open(assessments_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(self._assessments)} assessments")

    def create_assessment(
        self,
        practitioner: str,
        client_name: str,
        client_email: str,
        client_phone: str = "",
        date_of_birth: str = ""
    ) -> FullClientAssessment:
        """Create a new client assessment."""
        assessment_id = f"ASM-{uuid.uuid4().hex[:8].upper()}"
        client_id = f"CLI-{uuid.uuid4().hex[:8].upper()}"

        assessment = FullClientAssessment(
            assessment_id=assessment_id,
            client_id=client_id,
            date=datetime.now().isoformat(),
            practitioner=practitioner,
            name=client_name,
            email=client_email,
            phone=client_phone,
            date_of_birth=date_of_birth
        )

        self._assessments[assessment_id] = assessment
        logger.info(f"Created assessment {assessment_id} for {client_name}")
        return assessment

    def determine_skin_type(self, answers: Dict[str, str]) -> SkinType:
        """Determine skin type based on questionnaire answers."""
        score = {
            SkinType.DRY: 0,
            SkinType.OILY: 0,
            SkinType.COMBINATION: 0,
            SkinType.SENSITIVE: 0,
            SkinType.NORMAL: 0
        }

        # Morning feel
        morning = answers.get("morning_feel", "")
        if morning == "tight_dry":
            score[SkinType.DRY] += 2
        elif morning == "normal":
            score[SkinType.NORMAL] += 2
        elif morning == "slightly_oily":
            score[SkinType.COMBINATION] += 2
        elif morning == "oily":
            score[SkinType.OILY] += 2

        # Pore visibility
        pores = answers.get("pore_visibility", "")
        if pores == "minimal":
            score[SkinType.DRY] += 1
            score[SkinType.NORMAL] += 1
        elif pores == "tzone":
            score[SkinType.COMBINATION] += 2
        elif pores in ["cheeks_too", "large_all"]:
            score[SkinType.OILY] += 2

        # Midday shine
        shine = answers.get("midday_shine", "")
        if shine == "never":
            score[SkinType.DRY] += 2
        elif shine == "tzone_only":
            score[SkinType.COMBINATION] += 2
        elif shine in ["mostly", "very"]:
            score[SkinType.OILY] += 2

        # Product reaction
        reaction = answers.get("product_reaction", "")
        if reaction in ["often", "always"]:
            score[SkinType.SENSITIVE] += 3

        # Hydration
        hydration = answers.get("hydration", "")
        if hydration == "always":
            score[SkinType.DRY] += 2
        elif hydration == "sometimes":
            score[SkinType.COMBINATION] += 1

        # Get highest scoring type
        return max(score, key=score.get)

    def determine_fitzpatrick(self, answers: Dict[str, str]) -> FitzpatrickType:
        """Determine Fitzpatrick skin type."""
        sun_reaction = answers.get("sun_reaction", "")
        natural_color = answers.get("natural_color", "")

        # Simple mapping based on combined factors
        if sun_reaction == "always_burn" or natural_color == "very_fair":
            return FitzpatrickType.TYPE_I
        elif sun_reaction == "usually_burn" or natural_color == "fair":
            return FitzpatrickType.TYPE_II
        elif sun_reaction == "sometimes_burn" or natural_color == "medium":
            return FitzpatrickType.TYPE_III
        elif sun_reaction == "rarely_burn" or natural_color == "olive":
            return FitzpatrickType.TYPE_IV
        elif sun_reaction == "very_rarely_burn" or natural_color == "brown":
            return FitzpatrickType.TYPE_V
        elif sun_reaction == "never_burn" or natural_color == "dark_brown":
            return FitzpatrickType.TYPE_VI

        return FitzpatrickType.TYPE_III  # Default

    def analyze_concerns(
        self,
        concern_ratings: Dict[str, int],
        threshold_primary: int = 4,
        threshold_secondary: int = 2
    ) -> Tuple[List[SkinConcern], List[SkinConcern]]:
        """
        Analyze concern ratings and return prioritized concerns.

        Args:
            concern_ratings: Dict mapping question_id to 1-5 rating
            threshold_primary: Rating >= this is a primary concern
            threshold_secondary: Rating >= this is a secondary concern

        Returns:
            Tuple of (primary_concerns, secondary_concerns)
        """
        primary = []
        secondary = []

        for question in CONCERN_QUESTIONS:
            rating = concern_ratings.get(question["id"], 0)

            if rating >= threshold_primary:
                primary.extend(question["maps_to"])
            elif rating >= threshold_secondary:
                secondary.extend(question["maps_to"])

        # Remove duplicates while preserving order
        primary = list(dict.fromkeys(primary))
        secondary = [c for c in dict.fromkeys(secondary) if c not in primary]

        return primary, secondary

    def determine_zone_focus(
        self,
        concerns: List[SkinConcern]
    ) -> List[ZonePillar]:
        """Determine which Zone Concept pillars to focus on."""
        pillar_counts = {p: 0 for p in ZonePillar}

        for concern in concerns:
            if concern in CONCERN_ZONE_MAP:
                for pillar in CONCERN_ZONE_MAP[concern]:
                    pillar_counts[pillar] += 1

        # Sort by count, return those with count > 0
        sorted_pillars = sorted(pillar_counts.items(), key=lambda x: x[1], reverse=True)
        return [p for p, count in sorted_pillars if count > 0]

    def complete_assessment(
        self,
        assessment_id: str,
        skin_type_answers: Dict[str, str],
        concern_ratings: Dict[str, int],
        fitzpatrick_answers: Dict[str, str],
        medical_conditions: List[MedicalCondition] = None,
        lifestyle_factors: List[LifestyleFactors] = None,
        allergies: List[str] = None,
        medications: List[str] = None,
        current_products: List[str] = None,
        treatment_goals: List[str] = None,
        visual_observations: str = "",
        practitioner_notes: str = ""
    ) -> FullClientAssessment:
        """
        Complete an assessment with all gathered data.
        """
        if assessment_id not in self._assessments:
            raise ValueError(f"Assessment not found: {assessment_id}")

        assessment = self._assessments[assessment_id]

        # Determine skin type
        assessment.skin_type = self.determine_skin_type(skin_type_answers)

        # Determine Fitzpatrick type
        assessment.fitzpatrick_type = self.determine_fitzpatrick(fitzpatrick_answers)

        # Analyze concerns
        primary, secondary = self.analyze_concerns(concern_ratings)
        assessment.primary_concerns = primary
        assessment.secondary_concerns = secondary

        # Determine Zone focus
        all_concerns = primary + secondary
        assessment.zone_focus = self.determine_zone_focus(all_concerns)

        # Store other data
        assessment.medical_conditions = medical_conditions or []
        assessment.lifestyle_factors = lifestyle_factors or []
        assessment.allergies = allergies or []
        assessment.medications = medications or []
        assessment.current_products = current_products or []
        assessment.treatment_goals = treatment_goals or []
        assessment.visual_observations = visual_observations
        assessment.practitioner_notes = practitioner_notes

        # Store raw answers
        assessment.answers = SkinAssessmentAnswers(
            morning_skin_feel=skin_type_answers.get("morning_feel", ""),
            pore_visibility=skin_type_answers.get("pore_visibility", ""),
            midday_shine=skin_type_answers.get("midday_shine", ""),
            reaction_to_products=skin_type_answers.get("product_reaction", ""),
            sun_reaction=fitzpatrick_answers.get("sun_reaction", ""),
            tanning_ability=fitzpatrick_answers.get("natural_color", ""),
            fine_lines_concern=concern_ratings.get("ageing", 0),
            pigmentation_concern=concern_ratings.get("pigmentation", 0),
            acne_concern=concern_ratings.get("acne", 0),
            sensitivity_concern=concern_ratings.get("sensitivity", 0),
            texture_concern=concern_ratings.get("texture", 0),
            hydration_concern=concern_ratings.get("hydration", 0),
            dark_circles_concern=concern_ratings.get("eyes", 0)
        )

        # Check for contraindications
        assessment.contraindications = self._check_contraindications(assessment)

        logger.info(f"Completed assessment {assessment_id}")
        return assessment

    def _check_contraindications(self, assessment: FullClientAssessment) -> List[str]:
        """Check for treatment contraindications based on assessment."""
        contraindications = []

        # Pregnancy/breastfeeding
        if MedicalCondition.PREGNANCY in assessment.medical_conditions:
            contraindications.append("Pregnancy - avoid retinoids, high-strength acids, certain essential oils")
        if MedicalCondition.BREASTFEEDING in assessment.medical_conditions:
            contraindications.append("Breastfeeding - avoid retinoids and certain ingredients")

        # Skin conditions
        if MedicalCondition.ROSACEA_DIAGNOSED in assessment.medical_conditions:
            contraindications.append("Rosacea - avoid aggressive treatments, strong acids, heat")

        # Current products that may interact
        if "retinoids" in [p.lower() for p in assessment.current_products]:
            contraindications.append("Currently using retinoids - be cautious with acids and peels")

        # Allergies
        if assessment.allergies:
            contraindications.append(f"Known allergies: {', '.join(assessment.allergies)}")

        return contraindications

    def get_assessment(self, assessment_id: str) -> Optional[FullClientAssessment]:
        """Retrieve an assessment by ID."""
        return self._assessments.get(assessment_id)

    def get_client_assessments(self, client_id: str) -> List[FullClientAssessment]:
        """Get all assessments for a client."""
        return [a for a in self._assessments.values() if a.client_id == client_id]

    def generate_assessment_summary(self, assessment: FullClientAssessment) -> str:
        """Generate a readable assessment summary."""
        zone_names = [z.value.replace("_", "-").title() for z in assessment.zone_focus]

        summary = f"""
═══════════════════════════════════════════════════════════════════════════════
                         RÉGIMA CLIENT SKIN ASSESSMENT
═══════════════════════════════════════════════════════════════════════════════

ASSESSMENT ID: {assessment.assessment_id}
DATE: {assessment.date[:10]}
PRACTITIONER: {assessment.practitioner}

───────────────────────────────────────────────────────────────────────────────
                              CLIENT INFORMATION
───────────────────────────────────────────────────────────────────────────────
Name: {assessment.name}
Email: {assessment.email}
Phone: {assessment.phone or "Not provided"}
DOB: {assessment.date_of_birth or "Not provided"}

───────────────────────────────────────────────────────────────────────────────
                              SKIN ANALYSIS
───────────────────────────────────────────────────────────────────────────────
SKIN TYPE: {assessment.skin_type.value.upper()}
FITZPATRICK TYPE: {assessment.fitzpatrick_type.value.replace("_", " ").title()}

ZONE CONCEPT FOCUS:
{chr(10).join(f"  → {z}" for z in zone_names) if zone_names else "  None identified"}

PRIMARY CONCERNS:
{chr(10).join(f"  • {c.value.replace('_', ' ').title()}" for c in assessment.primary_concerns) if assessment.primary_concerns else "  None identified"}

SECONDARY CONCERNS:
{chr(10).join(f"  • {c.value.replace('_', ' ').title()}" for c in assessment.secondary_concerns) if assessment.secondary_concerns else "  None identified"}

───────────────────────────────────────────────────────────────────────────────
                            HEALTH & LIFESTYLE
───────────────────────────────────────────────────────────────────────────────
MEDICAL CONDITIONS:
{chr(10).join(f"  • {m.value.replace('_', ' ').title()}" for m in assessment.medical_conditions) if assessment.medical_conditions else "  None reported"}

LIFESTYLE FACTORS:
{chr(10).join(f"  • {l.value.replace('_', ' ').title()}" for l in assessment.lifestyle_factors) if assessment.lifestyle_factors else "  None identified"}

CURRENT PRODUCTS:
{chr(10).join(f"  • {p}" for p in assessment.current_products) if assessment.current_products else "  None reported"}

ALLERGIES:
{chr(10).join(f"  • {a}" for a in assessment.allergies) if assessment.allergies else "  None reported"}

MEDICATIONS:
{chr(10).join(f"  • {m}" for m in assessment.medications) if assessment.medications else "  None reported"}

───────────────────────────────────────────────────────────────────────────────
                            TREATMENT GOALS
───────────────────────────────────────────────────────────────────────────────
{chr(10).join(f"  • {g}" for g in assessment.treatment_goals) if assessment.treatment_goals else "  Not specified"}

───────────────────────────────────────────────────────────────────────────────
                         PRACTITIONER OBSERVATIONS
───────────────────────────────────────────────────────────────────────────────
{assessment.visual_observations if assessment.visual_observations else "No observations recorded"}

NOTES:
{assessment.practitioner_notes if assessment.practitioner_notes else "No additional notes"}

───────────────────────────────────────────────────────────────────────────────
                           CONTRAINDICATIONS
───────────────────────────────────────────────────────────────────────────────
{chr(10).join(f"  ⚠️  {c}" for c in assessment.contraindications) if assessment.contraindications else "  None identified"}

═══════════════════════════════════════════════════════════════════════════════
                         ZONE CONCEPT RECOMMENDATION
═══════════════════════════════════════════════════════════════════════════════

Based on this assessment, focus treatment on:
"""

        if ZonePillar.ANTI_INFLAMMATORY in assessment.zone_focus:
            summary += """
ANTI-INFLAMMATORY PILLAR
  The client shows signs of inflammation-related concerns. Prioritize calming,
  soothing products that reduce redness and sensitivity while protecting the
  skin barrier.
"""

        if ZonePillar.ANTI_OXIDANT in assessment.zone_focus:
            summary += """
ANTI-OXIDANT PILLAR
  Environmental protection is key for this client. Focus on products that
  neutralize free radicals, protect against UV and pollution damage, and
  address pigmentation concerns.
"""

        if ZonePillar.REJUVENATION in assessment.zone_focus:
            summary += """
REJUVENATION PILLAR
  Cell renewal and repair are priorities. Include products that stimulate
  collagen production, improve skin texture, and address signs of ageing.
"""

        summary += """
═══════════════════════════════════════════════════════════════════════════════

Next Step: Generate a personalized treatment protocol using the Protocol Builder
           with client ID: """ + assessment.client_id + """

═══════════════════════════════════════════════════════════════════════════════
"""
        return summary

    def generate_protocol_for_assessment(
        self,
        assessment_id: str,
        include_professional: bool = True
    ) -> Tuple[str, str]:
        """
        Generate a treatment protocol from an assessment.

        Returns tuple of (assessment_summary, protocol_summary)
        """
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment not found: {assessment_id}")

        # Generate assessment summary
        assessment_summary = self.generate_assessment_summary(assessment)

        # Convert to client profile and generate protocol
        client_profile = assessment.to_client_profile()
        builder = ProtocolBuilder()
        routine = builder.build_basic_routine(client_profile, include_professional)
        protocol_summary = builder.generate_protocol_summary(client_profile, routine)

        return assessment_summary, protocol_summary


def demo_assessment():
    """Demonstrate the assessment system with a sample client."""
    engine = SkinAssessmentEngine()

    # Create new assessment
    assessment = engine.create_assessment(
        practitioner="Dr. Sarah Chen",
        client_name="Emily Johnson",
        client_email="emily.j@email.com",
        client_phone="555-0123",
        date_of_birth="1985-03-15"
    )

    # Simulate questionnaire answers
    skin_type_answers = {
        "morning_feel": "slightly_oily",
        "pore_visibility": "tzone",
        "midday_shine": "tzone_only",
        "product_reaction": "sometimes",
        "hydration": "sometimes"
    }

    concern_ratings = {
        "ageing": 4,        # High concern
        "pigmentation": 5,  # Very high concern
        "acne": 2,          # Low concern
        "sensitivity": 3,   # Moderate concern
        "texture": 4,       # High concern
        "hydration": 3,     # Moderate concern
        "eyes": 4           # High concern
    }

    fitzpatrick_answers = {
        "sun_reaction": "sometimes_burn",
        "natural_color": "medium"
    }

    # Complete the assessment
    completed = engine.complete_assessment(
        assessment_id=assessment.assessment_id,
        skin_type_answers=skin_type_answers,
        concern_ratings=concern_ratings,
        fitzpatrick_answers=fitzpatrick_answers,
        medical_conditions=[],
        lifestyle_factors=[
            LifestyleFactors.HIGH_STRESS,
            LifestyleFactors.SCREEN_TIME
        ],
        allergies=[],
        medications=[],
        current_products=["Basic cleanser", "Moisturizer", "Occasional sunscreen"],
        treatment_goals=[
            "Even out skin tone",
            "Reduce fine lines",
            "Brighter complexion",
            "Address dark circles"
        ],
        visual_observations="Visible pigmentation on cheeks, fine lines around eyes, combination T-zone",
        practitioner_notes="Good candidate for pigmentation treatment protocol. Consider Power Peel series."
    )

    # Generate outputs
    assessment_summary, protocol_summary = engine.generate_protocol_for_assessment(
        assessment.assessment_id,
        include_professional=True
    )

    # Print results
    print(assessment_summary)
    print("\n" + "=" * 80 + "\n")
    print(protocol_summary)

    # Save
    engine.save_assessments()

    # Save summaries to files
    output_path = Path(__file__).parent.parent / "outputs"
    output_path.mkdir(exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")

    with open(output_path / f"assessment_{assessment.assessment_id}_{date_str}.txt", "w") as f:
        f.write(assessment_summary)

    with open(output_path / f"protocol_{assessment.client_id}_{date_str}.txt", "w") as f:
        f.write(protocol_summary)

    print(f"\nFiles saved to outputs/")
    print(f"  - assessment_{assessment.assessment_id}_{date_str}.txt")
    print(f"  - protocol_{assessment.client_id}_{date_str}.txt")


if __name__ == "__main__":
    demo_assessment()
