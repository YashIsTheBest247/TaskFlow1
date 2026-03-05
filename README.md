# TaskFlow - Task Management System

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Installation

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd client
npm install
```

## Environment Setup

Copy `.env.example` to `.env` in the `backend` directory and update values:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and set your own `SECRET_KEY` for production use.

## Running the Application

### Initialize Database (First Time Only)

```bash
cd backend
python init_db.py
```

### Start Backend Server

```bash
cd backend
python run.py
```

Backend runs at: http://localhost:8800

### Start Frontend Server

```bash
cd client
npm run dev
```

Frontend runs at: http://localhost:3001

## Default Login Credentials

- Email: `admin@taskflow.com`
- Password: `admin123`

### Environment Variables Explanation
```bash
| Variable               | Description                         |
| ---------------------- | ---------------------------         |
| DATABASE_URL           | Database connection string          |
| SECRET_KEY             | Secret key used to sign JWT tokens  |
| ALGORITHM              | Algorithm used for token encryption |
| ACCESS_TOKEN_EXPIRE_MINUTES  |Access token expiry time       |
| REFRESH_TOKEN_EXPIRE_DAYS| Refresh token expiry time         |
```

### Example .env configuration:
```bash
DATABASE_URL=sqlite:///./taskflow.db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```


### Database Migration Steps
- TaskFlow uses Alembic for managing database migrations.
Generate Migration
```bash
cd backend
alembic revision --autogenerate -m "initial migration"
```
### Apply Migration
```bash
alembic upgrade head
```

### JWT Authentication Implementation
TaskFlow uses JSON Web Tokens (JWT) to authenticate users securely.

Authentication Flow
- User logs in using email and password.
- Backend verifies credentials.

- If valid, the server generates:
1. Access Token
2. Refresh Token

- Access token is sent with every API request.
Example request header:
```bash
Authorization: Bearer <access_token>
```

### Token Structure
Example payload:
``` bash
{
  "sub": "user_id",
  "exp": 1710000000
}
```

### Analytics Logic Calculation
```bash
Total Tasks = Number of tasks created by user

Completed Tasks = Tasks with status "completed"

Pending Tasks = Tasks with status "pending"

Completion Rate =
(Completed Tasks / Total Tasks) * 100
```

### Productivity Score Calculation
```bash
Productivity Score =
(Completed Tasks / Total Tasks) * 100
```
### Project Structure 
```bash 
TaskFlow
│
├── backend
│   ├── app
│   ├── alembic
│   ├── run.py
│   ├── init_db.py
│   ├── seed_data.py
│   ├── requirements.txt
│   └── taskflow.db
│
├── client
│   ├── src
│   │   ├── components
│   │   ├── pages
│   │   └── api.js
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```