import os
import uuid

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager
from sqlmodel import Session, select

from pydantic import BaseModel
from src import database
from src.users import models
from src.auth import service as auth_service

@asynccontextmanager
async def lifespan_function(app: FastAPI):
    database.create_db_and_tables()
    yield

def create_app():
    app = FastAPI(lifespan=lifespan_function)

    from src.users import routes as user_routes
    from src.auth import routes as auth_routes
    from src.users import view_routes

    app.mount("/static", StaticFiles(directory="src/static"), name="static")

    app.include_router(user_routes.router, prefix="/api", tags=["users"])
    app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
    app.include_router(view_routes.router, prefix="", tags=["routes"])

    if os.getenv("ENV") != "TEST":
        static_dir = "src/static"
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory="src/static"), name="static")
        else:
            print(f"Static directory '{static_dir}' does not exist, skipping mounting")
            app.templates = Jinja2Templates(directory="src/templates")
    return app
app = create_app()