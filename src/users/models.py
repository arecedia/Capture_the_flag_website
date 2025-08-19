from datetime import datetime
import uuid
from operator import index
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

'''
Main Database Model
'''
class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    score: int = Field(default=0)
    rank: Optional[int] = None

    is_admin: bool = Field(default=False)
    is_active: bool = Field(default=True)

    profile_bio: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None

    solved_challenges: List["ChallengeSolve"] = Relationship(back_populates="user")

    def verify_password(self, password):
        if password is None :
            return False
        return pwd_context.verify(password, self.password)

    def update_password(self, password):
        if password is None:
            return False
        elif password != "":
            new_password = hash_password(password)
            self.password = new_password

'''
Public User Model
'''
class PublicUser(SQLModel):
    id: uuid.UUID
    username: str
    score: int
    rank: Optional[int]
    country: Optional[str]
    avatar_url: Optional[str]

'''
Model for creating users
'''
class CreateUser(SQLModel):
    username: str
    email: str
    password: str
    country: Optional[str] = None
    avatar_url: Optional[str] = None

'''
Model for updating users
'''
class UpdateUser(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_bio: Optional[str] = None

'''
Challenge Database Model
'''
class Challenge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, unique=True)
    category: str
    description:str
    points: int
    flag: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author_id: Optional[int] = Field(default=None, foreign_key="user.id")

    solves: List["ChallengeSolve"] = Relationship(back_populates="challenge")
    reviews: List["ChallengeReview"] = Relationship(back_populates="challenge")

'''
Model for saving who has completed what challenge
'''
class ChallengeSolve(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key = True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    challenge_id: int = Field(foreign_key="challenge.id")
    solved_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="solved_challenges")
    challenge: "Challenge" = Relationship(back_populates="solves")

'''
Model for saving reviews of challenges
'''
class ChallengeReview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    challenge_id: int = Field(foreign_key="challenge.id")
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship()
    challenge: "Challenge" = Relationship(back_populates="reviews")

'''
Model for creating reviews of challenges
'''
class CreateChallengeReview(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

'''
Public challenge review model
'''
class PublicChallengeReview(SQLModel):
    id: int
    user_id: uuid.UUID
    rating: int
    comment: Optional[str]
    created_at: datetime

'''
Model for creating challenges
'''
class CreateChallenge(SQLModel):
    title: str
    category: str
    description: str
    points: int
    flag: str

'''
Public challenge model
'''
class PublicChallenge(SQLModel):
    id: int
    title: str
    category: str
    description: str
    points: int
    author_id: Optional[uuid.UUID]
    created_at: datetime