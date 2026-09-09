from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import uvicorn

class User(BaseModel):
    id: int | None = None  
    name: str
    age: int

users_db = [
    {"id": 1, "name": "batman", "age": 40}, 
    {"id": 2, "name": "superman", "age": 30},
    {"id": 3, "name": "wonder woman", "age": 5000},
    {"id": 4, "name": "flash", "age": 18},
    {"id": 5, "name": "martian manhunter", "age": 300},
    {"id": 6, "name": "green lantern", "age": 25},
    {"id": 7, "name": "aquaman", "age": 40}
]

app = FastAPI()

@app.get("/users")
async def get_users():
    return users_db

@app.post("/users")
async def create_user(user: User):
    new_user = user.model_dump()
    
    if new_user.get("id") is None:
        new_user["id"] = len(users_db) + 1
    users_db.append(new_user)
    
    return {"message": "user created", "user": new_user}

@app.put("/users/{user_id}")
async def update_user_complete(user_id: int, updated_user: User):
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db[index] = updated_user.model_dump()
            return {"message": "User updated completely", "user": updated_user}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hero not found')

    

if __name__ == "__main__":
    uvicorn.run(app)