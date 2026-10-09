from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_tables
from routes.reviews import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan started")
    create_tables()
    print("Database tables created")
    yield
    # shutdown: clean up here
    print("Shutting down the app")
    

app = FastAPI(
    title= "Rangmanch review API",
    description= "Theater customer review API for a Hyderabad based theatre startup",
    lifespan=lifespan
)

app.include_router(router)