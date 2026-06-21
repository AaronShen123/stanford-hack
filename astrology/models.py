from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

class TargetVectorEnum(str, Enum):
    WEALTH = "wealth"
    AFFINITY = "affinity"
    VITALITY = "vitality"
    MACRO_EVOLUTION = "macro_evolution"

class GenderEnum(str, Enum):
    M = "M"
    F = "F"

class AstrologyRequest(BaseModel):
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field(..., description="Birth time in HH:MM:SS format")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Birth latitude (-90 to 90)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Birth longitude (-180 to 180)")
    target_vector: TargetVectorEnum = Field(..., description="Target vector for synthesis analysis")
    timezone_offset: Optional[float] = Field(None, ge=-12.0, le=14.0, description="Optional timezone offset in hours. Approximated if not provided.")
    gender: GenderEnum = Field(GenderEnum.M, description="Optional biological gender for ZWDS calculations")

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("birth_date must match YYYY-MM-DD")
        from datetime import datetime
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("birth_date must be a valid calendar date")
        return v

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, v: str) -> str:
        if not re.match(r"^\d{2}:\d{2}:\d{2}$", v):
            raise ValueError("birth_time must match HH:MM:SS")
        from datetime import datetime
        try:
            datetime.strptime(v, "%H:%M:%S")
        except ValueError:
            raise ValueError("birth_time must be a valid time of day")
        return v


class TimeMetricsModel(BaseModel):
    local_datetime: str
    utc_datetime: str
    lmt_datetime: str
    tlt_datetime: str
    timezone_offset: float
    jd_ut: float
    jd_et: float
    eot_seconds: float
    branch_boundary_anomaly: bool = Field(False, description="Flag set if TLT is within 60s of an earthly branch boundary")


class WesternMatrix(BaseModel):
    sun_degree: float = Field(..., ge=0.0, lt=360.0)
    moon_degree: float = Field(..., ge=0.0, lt=360.0)
    ascendant_degree: float = Field(..., ge=0.0, lt=360.0)
    midheaven_degree: float = Field(..., ge=0.0, lt=360.0)
    saturn_degree: float = Field(..., ge=0.0, lt=360.0)
    mars_degree: float = Field(..., ge=0.0, lt=360.0)
    neptune_degree: float = Field(..., ge=0.0, lt=360.0)
    pluto_degree: float = Field(..., ge=0.0, lt=360.0)
    houses: Dict[int, float] = Field(..., description="Cusp degrees for houses 1 to 12")


class StarMetadata(BaseModel):
    name: str
    brightness_index: str = "Neutral" # Radiant, Neutral, Dark
    classification: str = "Benefic" # Benefic, Malefic
    archetype_definition: str = ""

class MainStarModel(BaseModel):
    name: str
    status: Optional[str] = ""

class ZWDSPalace(BaseModel):
    name: str = Field(..., description="Palace name (e.g. Ming, Wealth, Career)")
    stem_branch: str = Field(..., description="Heavenly Stem and Earthly Branch combination")
    stars: List[str] = Field(default_factory=list, description="List of major and minor stars residing in this palace")
    decadal_range: Optional[str] = Field(None, description="Decadal age range (e.g. 26-35)")
    main_stars: List[MainStarModel] = Field(default_factory=list, description="List of main stars and status")
    minor_stars: List[str] = Field(default_factory=list, description="List of minor stars")
    changsheng: str = Field("", description="Cosmic vitality stage")
    pillar_gods: List[str] = Field(default_factory=list, description="Pillar gods descriptors")
    one_year_luck: str = Field("", description="One year luck bounds")
    stars_metadata: List[StarMetadata] = Field(default_factory=list, description="Extended star definitions")


class ZWDSMatrix(BaseModel):
    palaces: List[ZWDSPalace] = Field(default_factory=list, description="The 12 palaces of the ZWDS chart")
    yearly_stem_branch: str = Field(..., description="Stem-Branch of the birth year")
    monthly_branch: str = Field(..., description="Earthly branch of the birth month")
    lunar_date_str: str = Field(..., description="Chinese lunar calendar representation of birth time")


class AstrologyAspect(BaseModel):
    planet1: str
    planet2: str
    aspect_type: str
    degree_difference: float
    orb: float


class ZWDSPattern(BaseModel):
    name: str
    is_triggered: bool
    description: str

class SynthesisFlags(BaseModel):
    friction_index: float = Field(..., description="Calculated structural friction index")
    friction_points: List[str] = Field(default_factory=list, description="Friction points list")
    aspects: List[AstrologyAspect] = Field(default_factory=list, description="Western planetary aspects")
    synthesis_notes: List[str] = Field(default_factory=list, description="Calculated integration insights")
    dual_matrix_indicator: bool = Field(False, description="Indicator if time is near boundary to trigger dual-matrix processing")
    critical_bottleneck: bool = Field(False, description="Flag for unified wealth bottleneck conditions")
    interpersonal_risk: bool = Field(False, description="Flag for unified interpersonal risk conditions")
    systemic_exhaustion: bool = Field(False, description="Flag for unified systemic health exhaustion conditions")
    palace_friction_index: float = Field(0.0, description="Palace friction index score")
    detected_patterns: List[ZWDSPattern] = Field(default_factory=list, description="Patterns identified in the chart")


class AstrologyResponse(BaseModel):
    birth_time_metrics: TimeMetricsModel
    western_matrix: WesternMatrix
    zwds_matrix: ZWDSMatrix
    synthesis_flags: SynthesisFlags

    model_config = ConfigDict(strict=True)


class AstrologyCompletionResponse(BaseModel):
    synthesis: AstrologyResponse
    compiled_prompt: str
    reading: str

    model_config = ConfigDict(strict=True)
