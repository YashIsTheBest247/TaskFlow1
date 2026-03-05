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
