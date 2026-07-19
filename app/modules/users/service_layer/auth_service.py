from datetime import datetime, timedelta, timezone
from typing import Any

from app.modules.users.adapters.repository import UserRepository
from app.shared.config import get_settings
from app.shared.security import create_jwt_token, verify_password


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.settings = get_settings()

    def authenticate_user(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        if user.status != "active":
            raise ValueError("User is not active")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        return user

    def create_access_token(
        self,
        *,
        subject: str,
        claims: dict[str, Any] | None = None,
    ) -> tuple[str, int]:
        expires_delta = timedelta(
            minutes=self.settings.access_token_expire_minutes,
        )
        expires_at = datetime.now(timezone.utc) + expires_delta

        payload: dict[str, Any] = {
            "sub": subject,
            "exp": expires_at,
            "iat": datetime.now(timezone.utc),
        }
        if claims:
            payload.update(claims)

        token = create_jwt_token(
            payload,
            self.settings.normalized_secret_key,
        )
        return token, int(expires_delta.total_seconds())

    def login(self, email: str, password: str):
        user = self.authenticate_user(email, password)
        access_token, expires_in = self.create_access_token(
            subject=str(user.id),
            claims={
                "email": user.email,
                "role": user.role,
            },
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "user": user,
        }
