from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import RobotSolution
from app.schemas import RecommendationRequest, RecommendationResponse
from app.services.recommendations import match_solutions

router = APIRouter(prefix="/api/recommendations", tags=["Рекомендации"])


@router.post("/match", response_model=RecommendationResponse)
def get_recommendations(
    data: RecommendationRequest,
    db: Session = Depends(get_db),
):
    solutions = (
        db.query(RobotSolution)
        .options(joinedload(RobotSolution.category))
        .all()
    )
    recommendations = match_solutions(
        object_type_slug=data.object_type_slug,
        parameters=data.parameters,
        solutions=solutions,
    )
    return RecommendationResponse(
        recommendations=recommendations,
        total=len(recommendations),
    )
