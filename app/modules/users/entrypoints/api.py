from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from app.shared.config import get_settings
from app.shared.database import get_db
from app.shared.security import decode_jwt_token
from app.modules.users.adapters.repository import UserRepository
from app.modules.users.service_layer.auth_service import AuthService
from app.modules.users.service_layer.user_service import UserService
from app.modules.users.domain.entities import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_service(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return UserService(user_repo)


def get_auth_service(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return AuthService(user_repo)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_jwt_token(
            token,
            settings.normalized_secret_key,
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    user = UserRepository(db).get_by_id(int(user_id))
    if user is None or user.status != "active":
        raise credentials_exception

    return user


@auth_router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.login(data.email, data.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


@auth_router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserResponse])
def get_users(service: UserService = Depends(get_user_service)):
    return service.get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        return service.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, service: UserService = Depends(get_user_service)):
    try:
        return service.create_user(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    try:
        return service.update_user(user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        return service.delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
