from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.init_db import init_db
from app.routes import authRoute

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(authRoute.router)

@app.get("/")
def root():
    return {"message": "Connected to DB"}