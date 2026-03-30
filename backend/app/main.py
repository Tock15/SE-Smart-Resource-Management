from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.init_db import init_db
from app.routes.authRoute import router as auth_router
from app.routes.adminRoute import router as admin_router
from app.routes.resourceRoute import router as resource_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(resource_router)

@app.get("/")
def root():
    return {"message": "Connected to DB"}