import logging
from sqlmodel import Session, select
from typing import Optional
from src import database
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.users import models

import src.auth.service as auth_service

log = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="Home/Index.html",
        context={}
    )

@router.get("/Index/", response_class=HTMLResponse)
async def home(
        request: Request,
        user: Optional[models.User] = Depends(auth_service.optional_user)
):
    return templates.TemplateResponse("Home/Index.html", {"request": request, "user": user})

@router.get("/Challenges/", response_class=HTMLResponse)
async def challenges(request: Request):
    return templates.TemplateResponse("Home/Challenges.html", {"request": request})

@router.get("/Reviews/", response_class=HTMLResponse)
async def reviews(request: Request):
    return templates.TemplateResponse("Home/Reviews.html", {"request": request})

@router.get("/Tutorials/", response_class=HTMLResponse)
async def tutorials(request: Request):
    return templates.TemplateResponse("Home/Tutorials.html", {"request": request})

@router.get("/Login/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("Home/Login.html", {"request": request})

@router.get("/Signup/", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("Home/Signup.html", {"request": request})

@router.get("/Profile", response_class=HTMLResponse)
async def profile_page(
        request: Request,
        user: models.User = Depends(auth_service.get_user)
):
    return templates.TemplateResponse(
        "Home/Profile.html",
        {
            "request": request,
            "username": user.username,
            "profile_picture": user.profile_picture,
            "profile_bio": user.profile_bio
        },
    )

@router.get("/user.html", response_class=HTMLResponse)
async def user_view(*,
                    request: Request,
                    session: Session = Depends(database.get_session)
                    ):
    qry = select(models.User)
    users = session.exec(qry).all()

    return templates.TemplateResponse(
        request=request,
        name="Home/User.html",
        context={"users": users}
    )

@router.get("/challenge/1", response_class=HTMLResponse)
async def challenge_1_view(request: Request):
    return templates.TemplateResponse("Challenges/Challenge_1.html", {"request": request})


@router.get("/challenge/2", response_class=HTMLResponse)
async def challenge_2_view(request: Request):
    return templates.TemplateResponse("Challenges/Challenge_2.html", {"request": request})


@router.get("/challenge/3", response_class=HTMLResponse)
async def challenge_3_view(request: Request):
    return templates.TemplateResponse("Challenges/Challenge_3.html", {"request": request})

@router.get("/challenge/4", response_class=HTMLResponse)
async def challenge_4_view(request: Request):
    return templates.TemplateResponse("Challenges/Challenge_4.html", {"request": request})


@router.get("/challenge/5", response_class=HTMLResponse)
async def challenge_5_view(request: Request):
    return templates.TemplateResponse("Challenges/Challenge_5.html", {"request": request})

@router.get("/tutorial/1", response_class=HTMLResponse)
async def tutorial_1_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Tutorials/Tutorial_1.html",
        context = {}
    )


@router.get("/tutorial/2", response_class=HTMLResponse)
async def tutorial_2_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Tutorials/Tutorial_2.html",
        context = {}
    )


@router.get("/tutorial/3", response_class=HTMLResponse)
async def tutorial_3_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Tutorials/Tutorial_3.html",
        context = {}
    )


@router.get("/tutorial/4", response_class=HTMLResponse)
async def tutorial_4_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Tutorials/Tutorial_4.html",
        context = {}
    )


@router.get("/tutorial/5", response_class=HTMLResponse)
async def tutorial_5_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Tutorials/Tutorial_5.html",
        context = {}
    )

@router.get("/Reviews/", response_class=HTMLResponse)
async def reviews_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="Home/Reviews.html",
        context={}
    )

@router.get("/Review-Submission/1", response_class=HTMLResponse)
async def review_submission_1_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Reviews/Review_1.html",
        context = {}
    )

@router.get("/Review-Submission/2", response_class=HTMLResponse)
async def review_submission_2_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Reviews/Review_2.html",
        context = {}
    )

@router.get("/Review-Submission/3", response_class=HTMLResponse)
async def review_submission_3_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Reviews/Review_3.html",
        context = {}
    )

@router.get("/Review-Submission/4", response_class=HTMLResponse)
async def review_submission_4_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Reviews/Review_4.html",
        context = {}
    )

@router.get("/Review-Submission/5", response_class=HTMLResponse)
async def review_submission_5_view(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "Reviews/Review_5.html",
        context = {}
    )