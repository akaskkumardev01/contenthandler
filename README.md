# Social Media Platform - FastAPI + Streamlit

A social media platform with file upload, image transformation, user authentication, and a feed. Built with FastAPI backend + Streamlit frontend.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Architecture Flow](#architecture-flow)
- [File Structure & Components](#file-structure--components)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Features](#features)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

This application allows users to:
- Register and authenticate with JWT tokens
- Upload media (images/videos) to ImageKit CDN
- Apply real-time image transformations
- View a social feed with posts from other users`
- Delete their own posts`
- Manage their profile

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI | REST API framework (async) |
| **Frontend** | Streamlit | Interactive UI dashboard |
| **Database** | SQLite + SQLAlchemy | Data persistence (ORM) |
| **Authentication** | fastapi-users + JWT | Secure user auth |
| **CDN** | ImageKit | Image/video hosting & transformations |
| **Python Version** | 3.11+ | Runtime environment |

---

## 🏗 Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User visits Streamlit (frontend.py) at :8501             │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Login → POST /auth/jwt/login (app.py)                    │
│    FastAPI validates credentials → returns JWT token        │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Streamlit stores JWT in session_state                    │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. User uploads file → POST /upload (app.py)                │
│    File sent to ImageKit CDN (images.py)                    │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. FastAPI saves metadata to SQLite (db.py)                 │
│    Returns public ImageKit URL                              │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. User views feed → GET /feeds (app.py)                    │
│    Returns posts with ImageKit transformation URLs          │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Streamlit displays images with transformations           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure & Components

### **app.py** — FastAPI Backend Server

**Purpose:** REST API endpoints for social features

**Key Features:**
- ✓ Auth routers (register, login, JWT, password reset, email verify) via `fastapi-users`
- ✓ `POST /upload` — upload media (file + caption) with ImageKit transformation
- ✓ `GET /feeds` — fetch user's feed (posts from followed users or all)
- ✓ `DELETE /posts/{post_id}` — delete a post
- ✓ `GET /hello` — health check endpoint
- ✓ **Lifespan:** startup creates database tables, shutdown cleanup

**Dependencies:** FastAPI, SQLAlchemy, ImageKit, fastapi-users

---

### **db.py** — SQLAlchemy ORM & SQLite Database

**Purpose:** Data models and database session management

**Components:**
- **`User` Model** — inherits from `fastapi-users` `SQLAlchemyBaseUserTableUUID`
  - Fields: id (UUID), email, hashed_password, etc.
  - Relationship: one-to-many with Posts
  
- **`Post` Model** — stores upload metadata
  - Fields: id, user_id, caption, url, file_type, file_name, created_at, updated_at
  - Relationship: many-to-one with User

- **`get_session()`** — FastAPI dependency providing async database sessions
- **`create_db_and_tables()`** — initializes database schema at app startup
- **`get_users_db()`** — provides SQLAlchemy user database for fastapi-users

**Database:** SQLite (async via `aiosqlite`)

---

### **users.py** — Authentication & User Management

**Purpose:** JWT authentication and user management via fastapi-users

**Components:**
- **`UserManager`** — handles user creation, password hashing, validation
- **`auth_backend`** — JWT-based authentication (Bearer token)
- **`get_user_manager()`** — FastAPI dependency to get current user manager
- **`get_jwt_strategy()`** — configures JWT token generation/validation (SECRET key)
- **`current_active_user`** — dependency to get authenticated user in endpoints

---

### **schemas.py** — Pydantic Data Models

**Purpose:** Request/response validation and documentation

**Models:**
- **`PostSchemaBody`** — POST request body (title, content)
- **`PostSchemaResponse`** — POST response (title, content, id, timestamps)
- **`UserCreate`** — registration request (email, password)
- **`UserRead`** — user response (email, id)
- **`UserUpdate`** — user update request (email, password)

---

### **frontend.py** — Streamlit Interactive UI

**Purpose:** User-facing frontend application

**Pages:**
- **`login_page()`** — email/password login form
- **`upload_page()`** — media upload + caption input
- **`feed_page()`** — display user's posts feed

**Utilities:**
- **`get_headers()`** — adds JWT Bearer token to API requests
- **`create_transformed_url()`** — generates ImageKit transformation URLs (crop, overlay, filters)
- **`session_state`** — tracks logged-in user + JWT token
- **Sidebar:** user info, logout button, page navigation

---

### **images.py** — ImageKit Integration

**Purpose:** Media hosting and image transformations

**Features:**
- ✓ File upload to ImageKit CDN (not stored locally)
- ✓ Image/video transformations (crop, resize, overlay text, filters)
- ✓ Returns public URLs for embedded media

**API:** ImageKit Python SDK

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11 or higher
- `uv` package manager (or pip)
- ImageKit account (free tier available)

### 1. Clone & Navigate
```bash
cd /Users/akashkumar/myProject/fastApiProject
```

### 2. Create Virtual Environment
```bash
uv venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
uv pip install -r requirements.txt
# or manually:
uv pip install fastapi uvicorn sqlalchemy sqlalchemy[asyncio] aiosqlite fastapi-users fastapi-users-db-sqlalchemy streamlit imagekit
```

### 4. Configure Environment Variables
Create `.env` file in project root:
```
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=your-secret-key-here
IMAGEKIT_PUBLIC_KEY=your-imagekit-public-key
IMAGEKIT_PRIVATE_KEY=your-imagekit-private-key
IMAGEKIT_URL_ENDPOINT=your-imagekit-url-endpoint
```

### 5. Initialize Database
```bash
python -c "import asyncio; from app.db import create_db_and_tables; asyncio.run(create_db_and_tables())"
```

---

## ▶️ Running the Application

### Start Backend (FastAPI)
```bash
uvicorn app.app:app_route --reload --host 127.0.0.1 --port 8000
```

### Start Frontend (Streamlit) — in a new terminal
```bash
streamlit run app/frontend.py --server.port 8501
```

### Access
- **FastAPI API:** http://127.0.0.1:8000
- **API Docs:** http://127.0.0.1:8000/docs (Swagger UI)
- **Streamlit UI:** http://127.0.0.1:8501

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/jwt/login` | Login (JWT) |
| POST | `/auth/logout` | Logout |
| POST | `/auth/request-verify-token` | Request email verification |
| POST | `/auth/forgot-password` | Request password reset |

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload media + caption |
| GET | `/feeds` | Get user's feed |
| DELETE | `/posts/{post_id}` | Delete a post |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user info |
| PATCH | `/users/me` | Update user profile |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hello` | Health check |

---

## ✨ Features

### Current
- ✅ User registration & JWT authentication
- ✅ Email-based login
- ✅ Media upload (image/video) to ImageKit CDN
- ✅ Real-time image transformations (crop, text overlay, filters)
- ✅ Social feed (view all posts)
- ✅ Post deletion
- ✅ User session management
- ✅ Password reset & email verification

### Missing / TODO
- 🔲 Follow/unfollow users
- 🔲 Feed filtering (only followed users' posts)
- 🔲 Pagination
- 🔲 Comments & likes
- 🔲 User profiles
- 🔲 Search functionality
- 🔲 Frontend error handling (comprehensive)
- 🔲 Rate limiting
- 🔲 CORS setup for browser-based requests

---

## 🔮 Future Enhancements

1. **Social Features**
   - Follow/unfollow system
   - Like & comment on posts
   - User profiles with bio, profile picture

2. **Feed Improvements**
   - Pagination
   - Infinite scroll
   - Filter by date/user

3. **Admin & Moderation**
   - Admin dashboard
   - Content moderation
   - User ban/suspend

4. **Performance**
   - Caching (Redis)
   - Database query optimization
   - CDN edge caching

5. **Deployment**
   - Docker containerization
   - PostgreSQL (production)
   - Cloud hosting (AWS/Google Cloud)

---

## 📝 License

MIT License (or your chosen license)

---

## 👤 Author

Akash Kumar

---

**Last Updated:** November 30, 2025