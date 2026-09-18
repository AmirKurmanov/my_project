from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI()


BALANCE = {}

@app.get("/balance")
def get_balance(wallet_name: str | None = None):
    if wallet_name is None:
        return {"wallet_balance": sum(BALANCE.values())}
    if wallet_name not in BALANCE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="NOT FOUND"
            )
    return {"wallet": wallet_name, "balance": BALANCE[wallet_name]}

@app.post("/wallets/{name}")
def create_wallet(name: str, initial_balance: float = 0):
    if name in BALANCE:
        raise HTTPException(
            status_code=400, 
            detail="wallet already exists"
            )
    BALANCE[name] = initial_balance
    return {
        "message": f"wallet {name} created", 
        "wallet": name, 
        "balance": BALANCE[name]
    }

