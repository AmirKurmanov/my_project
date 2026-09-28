from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # guest, user, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class ObjectType(Base):
    __tablename__ = "object_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(100))
    parameters_schema = Column(JSON)
    demo_parameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="object_type")


class RobotCategory(Base):
    __tablename__ = "robot_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    solutions = relationship("RobotSolution", back_populates="category")


class RobotSolution(Base):
    __tablename__ = "robot_solutions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    manufacturer = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("robot_categories.id"), nullable=False)
    country = Column(String(100))
    availability_status = Column(String(100), default="available")
    description = Column(Text)

    # Technical specs
    payload_capacity_kg = Column(Float, nullable=True)
    length_mm = Column(Float, nullable=True)
    width_mm = Column(Float, nullable=True)
    height_mm = Column(Float, nullable=True)
    max_speed_ms = Column(Float, nullable=True)
    productivity_per_hour = Column(Float, nullable=True)
    battery_life_hours = Column(Float, nullable=True)
    positioning_accuracy_mm = Column(Float, nullable=True)
    navigation_type = Column(String(255), nullable=True)
    operating_conditions = Column(String(500), nullable=True)

    # Infrastructure
    min_aisle_width_mm = Column(Float, nullable=True)
    charging_stations_required = Column(Boolean, default=False)
    connectivity_requirements = Column(String(500), nullable=True)
    integration_options = Column(String(500), nullable=True)

    # Economics
    equipment_cost_rub = Column(Float, nullable=True)
    software_cost_rub = Column(Float, nullable=True)
    implementation_cost_rub = Column(Float, nullable=True)
    annual_maintenance_cost_rub = Column(Float, nullable=True)
    acquisition_model = Column(String(100), nullable=True)
    service_life_years = Column(Integer, nullable=True)

    # Applicability
    supported_processes = Column(JSON)
    supported_object_types = Column(JSON)
    limitations = Column(Text, nullable=True)
    case_studies = Column(Text, nullable=True)

    # Data quality
    data_source = Column(String(500), nullable=True)
    data_updated_at = Column(DateTime, nullable=True)
    data_completeness = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("RobotCategory", back_populates="solutions")
    scenarios = relationship("Scenario", back_populates="robot_solution")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    object_type_id = Column(Integer, ForeignKey("object_types.id"), nullable=False)
    parameters = Column(JSON)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    object_type = relationship("ObjectType", back_populates="projects")
    scenarios = relationship("Scenario", back_populates="project", cascade="all, delete-orphan")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    scenario_type = Column(String(50), nullable=False)  # baseline, purchase, raas
    robot_solution_id = Column(Integer, ForeignKey("robot_solutions.id"), nullable=True)
    parameters = Column(JSON)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="scenarios")
    robot_solution = relationship("RobotSolution", back_populates="scenarios")
