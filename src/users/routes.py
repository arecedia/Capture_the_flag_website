import logging
import jwt
from sqlmodel import Session, select
from typing import Annotated, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import or_

import src.auth.service
from src import database
from src.users import models
from src.auth import service as auth_service
from src.auth import routes as auth_routes

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["API"])
templates = Jinja2Templates(directory="src/templates")

@router.get("/current_user")
async def get_current_user(
        user: models.User = Depends(auth_service.get_user)
):
    return(user)

@router.post("/login.html", response_class=JSONResponse)
async def login_code(
        *,
        request: Request,
        session: Session = Depends(database.get_session),
):
    body = await request.json()
    identifier = body.get("identifier")
    password = body.get("password")

    statement = select(models.User).where(
        or_(
            models.User.email == identifier,
            models.User.username == identifier
        )
    )
    result = session.exec(statement).first()

    if not result or not result.verify_password(password):
        return JSONResponse(content={"message": "Invalid details"}, status_code=400)

    audience = "admin" if result.is_admin else "user"

    result.last_login = datetime.utcnow()
    session.add(result)
    session.commit()

    encoded_jwt = auth_service.create_access_token(
        data={"audience": audience, "subject": result.id.hex}
    )

    response = JSONResponse(content={"success": True, "redirect_url": "http://127.0.0.1:8000"})
    response.set_cookie(key="access_token", value=encoded_jwt)
    return response


@router.post("/api/signup", response_class=JSONResponse)
async def signup_code(
    *,
    request: Request,
    session: Session = Depends(database.get_session),
):
    body = await request.json()
    email = body.get("email")
    username = body.get("username")
    country = body.get("country")
    password = body.get("password")
    password_confirm = body.get("password_confirm")


    if session.exec(select(models.User).where(models.User.email == email)).first():
        return JSONResponse(content={"message": "Invalid details"}, status_code=400)
    if session.exec(select(models.User).where(models.User.username == username)).first():
        return JSONResponse(content={"message": "Invalid details"}, status_code=400)
    if password != password_confirm:
        return JSONResponse(content={"message": "Invalid details"}, status_code=400)

    db_user = models.User(
        email=email,
        username=username,
        country=country,
        is_admin=False,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow(),
    )
    db_user.update_password(password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    audience = "admin" if email == "arecedia.admin@temp.org" else "user"
    encoded_jwt = auth_service.create_access_token(email=email, data={"audience": audience})

    return JSONResponse(
        content={
            "message": "Account Created",
            "access_token": encoded_jwt,
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "country": db_user.country,
                "score": db_user.score,
            }
        },
        status_code=201
    )

@router.get("/api/users", response_model=list[models.PublicUser])
async def get_users(session: Session = Depends(database.get_session)):
    qry = select(models.User)
    result = session.exec(qry).all()
    return result

@router.get("/auth_user")
async def get_auth_user(
        user: models.User = Depends(auth_service.get_auth_user)
):
    """
    Return the current User or None
    """
    return {"current_user": user}

@router.get("/api/reviews")
async def display_reviews(
        session: Session = Depends(database.get_session)
):
    """
    Return the contents of the review database
    """
    qry = select(models.Review)
    result = session.exec(qry).all()
    return result