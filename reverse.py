from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Task manager API",
    description="project",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
    
if __name__ == "__main__":
    uvicorn.run(app)
