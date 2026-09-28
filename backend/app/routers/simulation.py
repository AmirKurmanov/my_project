from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Project, Scenario, User
from app.auth import get_required_user
from app.services.simulation import generate_simulation_data

router = APIRouter(prefix="/api/projects", tags=["Визуализация"])


@router.get("/{project_id}/simulation")
def get_simulation(
    project_id: int,
    scenario_id: int = None,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .options(joinedload(Project.object_type), joinedload(Project.scenarios))
        .filter(Project.id == project_id, Project.user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    # Pick scenario
    scenario = None
    if scenario_id:
        scenario = next((s for s in project.scenarios if s.id == scenario_id), None)
    else:
        scenario = next(
            (s for s in project.scenarios if s.scenario_type != "baseline" and s.results),
            None,
        )
    if not scenario:
        scenario = project.scenarios[0] if project.scenarios else None

    robot_count = 0
    if scenario and scenario.results:
        robot_count = scenario.results.get("robot_count", 3)
    robot_count = max(robot_count, 2)

    object_type = project.object_type.slug if project.object_type else "warehouse"
    params = project.parameters or {}

    data = generate_simulation_data(object_type, params, robot_count)
    data["scenario_name"] = scenario.name if scenario else "—"
    return data
