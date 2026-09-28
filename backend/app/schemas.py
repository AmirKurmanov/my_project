from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field


# ──── Auth ────

class UserCreate(BaseModel):
    email: str = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль")
    full_name: str = Field(..., description="ФИО")


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# ──── Object Types ────

class ObjectTypeResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    parameters_schema: Optional[Any]
    demo_parameters: Optional[Any]

    class Config:
        from_attributes = True


# ──── Robot Categories ────

class RobotCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]

    class Config:
        from_attributes = True


# ──── Robot Solutions ────

class RobotSolutionCreate(BaseModel):
    name: str
    manufacturer: str
    category_id: int
    country: Optional[str] = None
    availability_status: str = "available"
    description: Optional[str] = None
    payload_capacity_kg: Optional[float] = None
    length_mm: Optional[float] = None
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None
    max_speed_ms: Optional[float] = None
    productivity_per_hour: Optional[float] = None
    battery_life_hours: Optional[float] = None
    positioning_accuracy_mm: Optional[float] = None
    navigation_type: Optional[str] = None
    operating_conditions: Optional[str] = None
    min_aisle_width_mm: Optional[float] = None
    charging_stations_required: bool = False
    connectivity_requirements: Optional[str] = None
    integration_options: Optional[str] = None
    equipment_cost_rub: Optional[float] = None
    software_cost_rub: Optional[float] = None
    implementation_cost_rub: Optional[float] = None
    annual_maintenance_cost_rub: Optional[float] = None
    acquisition_model: Optional[str] = None
    service_life_years: Optional[int] = None
    supported_processes: Optional[List[str]] = None
    supported_object_types: Optional[List[str]] = None
    limitations: Optional[str] = None
    case_studies: Optional[str] = None
    data_source: Optional[str] = None
    data_completeness: Optional[str] = None
    image_url: Optional[str] = None


class RobotSolutionUpdate(RobotSolutionCreate):
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    category_id: Optional[int] = None


class RobotSolutionResponse(BaseModel):
    id: int
    name: str
    manufacturer: str
    category_id: int
    category: Optional[RobotCategoryResponse] = None
    country: Optional[str]
    availability_status: str
    description: Optional[str]
    payload_capacity_kg: Optional[float]
    length_mm: Optional[float]
    width_mm: Optional[float]
    height_mm: Optional[float]
    max_speed_ms: Optional[float]
    productivity_per_hour: Optional[float]
    battery_life_hours: Optional[float]
    positioning_accuracy_mm: Optional[float]
    navigation_type: Optional[str]
    operating_conditions: Optional[str]
    min_aisle_width_mm: Optional[float]
    charging_stations_required: bool
    connectivity_requirements: Optional[str]
    integration_options: Optional[str]
    equipment_cost_rub: Optional[float]
    software_cost_rub: Optional[float]
    implementation_cost_rub: Optional[float]
    annual_maintenance_cost_rub: Optional[float]
    acquisition_model: Optional[str]
    service_life_years: Optional[int]
    supported_processes: Optional[Any]
    supported_object_types: Optional[Any]
    limitations: Optional[str]
    case_studies: Optional[str]
    data_source: Optional[str]
    data_completeness: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ──── Projects ────

class ProjectCreate(BaseModel):
    name: str = Field(..., description="Название проекта")
    object_type_id: int = Field(..., description="ID типа объекта")
    parameters: Optional[Dict[str, Any]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ScenarioBase(BaseModel):
    id: int
    name: str
    scenario_type: str
    robot_solution_id: Optional[int]
    parameters: Optional[Any]
    results: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    object_type_id: int
    object_type: Optional[ObjectTypeResponse] = None
    parameters: Optional[Any]
    status: str
    scenarios: Optional[List[ScenarioBase]] = []
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ──── Scenarios ────

class ScenarioCreate(BaseModel):
    name: str = Field(..., description="Название сценария")
    scenario_type: str = Field(..., description="Тип: baseline, purchase, raas")
    robot_solution_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ScenarioResponse(BaseModel):
    id: int
    project_id: int
    name: str
    scenario_type: str
    robot_solution_id: Optional[int]
    robot_solution: Optional[RobotSolutionResponse] = None
    parameters: Optional[Any]
    results: Optional[Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ──── Recommendations ────

class RecommendationRequest(BaseModel):
    object_type_slug: str
    parameters: Dict[str, Any]


class RecommendationItem(BaseModel):
    solution: RobotSolutionResponse
    score: float
    reasons: List[str]
    warnings: List[str]
    excluded: bool = False
    excluded_reasons: List[str] = []


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    total: int


# ──── Economics ────

class EconomicCalculationRequest(BaseModel):
    project_parameters: Dict[str, Any]
    scenario_type: str
    robot_solution_id: int
    overrides: Optional[Dict[str, Any]] = None


class EconomicResult(BaseModel):
    robot_count: int
    capex_total: float
    capex_breakdown: Dict[str, float]
    opex_annual: float
    opex_breakdown: Dict[str, float]
    current_costs_annual: float
    annual_effect: float
    payback_years: Optional[float]
    roi_pct: float
    tco_5years: float
    tco_yearly: List[float]
    sensitivity: Dict[str, Any]
    assumptions: List[str]
    formulas: List[str]
