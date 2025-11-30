from typing import List, Optional
from contextlib import asynccontextmanager
import shutil
import os
import uuid
import tempfile

from fastapi import FastAPI, HTTPException, Response, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from app.schemas import (
    PostSchemaBody,
    PostSchemaResponse,
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.db import create_db_and_tables, get_session, Post, User
from app.images import imagekit
from app.users import current_active_user, auth_backend, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting app...")
    await create_db_and_tables()
    print("✓ Database ready")
    yield
    print("🛑 Shutting down...")


app_route = FastAPI(lifespan=lifespan)
app_route.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app_route.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app_route.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app_route.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)
app_route.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"]
)


@app_route.get("/hello")
async def read_message() -> dict:
    return {"message": "Hello World"}


@app_route.post("/upload")
async def create_post(
    file: UploadFile = File(...),
    caption: str = Form(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
):
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        upload_file_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["uploaded_via_fastapi"],
            ),
        )

        if upload_file_result.response_metadata.http_status_code == 200:
            post = Post(
                user_id=user.id,
                caption=caption,
                url=upload_file_result.url,
                file_type=(
                    "video" if file.content_type.startswith("video/") else "image"
                ),
                file_name=upload_file_result.name,
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
        else:
            raise HTTPException(status_code=500, detail="File upload failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app_route.get("/feeds")
async def get_feeds(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    total_posts: List[Post] = [row[0] for row in result.all()]
    posts_details = []
    for post in total_posts:
        posts_details.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "is_owner": post.user_id == user.id,
                "email": user.email,
            }
        )
    return {"posts": posts_details}


@app_route.delete("/posts/{post_id}")
async def delete_post_by_id(
    post_id: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
):
    try:
        post_id = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_id))
        post: Optional[Post] = result.scalar_one_or_none()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this post"
            )

        await session.delete(post)
        await session.commit()
        return {"success": True, "message": "Post deleted", "post_id": str(post.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")
