from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.category import Category
from app.models.enums import TransactionType
from app.models.user import User


def list_categories(db: Session, user: User) -> list[Category]:
    return db.query(Category).filter(Category.user_id == user.id).order_by(Category.name).all()


def create_category(db: Session, user: User, name: str, type_: TransactionType) -> Category:
    existing = (
        db.query(Category)
        .filter(Category.user_id == user.id, Category.name == name, Category.type == type_)
        .first()
    )
    if existing is not None:
        raise ConflictError("A category with this name and type already exists.")

    category = Category(user_id=user.id, name=name, type=type_)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_owned_category(db: Session, user: User, category_id: int) -> Category:
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user.id)
        .first()
    )
    if category is None:
        raise NotFoundError("Category not found.")
    return category


def rename_category(db: Session, user: User, category_id: int, new_name: str) -> Category:
    category = get_owned_category(db, user, category_id)
    existing = (
        db.query(Category)
        .filter(
            Category.user_id == user.id,
            Category.name == new_name,
            Category.type == category.type,
            Category.id != category.id,
        )
        .first()
    )
    if existing is not None:
        raise ConflictError("A category with this name and type already exists.")

    category.name = new_name
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, user: User, category_id: int) -> None:
    category = get_owned_category(db, user, category_id)
    db.delete(category)
    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise ConflictError(
            "Category is used by at least one transaction and cannot be deleted."
        ) from err
