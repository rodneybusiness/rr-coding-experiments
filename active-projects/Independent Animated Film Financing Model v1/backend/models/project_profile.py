"""
Project Profile Models - Project specifications and parameters

This module defines the characteristics of an animated film/series project.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class ProjectType(str, Enum):
    """Type of animated project"""
    FEATURE_FILM = "feature_film"
    SHORT_FILM = "short_film"
    TV_SERIES = "tv_series"
    LIMITED_SERIES = "limited_series"
    SPECIAL = "special"


class AnimationTechnique(str, Enum):
    """Primary animation technique"""
    CGI_3D = "cgi_3d"
    TRADITIONAL_2D = "traditional_2d"
    STOP_MOTION = "stop_motion"
    HYBRID = "hybrid"
    REAL_TIME = "real_time"  # e.g., Unreal Engine


class TargetAudience(str, Enum):
    """Primary target demographic"""
    PRESCHOOL = "preschool"  # 2-5
    KIDS = "kids"  # 6-11
    FAMILY = "family"  # All ages
    TEEN_YOUNG_ADULT = "teen_young_adult"  # 12-25
    ADULT = "adult"  # 18+


class ProductionJurisdiction(BaseModel):
    """Details about a production jurisdiction"""

    country: str = Field(..., description="Country name")
    state_province: Optional[str] = Field(default=None, description="State/Province if applicable")

    # Spend allocation
    estimated_spend_percentage: Decimal = Field(..., ge=0, le=100, description="% of budget spent here")
    estimated_spend_amount: Optional[Decimal] = Field(default=None, description="Dollar amount spent here")

    # Labor
    estimated_local_labor_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    # Facilities
    studio_partner: Optional[str] = Field(default=None, description="Production studio/facility name")
    is_service_production: bool = Field(default=False, description="Service deal vs. official co-production")

    # Incentives
    applicable_incentive_policies: List[str] = Field(default_factory=list, description="List of policy_ids")


class DevelopmentStatus(str, Enum):
    """Current stage of project development"""
    CONCEPT = "concept"
    SCRIPT_DEVELOPMENT = "script_development"
    PACKAGED = "packaged"  # Has key talent attached
    GREENLIT = "greenlit"
    IN_PRODUCTION = "in_production"
    POST_PRODUCTION = "post_production"
    COMPLETED = "completed"


class StrategicPathway(str, Enum):
    """Primary financing strategy (from ontology)"""
    INDEPENDENT_PATCHWORK = "independent_patchwork"
    STUDIO_BUYOUT = "studio_buyout"
    INTERNATIONAL_COPRO = "international_copro"
    HYBRID = "hybrid"


class ProjectProfile(BaseModel):
    """Complete profile of an animated project"""

    # Identification
    project_id: str = Field(..., description="Unique project identifier")
    project_name: str = Field(..., description="Working title")

    # Basic parameters
    project_type: ProjectType
    animation_technique: AnimationTechnique
    target_audience: TargetAudience

    # If series
    number_of_episodes: Optional[int] = Field(default=None, description="For series/limited series")
    episode_runtime_minutes: Optional[int] = Field(default=None)

    # If feature
    target_runtime_minutes: Optional[int] = Field(default=None, description="For features")

    # Budget
    total_budget: Decimal = Field(..., gt=0, description="Total production budget USD")
    contingency_percentage: Decimal = Field(default=Decimal("10"), ge=0, le=20, description="Budget contingency %")

    # Development
    development_status: DevelopmentStatus
    expected_greenlight_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None

    # Creative team
    has_director_attached: bool = Field(default=False)
    director_name: Optional[str] = None
    director_track_record: Optional[str] = Field(default=None, description="Previous credits")

    has_voice_talent_attached: bool = Field(default=False)
    key_voice_talent: Optional[List[str]] = Field(default=None)

    # IP
    is_original_ip: bool = Field(default=True)
    underlying_ip_description: Optional[str] = Field(default=None, description="If based on existing IP")
    ip_ownership_status: Optional[str] = Field(default=None, description="e.g., 'Fully owned', 'Option exercised'")

    # Production jurisdictions
    production_jurisdictions: List[ProductionJurisdiction] = Field(..., min_length=1)

    # Strategic approach
    strategic_pathway: StrategicPathway

    # Market estimates (for pre-sales)
    estimated_worldwide_value: Optional[Decimal] = Field(default=None, description="Total market value estimate")
    territory_estimates: Optional[Dict[str, Decimal]] = Field(default=None, description="Territory-level estimates")

    # Comparable projects (comps)
    comparable_projects: Optional[List[str]] = Field(default=None, description="Similar projects for benchmarking")

    # Distribution
    has_distribution_commitment: bool = Field(default=False)
    distribution_commitment_description: Optional[str] = None

    # Stakeholder priorities (weights for optimization)
    priority_creative_control: Decimal = Field(default=Decimal("33.33"), ge=0, le=100, description="Importance weight %")
    priority_financial_return: Decimal = Field(default=Decimal("33.33"), ge=0, le=100, description="Importance weight %")
    priority_risk_mitigation: Decimal = Field(default=Decimal("33.34"), ge=0, le=100, description="Importance weight %")

    # Metadata
    created_date: date = Field(default_factory=date.today)
    last_updated: date = Field(default_factory=date.today)
    notes: Optional[str] = None

    def validate_priority_weights(self) -> bool:
        """Ensure priority weights sum to 100%"""
        total = self.priority_creative_control + self.priority_financial_return + self.priority_risk_mitigation
        return abs(total - Decimal("100")) < Decimal("0.01")  # Allow for rounding

    def get_primary_jurisdiction(self) -> Optional[ProductionJurisdiction]:
        """Get the jurisdiction with the highest spend percentage"""
        if not self.production_jurisdictions:
            return None
        return max(self.production_jurisdictions, key=lambda x: x.estimated_spend_percentage)

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "PROJ-001",
                "project_name": "The Animated Adventure",
                "project_type": "feature_film",
                "animation_technique": "cgi_3d",
                "target_audience": "family",
                "target_runtime_minutes": 90,
                "total_budget": "25000000",
                "development_status": "packaged",
                "strategic_pathway": "independent_patchwork",
                "production_jurisdictions": [
                    {
                        "country": "Canada",
                        "state_province": "Quebec",
                        "estimated_spend_percentage": "60",
                        "estimated_local_labor_percentage": "75"
                    }
                ]
            }
        }
