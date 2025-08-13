from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from sqlmodel import Session, select
from typing import Annotated, Optional, Dict
from passlib.context import CryptContext

from src.users import models
from src import database

import jwt
from jwt.exceptions import InvalidTokenError

import logging
from datetime import datetime, timedelta
import uuid

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)

# Token Expires in Minutes
JWT_TOKEN_EXPIRES = 30

# Cryptography Key
JWT_SECRET_KEY = ("bb7552e7504f689d3448ccf89fd15a701d38f53c1cedfc6c242eb9553a0d8c0e47fa453e6ddd76003f93ecbf5e044ffaaddb"
                  "648ef857107ff9759e52c6a2f5723f771de3d41a413bb879668bf6d780909c79b6d2c080e14fd2c5f8b0f56bb456dfe7c08f"
                  "3a373108dab34a6f1a50f528be147a7cb21b92b1bd98c6caabccfd4240f0d5c2aa0384eb53b31ecdc93e5fa0197b2747cd73"
                  "2fe54f3faeb0e37b9347928026c19a3b93adf79f250de858373334c68d8550c13a5501c6b59cfe54853a2511e4b1e0c8ba1f"
                  "adea2856c379561b9464a1b2a5d36002c225df7fe6db1e738c90de79fdc704c7302981ddbe92c6a25b9f562120e4655254c5"
                  "2535b3da421d")

# Algorithm
JWT_ALG = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    Follow the OAUTH2 Model to maintain compatibility with tokens
    and cookies.

    Essentially we overload the OAUTH2 Model to allow cookie based
    authentication to also be used.

    I have disabled auto_error by default,
    as it causes issues when we try to get a user or none
    (ie if there is a user return info, for example letting the homepage show either user or login pages)

    Error handing and 40x codes are handled in the requires authenticated user etc methods
    """

    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            auto_error: bool = False,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # Allow authorization scheme to be either cookie or header based
        log.debug("===== AUTH CALL ====")

        # Deal with cookie based authentication
        authorization: str = request.cookies.get("access_token")
        if authorization:
            # Beacuse I found the bearer prefix in the cookie ugly We dont actually have one.
            # Therefore just return whatever is in the access token field.
            log.debug("Auth via Cookie %s", authorization)
            return authorization

        # If we dont have a cookie try the request header
        if not authorization:
            log.debug("--> Auth Via Token")
            authorization: str = request.headers.get("Authorization")

        scheme, param = get_authorization_scheme_param(authorization)
        log.debug("scheme is %s", scheme)
        log.debug("params %s", param)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return param

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")

def create_access_token(
        data: dict,
        email = str
):
    """
    Given a dictionary of information (which should be user details)
    Create a JWT based token, and return it
    """
    if data["audience"] == "Admin":
        print("ADMIN2")
        to_encode = data.copy()

        unique_identifier = str(uuid.uuid4())
        expiration = datetime.now() + timedelta(30*60)
        issue_time = str(datetime.now())


        to_encode.update({"unique code": unique_identifier})
        to_encode.update({"issue time": issue_time})
        to_encode.update({"exp": expiration})
        to_encode.update({"issuer": "http://127.0.0.1:8000/api/auth/token"})


        encoded_jwt = jwt.encode(
            to_encode, JWT_SECRET_KEY, algorithm=JWT_ALG
        )
        return encoded_jwt
    elif data["audience"] == "User":
        print("USER2")
        to_encode = data.copy()

        unique_identifier = str(uuid.uuid4())
        expiration = datetime.now() +timedelta(30*60)
        issue_time = str(datetime.now())

        to_encode.update({"unique code": unique_identifier})
        to_encode.update({"issue time": issue_time})
        to_encode.update({"exp": expiration})
        to_encode.update({"issuer": "http://127.0.0.1:8000/api/auth/token"})


        encoded_jwt = jwt.encode(
            to_encode, JWT_SECRET_KEY, algorithm=JWT_ALG
        )
        print("JWT ", encoded_jwt)
        return encoded_jwt

def decode_token(
        token: str,
        session: Session = Depends(database.get_session),
):
    """
    Decode a token and return the relevant user if they exist.
    """
    print("decoding")
    if token is None:
        print("Empty Token")
        return None

    #try:
    payload = jwt.decode(
        token, JWT_SECRET_KEY, algorithms=[JWT_ALG]
    )
    user_id: str = payload.get("subject", None)


    #except InvalidTokenError as e:
    #    return e
    print("user id" , user_id)
    restored_uuid = uuid.UUID(user_id)
    the_user = session.get(models.User, restored_uuid)

    return the_user


def validate_login(
        email: str,
        password: str,
        session: Session = Depends(database.get_session),
):
    """
    Validate a login

    If the login is correct create a token and return it as a tuple
    of [User, token] otherwise, return [False, Message]
    """

    qry = select(models.User).where(models.User.email == email)
    db_user = session.exec(qry).first()
    if not db_user:
        return False
    # Confirm Password
    if not db_user.verify_password(password):
        return False

    # If we use UUID, our token hates it, so just return he hex
    hex_id = db_user.id.hex

    # Create a new token

    qry = select(models.User).where(models.User.admin == True and models.User.email == email)
    db_item = session.exec(qry).first
    if db_item:
        token = create_access_token(data={"subject": hex_id})

    qry - select(models.User).where(models.User.admin == False and models.User.email == email)
    db_item = session.exec(qry).first
    if db_item:
        token = create_access_token(data={"subject": hex_id})
    return [db_user, token]


async def get_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(database.get_session),
):
    """
    Return the current user. Or None if they don't exist
    """
    print("TOKEEN", token)
    if not token:
        return None

    the_user = decode_token(token, session)
    return the_user


async def get_auth_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(database.get_session),
):
    """
    Return the current user,  Raise a Not Authenticated
    Exception if the use does not exist
    """

    if not token:
        raise HTTPException(301, "Not Authenticated")

    the_user = decode_token(token, session)

    if not the_user:
        raise HTTPException(301, "Not Authenticated")

    return the_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(database, username: str, password: str):
    user = get_user(database, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user