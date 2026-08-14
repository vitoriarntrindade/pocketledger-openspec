from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.infrastructure.database import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.post(
    "",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryOut:
    category = category_service.create_category(
        db,
        current_user,
        payload.name,
        payload.type,
    )
    return CategoryOut.model_validate(category)


@router.get("", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CategoryOut]:
    categories = category_service.list_categories(db, current_user)
    return [
        CategoryOut.model_validate(category) for category in categories
    ]


@router.patch("/{category_id}", response_model=CategoryOut)
def rename_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryOut:
    category = category_service.rename_category(
        db,
        current_user,
        category_id,
        payload.name,
    )
    return CategoryOut.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    category_service.delete_category(db, current_user, category_id)
