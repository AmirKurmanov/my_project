from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import ObjectType
from app.schemas import ObjectTypeResponse

router = APIRouter(prefix="/api/objects", tags=["Типы объектов"])


@router.get("/", response_model=List[ObjectTypeResponse])
def list_object_types(db: Session = Depends(get_db)):
    return db.query(ObjectType).all()


@router.get("/{slug}", response_model=ObjectTypeResponse)
def get_object_type(slug: str, db: Session = Depends(get_db)):
    obj = db.query(ObjectType).filter(ObjectType.slug == slug).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Тип объекта не найден")
    return obj


@router.get("/{slug}/demo-data")
def get_demo_data(slug: str, db: Session = Depends(get_db)):
    obj = db.query(ObjectType).filter(ObjectType.slug == slug).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Тип объекта не найден")
    return {"parameters": obj.demo_parameters, "object_type": obj.name}
