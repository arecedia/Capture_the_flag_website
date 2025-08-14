import uuid
from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from src import database
from src.users import models
from src.auth import service as auth_service

router = APIRouter()

class ChallengeCreate(BaseModel):
    title: str
    category: str
    description: str
    points: int
    flag: str

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    points: Optional[int] = None
    flag: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False
    is_active: bool = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None

class ReviewCreate(BaseModel):
    challenge_id: int
    user_id: uuid.UUID
    content: str

class ReviewUpdate(BaseModel):
    content: Optional[str] = None

@router.post("/create-challenge")
async def create_challenge(
        data: ChallengeCreate,
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    challenge = models.Challenge(**data.dict())
    session.add(challenge)
    session.commit()
    session.refresh(challenge)
    return {"message": "Challenge created", "challenge": challenge}

@router.patch("/challenges/{challenge_id}")
async def update_challenge(
        challenge_id: int,
        data: ChallengeUpdate,
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    challenge = session.get(models.Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(challenge, key, value)

    session.add(challenge)
    session.commit()
    session.refresh(challenge)
    return {"message": "Challenge updated", "challenge": challenge}

@router.delete("/challenges/{challenge_id}")
async def delete_challenge(
        challenge_id: int,
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    challenge = session.get(models.Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    session.delete(challenge)
    session.commit()
    return {"message": "Challenge deleted"}

@router.post("/seed-challenges")
async def seed_challenges(
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    challenges = [
        {
            "title": "Challenge 1",
            "category": "Permissions",
            "description": "Find the correct flag in the permissions.",
            "points": 100,
            "flag": "P3rm1551ons",
        },
        {
            "title": "Challenge 2",
            "category": "Sneaky",
            "description": "A sneaky challenge.",
            "points": 150,
            "flag": "5n34ky",
        },
        {
            "title": "Challenge 3",
            "category": "Configuration",
            "description": "Misconfiguration issue.",
            "points": 200,
            "flag": "C0nf1gur4t10n",
        },
        {
            "title": "Challenge 4",
            "category": "Injection",
            "description": "Try to inject your way in.",
            "points": 250,
            "flag": "1nj3ct10n",
        },
        {
            "title": "Challenge 5",
            "category": "Cron Jobs",
            "description": "Something about scheduled jobs.",
            "points": 300,
            "flag": "Cr0nj0b5",
        }
    ]

    added = []
    skipped = []

    for c in challenges:
        existing = session.exec(
            select(models.Challenge).where(models.Challenge.title == c["title"])
        ).first()

        if not existing:
            challenge = models.Challenge(**c)
            session.add(challenge)
            added.append(c["title"])
        else:
            skipped.append(c["title"])

    session.commit()

    return {
        "message": "Seeding complete.",
        "added": added,
        "skipped": skipped
    }

@router.post("/users")
async def create_user(
        data: UserCreate,
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    hashed_pw = models.hash_password(data.password)
    user = models.User(
        username=data.username,
        email=data.email,
        password=hashed_pw,
        is_admin=data.is_admin,
        is_active=data.is_active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created", "user": user}

@router.patch("/users/{user_id}")
async def update_user(
        user_id: str,
        data: UserUpdate,
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    user = session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = auth_service.hash_password(update_data["password"])

    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User updated", "user": user}

@router.delete("/users/{user_id}")
async def delete_user(
        user_id: str,
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    user = session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return {"message": "User deleted"}


# -----------------------
# Review Routes
# -----------------------
@router.post("/reviews")
async def create_review(
        data: ReviewCreate,
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    review = models.ChallengeReview(**data.dict())
    session.add(review)
    session.commit()
    session.refresh(review)
    return {"message": "Review created", "review": review}

@router.patch("/reviews/{review_id}")
async def update_review(
        review_id: int,
        data: ReviewUpdate,
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    review = session.get(models.ChallengeReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(review, key, value)

    session.add(review)
    session.commit()
    session.refresh(review)
    return {"message": "Review updated", "review": review}

@router.delete("/reviews/{review_id}")
async def delete_review(
        review_id: int,
        session: Session = Depends(database.get_session),
        admin=Depends(auth_service.get_current_admin)
):
    review = session.get(models.ChallengeReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    session.delete(review)
    session.commit()
    return {"message": "Review deleted"}