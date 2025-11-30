import uuid
from typing import List, Optional
from fastapi import Response, Depends
from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin, models
from fastapi_users.authentication import CookieTransport, AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User, get_users_db


SECRET = "SECRET_KEY_FOR_JWT_TOKENS"

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET


    async def on_after_register(self, user: User, request: Optional[Response] = None):
        print(f"User {user.id} has registered.")
    
    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Response] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_users_db)):
    yield UserManager(user_db) 

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

    
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
