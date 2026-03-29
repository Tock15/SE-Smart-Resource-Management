from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Connected to DB"}