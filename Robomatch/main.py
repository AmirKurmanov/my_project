from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
from database import get_connection

from auth import (
    RegisterRequest,
    LoginRequest, 
    login_user, 
    register_user
)
 
from robots import robots
from recommendations import RecommendationRequest, recomend_robot

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/robots")
def get_robots():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.id,
            r.name,
            r.manufacturer,
            rst.name AS solution_type,
            r.purpose,
            r.payload_kg,
            r.data_quality
        FROM robots r
        JOIN robot_solution_types rst
            ON rst.id = r.solution_type_id
        ORDER BY r.id
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "manufacturer": row[2],
            "solution_type": row[3],
            "purpose": row[4],
            "payload_kg": row[5],
            "data_quality": row[6]
        }
        for row in rows
    ]
  

@app.get("/robots/{robot_id}")
def get_robot(robot_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.id,
            r.name,
            r.manufacturer,
            rst.name AS solution_type,
            r.purpose,
            r.payload_kg,
            r.data_quality
        FROM robots r
        JOIN robot_solution_types rst
            ON rst.id = r.solution_type_id
        WHERE r.id = %s
    """, (robot_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Робот не найден")

    return {
        "id": row[0],
        "name": row[1],
        "manufacturer": row[2],
        "solution_type": row[3],
        "purpose": row[4],
        "payload_kg": row[5],
        "data_quality": row[6]
    }

@app.post("/recommend")
def recommend(data: RecommendationRequest):
    return recomend_robot(data)

@app.post("/register")
def register(data: RegisterRequest):
    return register_user(data)

@app.post("/login")
def login(data: LoginRequest):
    return login_user(data)

@app.get("/db-test")
def db_test():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM robots")
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "database": "connected",
        "robots_count": count
    }