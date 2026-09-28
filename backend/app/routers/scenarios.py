from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models import Scenario, Project, RobotSolution, User
from app.schemas import ScenarioCreate, ScenarioUpdate, ScenarioResponse
from app.auth import get_required_user
from app.services.economics import full_calculation

router = APIRouter(prefix="/api", tags=["Сценарии"])


@router.post("/projects/{project_id}/scenarios", response_model=ScenarioResponse)
def create_scenario(
    project_id: int,
    data: ScenarioCreate,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    scenario = Scenario(
        project_id=project_id,
        name=data.name,
        scenario_type=data.scenario_type,
        robot_solution_id=data.robot_solution_id,
        parameters=data.parameters,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return (
        db.query(Scenario)
        .options(joinedload(Scenario.robot_solution))
        .filter(Scenario.id == scenario.id)
        .first()
    )


@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def update_scenario(
    scenario_id: int,
    data: ScenarioUpdate,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    scenario = (
        db.query(Scenario)
        .join(Project)
        .filter(Scenario.id == scenario_id, Project.user_id == user.id)
        .first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Сценарий не найден")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(scenario, key, val)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/scenarios/{scenario_id}")
def delete_scenario(
    scenario_id: int,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    scenario = (
        db.query(Scenario)
        .join(Project)
        .filter(Scenario.id == scenario_id, Project.user_id == user.id)
        .first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Сценарий не найден")
    db.delete(scenario)
    db.commit()
    return {"message": "Сценарий удалён"}


@router.post("/scenarios/{scenario_id}/calculate", response_model=ScenarioResponse)
def calculate_scenario(
    scenario_id: int,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    scenario = (
        db.query(Scenario)
        .join(Project)
        .options(joinedload(Scenario.project), joinedload(Scenario.robot_solution))
        .filter(Scenario.id == scenario_id, Project.user_id == user.id)
        .first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Сценарий не найден")

    project = scenario.project
    project_params = project.parameters or {}
    scenario_params = scenario.parameters or {}

    if scenario.scenario_type == "baseline":
        # Baseline: calculate current costs only
        staff_count = float(project_params.get("staff_count", 20))
        avg_salary = float(project_params.get("avg_salary_rub", 60000))
        annual_labor = staff_count * avg_salary * 12
        results = {
            "robot_count": 0,
            "capex_total": 0,
            "capex_breakdown": {},
            "opex_annual": annual_labor,
            "opex_breakdown": {"Фонд оплаты труда": annual_labor},
            "current_costs_annual": annual_labor,
            "annual_effect": 0,
            "payback_years": None,
            "roi_pct": 0,
            "tco_5years": annual_labor * 5,
            "tco_yearly": [annual_labor * i for i in range(1, 6)],
            "sensitivity": {},
            "assumptions": ["Текущий процесс без изменений", "Учтены только затраты на персонал"],
            "formulas": ["Годовые затраты = Кол-во персонала × Средняя зарплата × 12"],
        }
    else:
        robot = scenario.robot_solution
        if not robot:
            raise HTTPException(status_code=400, detail="Для расчёта необходимо выбрать робота")

        merged = {**project_params, **scenario_params}
        results = full_calculation(merged, robot, scenario.scenario_type)

    scenario.results = results
    project.status = "calculated"
    db.commit()
    db.refresh(scenario)
    return (
        db.query(Scenario)
        .options(joinedload(Scenario.robot_solution))
        .filter(Scenario.id == scenario.id)
        .first()
    )


@router.get("/projects/{project_id}/compare")
def compare_scenarios(
    project_id: int,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    scenarios = (
        db.query(Scenario)
        .options(joinedload(Scenario.robot_solution))
        .filter(Scenario.project_id == project_id)
        .all()
    )
    comparison = []
    for s in scenarios:
        comparison.append({
            "id": s.id,
            "name": s.name,
            "type": s.scenario_type,
            "robot": s.robot_solution.name if s.robot_solution else "—",
            "results": s.results,
        })
    return {"project_name": project.name, "scenarios": comparison}
