from fastapi import APIRouter, Depends, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from responses.user import UserResponse, LoginResponse
from schemas.user import RegisterUserRequest
from services import user
from config.security import get_current_user, oauth2_scheme
from config.database import get_session


user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

auth_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme), Depends(get_current_user)]
)

guest_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

@user_router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(data: RegisterUserRequest, session: Session = Depends(get_session)):
    return await user.create_user_account(data, session)

@guest_router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def user_login(data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    return await user.get_login_token(data, session)

@guest_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def refresh_token(refresh_token = Header(), session: Session = Depends(get_session)):
    return await user.get_refresh_token(refresh_token, session)

@auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def fetch_user(user = Depends(get_current_user)):
    return user

@auth_router.get("/{pk}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_info(pk, session: Session = Depends(get_session)):
    return await user.fetch_user_detail(pk, session)