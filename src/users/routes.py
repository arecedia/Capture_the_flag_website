import logging
from urllib.error import HTTPError
import os

import jwt
import shutil
from sqlmodel import Session, select
from typing import Annotated, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
from sqlalchemy import or_
from starlette.responses import RedirectResponse
from pathlib import Path

import src.auth.service
from src import database
from src.users import models
from src.auth import service as auth_service
from src.auth import routes as auth_routes

from fastapi import APIRouter, Depends, Request, Form, HTTPException, Cookie, UploadFile, File, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

log = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")
UPLOAD_DIR = "static/uploads"


@router.get("/current_user")
async def get_current_user(
        user: models.User = Depends(auth_service.get_user)):
    return user

@router.post("/login", response_class=JSONResponse)
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
        data={"audience": audience, "subject": result.id},
        email=result.email
    )

    response = JSONResponse(content={"success": True, "redirect_url": "/Index/"})
    response.set_cookie(
        key="access_token",
        value=encoded_jwt,
        httponly=True,
        max_age=1800,
        path="/",
        samesite="lax",
        secure=False
    )
    return response

@router.get("/Logout")
async def logout(
        request: Request,
        response: Response
):
    # Clear the authentication/session cookie
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")

    return response

@router.post("/signup", response_class=JSONResponse)
async def signup_code(*,
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
    encoded_jwt = auth_service.create_access_token(
        email=email, data={
            "audience": audience,
            "subject": db_user.id
        }
    )

    response = JSONResponse(
        content={
            "success": True,
            "redirect_url": "/Profile/",
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
    response.set_cookie(key="access_token", value=encoded_jwt, httponly=True)
    return response

@router.get("/users", response_model=list[models.PublicUser])
async def get_users(session: Session = Depends(database.get_session)):
    qry = select(models.User)
    result = session.exec(qry).all()
    return result

@router.get("/reviews")
async def display_reviews(
        session: Session = Depends(database.get_session)
):
    """
    Return the contents of the review database
    """
    qry = select(models.Review)
    result = session.exec(qry).all()
    return result

@router.post("/Challenge")
async def submit_flag(*,
                      session: Session = Depends(database.get_session),
                      request:Request,
                      current_user: models.User = Depends(auth_service.get_user)
                      ):
    body = await request.json()
    flag = body.get("flag")

    if not flag:
        return HTTPException(status_code=400, detail="Flag not found")

    challenge = session.exec(
        select(models.Challenge).where(models.Challenge.flag == flag)).first()

    if not challenge:
        return HTTPException(status_code=400, details="Invalid flag")

    existing_solve = session.exec(
        select(models.ChallengeSolve)
        .where(models.ChallengeSolve.user_id == current_user.id)
        .where(models.ChallengeSolve.challenge_id == challenge.id)
    ).first()

    if existing_solve:
        return {"success": False, "message": "You have already solved this challenge"}

    new_solve = models.ChallengeSolve(
        user_id=current_user.id,
        challenge_id=challenge.id,
        solved_at=datetime.utcnow(),
    )
    session.add(new_solve)

    current_user.score += challenge.points
    session.add(current_user)

    session.commit()
    session.refresh(current_user)

@router.post("/Profile/upload/")
async def upload_profile_picture(
        file: UploadFile = File(...),
        session: Session = Depends(database.get_session),
        user: models.User = Depends(auth_service.get_user)
):
    # Ensure the file extension is lowercase and safe
    ext = os.path.splitext(file.filename)[1].lower()
    filename = f"user_{user.id}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Save the uploaded file
    with open(filepath, "wb") as buffer:
        print("File absolute path:", os.path.abspath(filepath))
        buffer.write(await file.read())

    user.profile_picture = filename
    session.add(user)
    session.commit()

    print(os.path.abspath(filepath))
    print(os.path.exists(filepath))
    print("Saved profile picture in DB:", user.profile_picture)

    return RedirectResponse(url="/Profile/", status_code=303)

@router.post("/Profile/edit/")
async def edit_profile(
        new_username: str | None = Form(None),
        new_bio: str | None = Form(None),
        file: UploadFile | None = File(None),
        session: Session = Depends(database.get_session),
        user: models.User = Depends(auth_service.get_user)  # inject current user
):
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update username and bio only if new values are provided
    if new_username and new_username.strip():
        user.username = new_username.strip()
    if new_bio and new_bio.strip():
        user.profile_bio = new_bio.strip()

    # Update profile picture if a file is uploaded
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1]
        filename = f"user_{uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        user.profile_picture = filename

    session.add(user)
    session.commit()
    session.refresh(user)

    return RedirectResponse(url="/Profile/", status_code=303)