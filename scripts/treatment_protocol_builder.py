#!/usr/bin/env python3
"""
RégimA Treatment Protocol Builder

A practical tool for skincare practitioners to:
1. Assess client skin concerns
2. Map concerns to Zone Concept pillars (Anti-Inflammatory, Anti-Oxidant, Rejuvenation)
3. Generate personalized treatment protocols with specific product recommendations

This is the agent-arena-relation in action:
- Agent: Practitioner + RégimA products
- Arena: Client's skin, concerns, goals
- Relation: Zone Concept framework mediating the match
"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ZonePillar(Enum):
    """The three pillars of the RégimA Zone Concept."""
    ANTI_INFLAMMATORY = "anti_inflammatory"
    ANTI_OXIDANT = "anti_oxidant"
    REJUVENATION = "rejuvenation"


class SkinType(Enum):
    """Basic skin types."""
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    NORMAL = "normal"


class SkinConcern(Enum):
    """Common skin concerns that clients present with."""
    # Inflammatory concerns
    ACNE = "acne"
    REDNESS = "redness"
    ROSACEA = "rosacea"
    SENSITIVITY = "sensitivity"
    IRRITATION = "irritation"
    ECZEMA = "eczema"
    PSORIASIS = "psoriasis"

    # Oxidative/Environmental concerns
    SUN_DAMAGE = "sun_damage"
    PIGMENTATION = "pigmentation"
    DULLNESS = "dullness"
    UNEVEN_TONE = "uneven_tone"
    ENVIRONMENTAL_STRESS = "environmental_stress"

    # Ageing/Rejuvenation concerns
    FINE_LINES = "fine_lines"
    WRINKLES = "wrinkles"
    LOSS_OF_FIRMNESS = "loss_of_firmness"
    SAGGING = "sagging"
    CREPEY_SKIN = "crepey_skin"
    DARK_CIRCLES = "dark_circles"
    PUFFINESS = "puffiness"

    # Texture concerns
    ENLARGED_PORES = "enlarged_pores"
    ROUGH_TEXTURE = "rough_texture"
    SCARRING = "scarring"
    STRETCH_MARKS = "stretch_marks"

    # Hydration
    DEHYDRATION = "dehydration"
    DRYNESS = "dryness"


class ProductCategory(Enum):
    """Product categories in the RégimA range."""
    CLEANSER = "cleanser"
    EYE_CARE = "eye_care"
    SERUM = "serum"
    DAY_CARE = "day_care"
    NIGHT_CARE = "night_care"
    SUNSCREEN = "sunscreen"
    TREATMENT = "treatment"
    MASQUE = "masque"
    PEEL = "peel"
    BODY = "body"


@dataclass
class Product:
    """Represents a RégimA product."""
    code: str
    name: str
    category: ProductCategory
    zone_pillars: List[ZonePillar]
    concerns_addressed: List[SkinConcern]
    skin_types: List[SkinType]
    key_benefits: List[str]
    key_ingredients: List[str]
    usage: str
    contraindications: List[str] = field(default_factory=list)
    professional_only: bool = False

    def matches_concern(self, concern: SkinConcern) -> bool:
        return concern in self.concerns_addressed

    def matches_skin_type(self, skin_type: SkinType) -> bool:
        return skin_type in self.skin_types or SkinType.NORMAL in self.skin_types


@dataclass
class ClientProfile:
    """Client intake information."""
    client_id: str
    name: str
    date_of_birth: Optional[str] = None
    skin_type: SkinType = SkinType.NORMAL
    concerns: List[SkinConcern] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    current_products: List[str] = field(default_factory=list)
    medical_conditions: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ProtocolStep:
    """A step in a treatment protocol."""
    order: int
    product: Product
    frequency: str  # "AM", "PM", "AM+PM", "weekly", "as needed"
    application_notes: str
    zone_rationale: str  # Why this product for this concern


@dataclass
class TreatmentProtocol:
    """A complete treatment protocol for a client."""
    protocol_id: str
    client_id: str
    created_at: str
    practitioner: str
    primary_concerns: List[SkinConcern]
    zone_focus: List[ZonePillar]
    steps: List[ProtocolStep]
    home_care: List[ProtocolStep]
    professional_treatments: List[ProtocolStep]
    review_date: str
    notes: str = ""


# =============================================================================
# Product Database - Real RégimA Products from the manual
# =============================================================================

PRODUCT_DATABASE: Dict[str, Product] = {
    # Cleansers
    "DZ-CLNS": Product(
        code="DZ-CLNS",
        name="Derma Zest Cleansing + Toning Gel",
        category=ProductCategory.CLEANSER,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY, ZonePillar.ANTI_OXIDANT],
        concerns_addressed=[
            SkinConcern.ACNE, SkinConcern.ENLARGED_PORES,
            SkinConcern.SENSITIVITY, SkinConcern.IRRITATION
        ],
        skin_types=[SkinType.OILY, SkinType.COMBINATION, SkinType.SENSITIVE],
        key_benefits=[
            "Deep cleansing", "Natural astringent", "Tightens pores",
            "Anti-bacterial", "Soothing and calming"
        ],
        key_ingredients=["Ruby Star Grapefruit", "Bisabolol", "Centella Asiatica"],
        usage="AM and PM: Wet hands, face and neck, massage gently for one minute, rinse thoroughly"
    ),

    "DD-CLNS": Product(
        code="DD-CLNS",
        name="Derma Deep Rich Creamy Cleanser",
        category=ProductCategory.CLEANSER,
        zone_pillars=[ZonePillar.ANTI_OXIDANT, ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.DRYNESS, SkinConcern.DEHYDRATION, SkinConcern.FINE_LINES,
            SkinConcern.ECZEMA, SkinConcern.PSORIASIS
        ],
        skin_types=[SkinType.DRY, SkinType.SENSITIVE, SkinType.NORMAL],
        key_benefits=[
            "Deep hydration", "Collagen synthesis stimulation",
            "Rich in vitamins A, B, C, D", "Healing properties"
        ],
        key_ingredients=["Rosehip Oil", "Blackcurrant Seed Oil", "Soy Bean Oil"],
        usage="AM and PM: Wet hands, face and neck, massage gently for one minute, rinse thoroughly"
    ),

    # Eye Care
    "UEF-EYE": Product(
        code="UEF-EYE",
        name="New Expression-365 Under Eye Fix",
        category=ProductCategory.EYE_CARE,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY, ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.WRINKLES, SkinConcern.DARK_CIRCLES, SkinConcern.PUFFINESS,
            SkinConcern.FINE_LINES, SkinConcern.LOSS_OF_FIRMNESS
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.SENSITIVE, SkinType.COMBINATION, SkinType.OILY],
        key_benefits=[
            "Reduces crow's feet", "Fades dark circles", "Reduces puffiness",
            "Immediate lifting effect", "Myo-relaxing action"
        ],
        key_ingredients=["Matrixyl 3000", "Hesperidin Methyl Chalcone", "Dipeptide-2"],
        usage="AM and PM: Apply one pump to under eye area, crow's feet, and frown lines. Do not apply to upper eyelids."
    ),

    "EOS-EYE": Product(
        code="EOS-EYE",
        name="Eye Opener Serum - Revolution-Eyz",
        category=ProductCategory.EYE_CARE,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY, ZonePillar.ANTI_OXIDANT, ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.CREPEY_SKIN, SkinConcern.FINE_LINES, SkinConcern.WRINKLES,
            SkinConcern.DARK_CIRCLES, SkinConcern.PUFFINESS, SkinConcern.LOSS_OF_FIRMNESS
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.SENSITIVE, SkinType.COMBINATION, SkinType.OILY],
        key_benefits=[
            "Deeply hydrating", "Firms and tightens", "Reduces fine lines",
            "Improves crepey upper eyelids", "Anti-ageing"
        ],
        key_ingredients=["Giant Kelp Extract", "Aquacacteen (Cactus)", "White Lily Extract"],
        usage="AM and PM: Apply to upper eyelids and whole eye area before Under Eye Fix"
    ),

    # Day Care with Beta-Endorphin
    "DRB-DAY": Product(
        code="DRB-DAY",
        name="Daily Radiant Boost + ßeta-Endorphin Stimulator",
        category=ProductCategory.DAY_CARE,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY, ZonePillar.ANTI_OXIDANT],
        concerns_addressed=[
            SkinConcern.DULLNESS, SkinConcern.UNEVEN_TONE, SkinConcern.SENSITIVITY,
            SkinConcern.ENVIRONMENTAL_STRESS, SkinConcern.DEHYDRATION
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION],
        key_benefits=[
            "Radiance boosting", "Beta-endorphin stimulation for wellbeing",
            "Anti-inflammatory", "Environmental protection"
        ],
        key_ingredients=["Beta-Endorphin Stimulator Complex"],
        usage="AM: Apply after serums, before sunscreen"
    ),

    "DIS-DAY": Product(
        code="DIS-DAY",
        name="Daily Intelligent Sebum-Solver + ßeta-Endorphin Stimulator",
        category=ProductCategory.DAY_CARE,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY],
        concerns_addressed=[
            SkinConcern.ACNE, SkinConcern.ENLARGED_PORES, SkinConcern.ENLARGED_PORES
        ],
        skin_types=[SkinType.OILY, SkinType.COMBINATION],
        key_benefits=[
            "Sebum regulation", "Pore minimizing",
            "Beta-endorphin stimulation", "Oil control"
        ],
        key_ingredients=["Beta-Endorphin Stimulator Complex", "Sebum Regulators"],
        usage="AM: Apply after serums, before sunscreen"
    ),

    "DUD-DAY": Product(
        code="DUD-DAY",
        name="Daily Ultra Defence + ßeta-Endorphin Stimulator",
        category=ProductCategory.DAY_CARE,
        zone_pillars=[ZonePillar.ANTI_OXIDANT, ZonePillar.ANTI_INFLAMMATORY],
        concerns_addressed=[
            SkinConcern.ENVIRONMENTAL_STRESS, SkinConcern.SUN_DAMAGE,
            SkinConcern.SENSITIVITY, SkinConcern.DULLNESS
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.SENSITIVE],
        key_benefits=[
            "Environmental protection", "Ultra defence",
            "Beta-endorphin stimulation", "Anti-oxidant protection"
        ],
        key_ingredients=["Beta-Endorphin Stimulator Complex", "Antioxidant Complex"],
        usage="AM: Apply after serums, before sunscreen"
    ),

    # Serums and Treatments
    "AIA-SER": Product(
        code="AIA-SER",
        name="Anti-Inflamm-Ageing",
        category=ProductCategory.SERUM,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY, ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.REDNESS, SkinConcern.SENSITIVITY, SkinConcern.ROSACEA,
            SkinConcern.IRRITATION, SkinConcern.FINE_LINES, SkinConcern.WRINKLES
        ],
        skin_types=[SkinType.SENSITIVE, SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION],
        key_benefits=[
            "Reduces inflammation", "Anti-ageing", "Calming",
            "Suitable for rosacea-prone skin"
        ],
        key_ingredients=["Anti-inflammatory Complex"],
        usage="AM and/or PM: Apply after cleansing, before moisturizer"
    ),

    "EGX-SER": Product(
        code="EGX-SER",
        name="Epi-Genes Xpress",
        category=ProductCategory.SERUM,
        zone_pillars=[ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.FINE_LINES, SkinConcern.WRINKLES, SkinConcern.LOSS_OF_FIRMNESS,
            SkinConcern.SAGGING
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION, SkinType.OILY],
        key_benefits=[
            "Epigenetic anti-ageing", "Gene expression optimization",
            "Firming", "Rejuvenating"
        ],
        key_ingredients=["Epigenetic Complex"],
        usage="AM and/or PM: Apply after cleansing, before moisturizer"
    ),

    "SSH-SER": Product(
        code="SSH-SER",
        name="Super Smoother Dual Hyaluronic Action",
        category=ProductCategory.SERUM,
        zone_pillars=[ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.DEHYDRATION, SkinConcern.FINE_LINES, SkinConcern.ROUGH_TEXTURE,
            SkinConcern.DRYNESS
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION, SkinType.SENSITIVE],
        key_benefits=[
            "Dual-weight hyaluronic acid", "Deep hydration",
            "Smoothing", "Plumping"
        ],
        key_ingredients=["High and Low Molecular Weight Hyaluronic Acid"],
        usage="AM and PM: Apply after cleansing, before other serums or moisturizer"
    ),

    "PP-SER": Product(
        code="PP-SER",
        name="Pigment Perfector",
        category=ProductCategory.SERUM,
        zone_pillars=[ZonePillar.ANTI_OXIDANT, ZonePillar.ANTI_INFLAMMATORY],
        concerns_addressed=[
            SkinConcern.PIGMENTATION, SkinConcern.UNEVEN_TONE, SkinConcern.SUN_DAMAGE,
            SkinConcern.DARK_CIRCLES
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION, SkinType.OILY],
        key_benefits=[
            "Brightening", "Pigmentation correction",
            "Even skin tone", "Anti-oxidant"
        ],
        key_ingredients=["Pigment Correcting Complex"],
        usage="AM and/or PM: Apply to areas of concern"
    ),

    "AAR-SER": Product(
        code="AAR-SER",
        name="Acne Attack Rescue Serum",
        category=ProductCategory.SERUM,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY],
        concerns_addressed=[
            SkinConcern.ACNE, SkinConcern.ENLARGED_PORES,
            SkinConcern.REDNESS
        ],
        skin_types=[SkinType.OILY, SkinType.COMBINATION],
        key_benefits=[
            "Acne treatment", "Sebum control",
            "Anti-bacterial", "Anti-inflammatory"
        ],
        key_ingredients=["Acne-Fighting Complex"],
        usage="AM and PM: Apply to affected areas"
    ),

    "OQ-OIL": Product(
        code="OQ-OIL",
        name="On Q Quenching Facial Oil",
        category=ProductCategory.SERUM,
        zone_pillars=[ZonePillar.ANTI_OXIDANT, ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.DRYNESS, SkinConcern.DEHYDRATION, SkinConcern.FINE_LINES,
            SkinConcern.DULLNESS
        ],
        skin_types=[SkinType.DRY, SkinType.NORMAL, SkinType.COMBINATION],
        key_benefits=[
            "Deep nourishment", "Quenching hydration",
            "Anti-oxidant rich", "Radiance boosting"
        ],
        key_ingredients=["Nourishing Oil Blend"],
        usage="PM: Apply as final step or mix with night cream"
    ),

    # Night Care
    "ARN-NGT": Product(
        code="ARN-NGT",
        name="Age Reversal Night Complex",
        category=ProductCategory.NIGHT_CARE,
        zone_pillars=[ZonePillar.REJUVENATION, ZonePillar.ANTI_OXIDANT],
        concerns_addressed=[
            SkinConcern.WRINKLES, SkinConcern.FINE_LINES, SkinConcern.LOSS_OF_FIRMNESS,
            SkinConcern.SAGGING, SkinConcern.DULLNESS
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION],
        key_benefits=[
            "Age reversal technology", "Overnight renewal",
            "Firming", "Anti-wrinkle"
        ],
        key_ingredients=["Age Reversal Complex"],
        usage="PM: Apply after serums as final step"
    ),

    "OHI-NGT": Product(
        code="OHI-NGT",
        name="Omega High Impact Night Complex",
        category=ProductCategory.NIGHT_CARE,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY, ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.DRYNESS, SkinConcern.DEHYDRATION, SkinConcern.FINE_LINES,
            SkinConcern.SENSITIVITY, SkinConcern.ECZEMA
        ],
        skin_types=[SkinType.DRY, SkinType.SENSITIVE, SkinType.NORMAL],
        key_benefits=[
            "Omega fatty acid rich", "Intensive nourishment",
            "Barrier repair", "Anti-inflammatory"
        ],
        key_ingredients=["Omega 3, 6, 9 Complex"],
        usage="PM: Apply after serums as final step"
    ),

    "RJD-NGT": Product(
        code="RJD-NGT",
        name="Rejuvoderm Night Maintenance",
        category=ProductCategory.NIGHT_CARE,
        zone_pillars=[ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.FINE_LINES, SkinConcern.WRINKLES, SkinConcern.ROUGH_TEXTURE,
            SkinConcern.DULLNESS
        ],
        skin_types=[SkinType.NORMAL, SkinType.COMBINATION, SkinType.OILY],
        key_benefits=[
            "Cell renewal", "Skin maintenance",
            "Texture improvement", "Anti-ageing"
        ],
        key_ingredients=["Rejuvenation Complex"],
        usage="PM: Apply after serums as final step"
    ),

    # Sunscreen
    "SSC-SUN": Product(
        code="SSC-SUN",
        name="Sunscreen Complex",
        category=ProductCategory.SUNSCREEN,
        zone_pillars=[ZonePillar.ANTI_OXIDANT],
        concerns_addressed=[
            SkinConcern.SUN_DAMAGE, SkinConcern.PIGMENTATION,
            SkinConcern.ENVIRONMENTAL_STRESS
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION, SkinType.OILY, SkinType.SENSITIVE],
        key_benefits=[
            "Broad spectrum protection", "Anti-oxidant enriched",
            "Daily protection", "Prevents sun damage"
        ],
        key_ingredients=["UV Filters", "Antioxidant Complex"],
        usage="AM: Apply as final step, reapply every 2 hours when exposed"
    ),

    # Professional Treatments
    "PP30-TRT": Product(
        code="PP30-TRT",
        name="Power Peel 30",
        category=ProductCategory.PEEL,
        zone_pillars=[ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.ROUGH_TEXTURE, SkinConcern.FINE_LINES, SkinConcern.PIGMENTATION,
            SkinConcern.ACNE, SkinConcern.SCARRING, SkinConcern.DULLNESS
        ],
        skin_types=[SkinType.NORMAL, SkinType.OILY, SkinType.COMBINATION],
        key_benefits=[
            "Professional resurfacing", "Cell turnover acceleration",
            "Texture improvement", "Pigmentation reduction"
        ],
        key_ingredients=["30% Acid Complex"],
        usage="Professional use only: Apply according to protocol",
        professional_only=True,
        contraindications=["Active inflammation", "Broken skin", "Recent sun exposure"]
    ),

    "PP50-TRT": Product(
        code="PP50-TRT",
        name="Power Peel 50",
        category=ProductCategory.PEEL,
        zone_pillars=[ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.ROUGH_TEXTURE, SkinConcern.WRINKLES, SkinConcern.PIGMENTATION,
            SkinConcern.SCARRING, SkinConcern.ACNE
        ],
        skin_types=[SkinType.NORMAL, SkinType.OILY],
        key_benefits=[
            "Intensive professional resurfacing", "Deep renewal",
            "Significant texture improvement"
        ],
        key_ingredients=["50% Acid Complex"],
        usage="Professional use only: Apply according to protocol",
        professional_only=True,
        contraindications=["Active inflammation", "Broken skin", "Recent sun exposure", "Sensitive skin"]
    ),

    "T5R-TRT": Product(
        code="T5R-TRT",
        name="Techno 5 Resurfacer",
        category=ProductCategory.TREATMENT,
        zone_pillars=[ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.ROUGH_TEXTURE, SkinConcern.FINE_LINES, SkinConcern.ENLARGED_PORES,
            SkinConcern.DULLNESS
        ],
        skin_types=[SkinType.NORMAL, SkinType.OILY, SkinType.COMBINATION],
        key_benefits=[
            "5-action resurfacing", "Pore refinement",
            "Texture smoothing", "Brightening"
        ],
        key_ingredients=["5-Technology Complex"],
        usage="PM: 2-3 times weekly, or as directed"
    ),

    "QEC-TRT": Product(
        code="QEC-TRT",
        name="Quantum Elastin-Collagen Revival",
        category=ProductCategory.TREATMENT,
        zone_pillars=[ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.LOSS_OF_FIRMNESS, SkinConcern.SAGGING, SkinConcern.WRINKLES,
            SkinConcern.FINE_LINES
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION],
        key_benefits=[
            "Elastin revival", "Collagen boosting",
            "Firming", "Lifting"
        ],
        key_ingredients=["Elastin-Collagen Complex"],
        usage="PM: Apply 2-3 times weekly as intensive treatment"
    ),

    # Masques
    "RRM-MSK": Product(
        code="RRM-MSK",
        name="Rapid-Rejuvo Masque",
        category=ProductCategory.MASQUE,
        zone_pillars=[ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.DULLNESS, SkinConcern.FINE_LINES, SkinConcern.ROUGH_TEXTURE,
            SkinConcern.DEHYDRATION
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION],
        key_benefits=[
            "Rapid rejuvenation", "Instant glow",
            "Hydration boost", "Smoothing"
        ],
        key_ingredients=["Rejuvenation Complex"],
        usage="Weekly: Apply for 15-20 minutes, rinse"
    ),

    "AAP-MSK": Product(
        code="AAP-MSK",
        name="Acne Attack Pro-Masque",
        category=ProductCategory.MASQUE,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY],
        concerns_addressed=[
            SkinConcern.ACNE, SkinConcern.ENLARGED_PORES,
            SkinConcern.REDNESS
        ],
        skin_types=[SkinType.OILY, SkinType.COMBINATION],
        key_benefits=[
            "Acne control", "Deep cleansing",
            "Oil absorption", "Pore purifying"
        ],
        key_ingredients=["Acne Control Complex"],
        usage="Weekly or as needed: Apply for 15-20 minutes, rinse",
        professional_only=True
    ),

    # Scar Treatment
    "SRF-TRT": Product(
        code="SRF-TRT",
        name="Scar Repair Forté + Anti-Stretch Complex",
        category=ProductCategory.TREATMENT,
        zone_pillars=[ZonePillar.REJUVENATION, ZonePillar.ANTI_INFLAMMATORY],
        concerns_addressed=[
            SkinConcern.SCARRING, SkinConcern.STRETCH_MARKS
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION, SkinType.OILY, SkinType.SENSITIVE],
        key_benefits=[
            "Scar reduction", "Stretch mark improvement",
            "Tissue repair", "Skin regeneration"
        ],
        key_ingredients=["Scar Repair Complex"],
        usage="Apply to affected areas twice daily"
    ),

    "LAR-TRT": Product(
        code="LAR-TRT",
        name="Laser Azu-Repair - The Blue Gel",
        category=ProductCategory.TREATMENT,
        zone_pillars=[ZonePillar.ANTI_INFLAMMATORY, ZonePillar.REJUVENATION],
        concerns_addressed=[
            SkinConcern.IRRITATION, SkinConcern.REDNESS, SkinConcern.SENSITIVITY
        ],
        skin_types=[SkinType.SENSITIVE, SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION],
        key_benefits=[
            "Post-procedure healing", "Calming",
            "Repair acceleration", "Anti-inflammatory"
        ],
        key_ingredients=["Azulene", "Healing Complex"],
        usage="Apply to treated areas as needed for healing"
    ),

    # Neck & Body
    "NBR-TRT": Product(
        code="NBR-TRT",
        name="Neck + Breast Refining Complex",
        category=ProductCategory.BODY,
        zone_pillars=[ZonePillar.REJUVENATION, ZonePillar.ANTI_OXIDANT],
        concerns_addressed=[
            SkinConcern.LOSS_OF_FIRMNESS, SkinConcern.SAGGING, SkinConcern.CREPEY_SKIN,
            SkinConcern.FINE_LINES
        ],
        skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION],
        key_benefits=[
            "Neck firming", "Décolletage care",
            "Lifting", "Tightening"
        ],
        key_ingredients=["Firming Complex"],
        usage="AM and PM: Apply to neck and décolletage area"
    ),
}


# =============================================================================
# Concern to Zone Mapping
# =============================================================================

CONCERN_ZONE_MAP: Dict[SkinConcern, List[ZonePillar]] = {
    # Inflammatory concerns → Anti-Inflammatory
    SkinConcern.ACNE: [ZonePillar.ANTI_INFLAMMATORY],
    SkinConcern.REDNESS: [ZonePillar.ANTI_INFLAMMATORY],
    SkinConcern.ROSACEA: [ZonePillar.ANTI_INFLAMMATORY],
    SkinConcern.SENSITIVITY: [ZonePillar.ANTI_INFLAMMATORY],
    SkinConcern.IRRITATION: [ZonePillar.ANTI_INFLAMMATORY],
    SkinConcern.ECZEMA: [ZonePillar.ANTI_INFLAMMATORY],
    SkinConcern.PSORIASIS: [ZonePillar.ANTI_INFLAMMATORY],

    # Oxidative concerns → Anti-Oxidant
    SkinConcern.SUN_DAMAGE: [ZonePillar.ANTI_OXIDANT],
    SkinConcern.PIGMENTATION: [ZonePillar.ANTI_OXIDANT, ZonePillar.ANTI_INFLAMMATORY],
    SkinConcern.DULLNESS: [ZonePillar.ANTI_OXIDANT, ZonePillar.REJUVENATION],
    SkinConcern.UNEVEN_TONE: [ZonePillar.ANTI_OXIDANT],
    SkinConcern.ENVIRONMENTAL_STRESS: [ZonePillar.ANTI_OXIDANT],

    # Ageing concerns → Rejuvenation
    SkinConcern.FINE_LINES: [ZonePillar.REJUVENATION],
    SkinConcern.WRINKLES: [ZonePillar.REJUVENATION],
    SkinConcern.LOSS_OF_FIRMNESS: [ZonePillar.REJUVENATION],
    SkinConcern.SAGGING: [ZonePillar.REJUVENATION],
    SkinConcern.CREPEY_SKIN: [ZonePillar.REJUVENATION],
    SkinConcern.DARK_CIRCLES: [ZonePillar.ANTI_INFLAMMATORY, ZonePillar.REJUVENATION],
    SkinConcern.PUFFINESS: [ZonePillar.ANTI_INFLAMMATORY],

    # Texture concerns → Mixed
    SkinConcern.ENLARGED_PORES: [ZonePillar.ANTI_INFLAMMATORY, ZonePillar.REJUVENATION],
    SkinConcern.ROUGH_TEXTURE: [ZonePillar.REJUVENATION],
    SkinConcern.SCARRING: [ZonePillar.REJUVENATION, ZonePillar.ANTI_INFLAMMATORY],
    SkinConcern.STRETCH_MARKS: [ZonePillar.REJUVENATION],

    # Hydration → Can involve all zones
    SkinConcern.DEHYDRATION: [ZonePillar.ANTI_OXIDANT, ZonePillar.REJUVENATION],
    SkinConcern.DRYNESS: [ZonePillar.ANTI_OXIDANT, ZonePillar.REJUVENATION],
}


# =============================================================================
# Protocol Builder
# =============================================================================

class ProtocolBuilder:
    """
    Builds treatment protocols by matching client concerns to Zone Concept pillars
    and recommending appropriate products.
    """

    def __init__(self):
        self.products = PRODUCT_DATABASE
        self.concern_zones = CONCERN_ZONE_MAP

    def analyze_concerns(self, concerns: List[SkinConcern]) -> Dict[ZonePillar, int]:
        """Analyze which Zone pillars are most relevant for given concerns."""
        pillar_weights: Dict[ZonePillar, int] = {p: 0 for p in ZonePillar}

        for concern in concerns:
            if concern in self.concern_zones:
                for pillar in self.concern_zones[concern]:
                    pillar_weights[pillar] += 1

        return pillar_weights

    def get_primary_zones(self, concerns: List[SkinConcern]) -> List[ZonePillar]:
        """Get the primary Zone pillars to focus on."""
        weights = self.analyze_concerns(concerns)
        # Sort by weight, return pillars with weight > 0
        sorted_pillars = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        return [p for p, w in sorted_pillars if w > 0]

    def find_products(
        self,
        concerns: List[SkinConcern],
        skin_type: SkinType,
        category: Optional[ProductCategory] = None,
        exclude_professional: bool = True
    ) -> List[Product]:
        """Find products matching concerns and skin type."""
        matches = []

        for product in self.products.values():
            # Skip professional-only if excluded
            if exclude_professional and product.professional_only:
                continue

            # Filter by category if specified
            if category and product.category != category:
                continue

            # Check skin type compatibility
            if not product.matches_skin_type(skin_type):
                continue

            # Check if addresses any concerns
            concern_match = any(product.matches_concern(c) for c in concerns)
            if concern_match:
                matches.append(product)

        return matches

    def build_basic_routine(
        self,
        client: ClientProfile,
        include_professional: bool = False
    ) -> Dict[str, List[Product]]:
        """Build a basic AM/PM routine for a client."""
        routine = {
            "am": [],
            "pm": [],
            "weekly": [],
            "professional": []
        }

        concerns = client.concerns
        skin_type = client.skin_type

        # Step 1: Cleanser
        cleansers = self.find_products(concerns, skin_type, ProductCategory.CLEANSER)
        if cleansers:
            routine["am"].append(cleansers[0])
            routine["pm"].append(cleansers[0])

        # Step 2: Eye Care (if eye concerns)
        eye_concerns = [c for c in concerns if c in [
            SkinConcern.DARK_CIRCLES, SkinConcern.PUFFINESS,
            SkinConcern.CREPEY_SKIN, SkinConcern.FINE_LINES
        ]]
        if eye_concerns:
            eye_products = self.find_products(eye_concerns, skin_type, ProductCategory.EYE_CARE)
            for ep in eye_products[:2]:  # Max 2 eye products
                routine["am"].append(ep)
                routine["pm"].append(ep)

        # Step 3: Serums (based on primary concerns)
        serums = self.find_products(concerns, skin_type, ProductCategory.SERUM)
        for serum in serums[:2]:  # Max 2 serums
            routine["am"].append(serum)
            routine["pm"].append(serum)

        # Step 4: Day Care
        day_products = self.find_products(concerns, skin_type, ProductCategory.DAY_CARE)
        if day_products:
            routine["am"].append(day_products[0])

        # Step 5: Sunscreen (always for AM)
        sunscreens = self.find_products(concerns, skin_type, ProductCategory.SUNSCREEN)
        if sunscreens:
            routine["am"].append(sunscreens[0])

        # Step 6: Night Care
        night_products = self.find_products(concerns, skin_type, ProductCategory.NIGHT_CARE)
        if night_products:
            routine["pm"].append(night_products[0])

        # Step 7: Weekly treatments
        masques = self.find_products(concerns, skin_type, ProductCategory.MASQUE, exclude_professional=True)
        routine["weekly"].extend(masques[:1])

        treatments = self.find_products(concerns, skin_type, ProductCategory.TREATMENT, exclude_professional=True)
        routine["weekly"].extend(treatments[:1])

        # Step 8: Professional treatments (if requested)
        if include_professional:
            pro_treatments = self.find_products(concerns, skin_type, exclude_professional=False)
            routine["professional"] = [p for p in pro_treatments if p.professional_only][:3]

        return routine

    def generate_protocol_summary(
        self,
        client: ClientProfile,
        routine: Dict[str, List[Product]]
    ) -> str:
        """Generate a readable protocol summary."""
        zones = self.get_primary_zones(client.concerns)
        zone_names = [z.value.replace("_", "-").title() for z in zones]

        summary = f"""
═══════════════════════════════════════════════════════════════
                    RÉGIMA TREATMENT PROTOCOL
═══════════════════════════════════════════════════════════════

CLIENT: {client.name}
SKIN TYPE: {client.skin_type.value.title()}
DATE: {datetime.now().strftime("%Y-%m-%d")}

───────────────────────────────────────────────────────────────
                      ZONE CONCEPT FOCUS
───────────────────────────────────────────────────────────────
Primary Pillars: {", ".join(zone_names)}

Concerns Addressed:
{chr(10).join(f"  • {c.value.replace('_', ' ').title()}" for c in client.concerns)}

───────────────────────────────────────────────────────────────
                       MORNING ROUTINE
───────────────────────────────────────────────────────────────
"""
        for i, product in enumerate(routine["am"], 1):
            summary += f"{i}. {product.name}\n"
            summary += f"   → {product.usage}\n\n"

        summary += """───────────────────────────────────────────────────────────────
                       EVENING ROUTINE
───────────────────────────────────────────────────────────────
"""
        for i, product in enumerate(routine["pm"], 1):
            summary += f"{i}. {product.name}\n"
            summary += f"   → {product.usage}\n\n"

        if routine["weekly"]:
            summary += """───────────────────────────────────────────────────────────────
                      WEEKLY TREATMENTS
───────────────────────────────────────────────────────────────
"""
            for product in routine["weekly"]:
                summary += f"• {product.name}\n"
                summary += f"  → {product.usage}\n\n"

        if routine.get("professional"):
            summary += """───────────────────────────────────────────────────────────────
                   PROFESSIONAL TREATMENTS
───────────────────────────────────────────────────────────────
"""
            for product in routine["professional"]:
                summary += f"• {product.name}\n"
                summary += f"  → {', '.join(product.key_benefits)}\n\n"

        summary += """═══════════════════════════════════════════════════════════════
                    ZONE CONCEPT EXPLAINED
═══════════════════════════════════════════════════════════════

The RégimA Zone Concept addresses the two main causes of skin
ageing: inflammation and free radical damage.

• ANTI-INFLAMMATORY: Reduces cellular damage from inflammation
• ANTI-OXIDANT: Protects against environmental oxidative stress
• REJUVENATION: Promotes healthy cell renewal and repair

By bringing your skin "into the Zone" of optimal health, we
address not just symptoms but underlying causes.

═══════════════════════════════════════════════════════════════
"""
        return summary


def main():
    """Demo the protocol builder."""
    builder = ProtocolBuilder()

    # Example client
    client = ClientProfile(
        client_id="CLI-001",
        name="Jane Smith",
        skin_type=SkinType.COMBINATION,
        concerns=[
            SkinConcern.FINE_LINES,
            SkinConcern.PIGMENTATION,
            SkinConcern.DEHYDRATION,
            SkinConcern.DULLNESS
        ],
        goals=["Brighter skin", "Reduce fine lines", "Even skin tone"]
    )

    # Build routine
    routine = builder.build_basic_routine(client, include_professional=True)

    # Generate summary
    summary = builder.generate_protocol_summary(client, routine)
    print(summary)

    # Save to file
    output_path = Path(__file__).parent.parent / "outputs"
    output_path.mkdir(exist_ok=True)

    with open(output_path / f"protocol_{client.client_id}_{datetime.now().strftime('%Y%m%d')}.txt", "w") as f:
        f.write(summary)

    print(f"\nProtocol saved to outputs/protocol_{client.client_id}_{datetime.now().strftime('%Y%m%d')}.txt")


if __name__ == "__main__":
    main()
