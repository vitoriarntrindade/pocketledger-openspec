import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.core.security import decode_access_token
from app.infrastructure.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme,
    ),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing access token.")
    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as err:
        raise UnauthorizedError("Invalid or expired access token.") from err
    user = db.get(User, user_id)
    if user is None:
        raise UnauthorizedError("Invalid or expired access token.")
    request.state.user_id = user.id
    return user
