from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, SessionLocal, Base
from app.models import *  # noqa: F401, F403 — register all models
from app.routers import auth, objects, catalog, projects, scenarios, recommendations, export, simulation
from app.seed_data import seed_database

app = FastAPI(
    title="RoboMatch API",
    description="Платформа подбора роботизированных решений для бизнеса",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(objects.router)
app.include_router(catalog.router)
app.include_router(projects.router)
app.include_router(scenarios.router)
app.include_router(recommendations.router)
app.include_router(export.router)
app.include_router(simulation.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "RoboMatch API"}
