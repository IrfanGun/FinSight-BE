from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.shared.database import get_db
from app.modules.users.adapters.repository import UserRepository
from app.modules.users.service_layer.user_service import UserService
from app.modules.users.domain.entities import UserCreate, UserUpdate, UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


def get_user_service(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return UserService(user_repo)


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