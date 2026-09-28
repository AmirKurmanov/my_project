import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import pandas as pd
from app.database import get_db
from app.models import Project, Scenario, User, ObjectType
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.auth import get_required_user

router = APIRouter(prefix="/api/projects", tags=["Проекты"])


@router.get("/", response_model=List[ProjectResponse])
def list_projects(user: User = Depends(get_required_user), db: Session = Depends(get_db)):
    return (
        db.query(Project)
        .options(joinedload(Project.object_type), joinedload(Project.scenarios))
        .filter(Project.user_id == user.id)
        .order_by(Project.updated_at.desc())
        .all()
    )


@router.post("/", response_model=ProjectResponse)
def create_project(
    data: ProjectCreate,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    obj_type = db.query(ObjectType).filter(ObjectType.id == data.object_type_id).first()
    if not obj_type:
        raise HTTPException(status_code=404, detail="Тип объекта не найден")
    project = Project(
        user_id=user.id,
        name=data.name,
        object_type_id=data.object_type_id,
        parameters=data.parameters,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    # Auto-create baseline scenario
    baseline = Scenario(
        project_id=project.id,
        name="Базовый (без роботизации)",
        scenario_type="baseline",
        parameters=data.parameters,
    )
    db.add(baseline)
    db.commit()
    return (
        db.query(Project)
        .options(joinedload(Project.object_type), joinedload(Project.scenarios))
        .filter(Project.id == project.id)
        .first()
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
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
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return (
        db.query(Project)
        .options(joinedload(Project.object_type), joinedload(Project.scenarios))
        .filter(Project.id == project.id)
        .first()
    )


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    db.delete(project)
    db.commit()
    return {"message": "Проект удалён"}


@router.post("/{project_id}/duplicate", response_model=ProjectResponse)
def duplicate_project(
    project_id: int,
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    orig = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not orig:
        raise HTTPException(status_code=404, detail="Проект не найден")
    new_project = Project(
        user_id=user.id,
        name=f"{orig.name} (копия)",
        object_type_id=orig.object_type_id,
        parameters=orig.parameters,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return (
        db.query(Project)
        .options(joinedload(Project.object_type), joinedload(Project.scenarios))
        .filter(Project.id == new_project.id)
        .first()
    )


@router.post("/{project_id}/upload-params")
def upload_parameters(
    project_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_required_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    try:
        content = file.file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Поддерживаются только CSV и Excel файлы")

        # Expect columns: parameter_name, value
        if "parameter_name" in df.columns and "value" in df.columns:
            params = dict(zip(df["parameter_name"], df["value"]))
        else:
            # Try first row as header, rest as values
            params = df.iloc[0].to_dict() if len(df) > 0 else {}

        project.parameters = params
        db.commit()
        return {"message": "Параметры загружены", "parameters": params}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка чтения файла: {str(e)}")
