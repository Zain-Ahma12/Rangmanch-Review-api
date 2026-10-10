from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_tables
from routes import router

from exceptions import (
    InvalidPlayNameError, invalid_play_name_handler,
    InvalidReviewIdError, invalid_review_id_handler
)

from fastapi_swagger_ui_theme import setup_swagger_ui_theme

from custom_docs_ui import setup_custom_docs

import uvicorn

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
    lifespan=lifespan,
    docs_url=None, # to override the default /docs route
)

# Use the theme helper, just enables dark mode.
# setup_swagger_ui_theme(app, docs_path="/docs")

setup_custom_docs(app, docs_path="/docs")

# register your custom exception handlers
app.add_exception_handler(InvalidPlayNameError, invalid_play_name_handler)
app.add_exception_handler(InvalidReviewIdError, invalid_review_id_handler)

# include the router
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host = "127.0.0.1", port = 8000, reload = True)