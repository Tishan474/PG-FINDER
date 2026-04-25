from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.security import decode_token, CREDENTIALS_EXCEPTION
from app.crud import user as user_crud
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise CREDENTIALS_EXCEPTION
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise CREDENTIALS_EXCEPTION
    user_id = payload.get("sub")
    if not user_id:
        raise CREDENTIALS_EXCEPTION
    user = user_crud.get_by_id(db, int(user_id))
    if not user:
        raise CREDENTIALS_EXCEPTION
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    try:
        return get_current_user(credentials, db)
    except Exception:
        return None


def require_owner_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.owner, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner or admin access required",
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
