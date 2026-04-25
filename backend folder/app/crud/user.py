from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.scalar(select(User).where(User.email == email))


def create(db: Session, schema: UserCreate) -> User:
    user = User(
        name=schema.name,
        email=schema.email,
        password_hash=get_password_hash(schema.password),
        role=schema.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    user = get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
