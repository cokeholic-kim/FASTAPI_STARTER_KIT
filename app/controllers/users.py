from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.user import UserRepository
from app.schemas.response import SuccessResponse
from app.schemas.user import UserCreateRequest, UserListResponse, UserResponse, UserUpdateRequest
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    service = UserService(UserRepository(db))
    user = await service.create_user(payload)

    return SuccessResponse(
        message="User created",
        data=UserResponse.model_validate(user).model_dump(),
    ).to_response(status_code=201)


@router.get("", status_code=status.HTTP_200_OK)
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    service = UserService(UserRepository(db))
    users, total = await service.list_users(skip=skip, limit=limit)

    payload = UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
    )
    return SuccessResponse(data=payload.model_dump()).to_response(status_code=200)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    service = UserService(UserRepository(db))
    user = await service.get_user(user_id)
    return SuccessResponse(data=UserResponse.model_validate(user).model_dump()).to_response(status_code=200)


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    service = UserService(UserRepository(db))
    user = await service.update_user(user_id, payload)
    return SuccessResponse(data=UserResponse.model_validate(user).model_dump()).to_response(status_code=200)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    service = UserService(UserRepository(db))
    await service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
