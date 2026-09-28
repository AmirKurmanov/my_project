from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.models import RobotSolution, RobotCategory, User
from app.schemas import (
    RobotSolutionCreate, RobotSolutionUpdate, RobotSolutionResponse,
    RobotCategoryResponse,
)
from app.auth import get_current_admin

router = APIRouter(prefix="/api/catalog", tags=["Каталог"])


@router.get("/categories", response_model=List[RobotCategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(RobotCategory).all()


@router.get("/solutions", response_model=List[RobotSolutionResponse])
def list_solutions(
    category_id: Optional[int] = None,
    object_type: Optional[str] = None,
    min_payload: Optional[float] = None,
    max_payload: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "name",
    db: Session = Depends(get_db),
):
    query = db.query(RobotSolution).options(joinedload(RobotSolution.category))

    if category_id:
        query = query.filter(RobotSolution.category_id == category_id)
    if min_payload is not None:
        query = query.filter(RobotSolution.payload_capacity_kg >= min_payload)
    if max_payload is not None:
        query = query.filter(RobotSolution.payload_capacity_kg <= max_payload)
    if min_price is not None:
        query = query.filter(RobotSolution.equipment_cost_rub >= min_price)
    if max_price is not None:
        query = query.filter(RobotSolution.equipment_cost_rub <= max_price)
    if search:
        query = query.filter(
            RobotSolution.name.ilike(f"%{search}%")
            | RobotSolution.manufacturer.ilike(f"%{search}%")
            | RobotSolution.description.ilike(f"%{search}%")
        )
    if object_type:
        # Works with both SQLite (JSON stored as text) and PostgreSQL
        query = query.filter(
            RobotSolution.supported_object_types.like(f'%"{object_type}"%')
        )

    if sort_by == "price":
        query = query.order_by(RobotSolution.equipment_cost_rub.asc().nullslast())
    elif sort_by == "payload":
        query = query.order_by(RobotSolution.payload_capacity_kg.desc().nullslast())
    else:
        query = query.order_by(RobotSolution.name)

    return query.all()


@router.get("/solutions/{solution_id}", response_model=RobotSolutionResponse)
def get_solution(solution_id: int, db: Session = Depends(get_db)):
    sol = (
        db.query(RobotSolution)
        .options(joinedload(RobotSolution.category))
        .filter(RobotSolution.id == solution_id)
        .first()
    )
    if not sol:
        raise HTTPException(status_code=404, detail="Решение не найдено")
    return sol


@router.get("/solutions/compare/list")
def compare_solutions(
    ids: str = Query(..., description="ID решений через запятую"),
    db: Session = Depends(get_db),
):
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    solutions = (
        db.query(RobotSolution)
        .options(joinedload(RobotSolution.category))
        .filter(RobotSolution.id.in_(id_list))
        .all()
    )
    return solutions


@router.post("/solutions", response_model=RobotSolutionResponse)
def create_solution(
    data: RobotSolutionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    sol = RobotSolution(**data.model_dump())
    db.add(sol)
    db.commit()
    db.refresh(sol)
    return sol


@router.put("/solutions/{solution_id}", response_model=RobotSolutionResponse)
def update_solution(
    solution_id: int,
    data: RobotSolutionUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    sol = db.query(RobotSolution).filter(RobotSolution.id == solution_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Решение не найдено")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(sol, key, value)
    db.commit()
    db.refresh(sol)
    return sol


@router.delete("/solutions/{solution_id}")
def delete_solution(
    solution_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    sol = db.query(RobotSolution).filter(RobotSolution.id == solution_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Решение не найдено")
    db.delete(sol)
    db.commit()
    return {"message": "Решение удалено"}
