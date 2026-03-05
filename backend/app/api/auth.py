from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserLogin, UserResponse
from app.models import User
from fastapi import Request

router = APIRouter()


@router.post("/register", response_model=dict)
def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    
    # Check if user exists
    existing_user = repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = repo.create(user_data)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Set access token cookie
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=1800  # 30 minutes
    )
    
    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800  # 7 days
    )
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "title": user.title,
        "isAdmin": user.isAdmin,
        "isActive": user.isActive,
        "created_at": user.created_at,
        "token": access_token
    }


@router.post("/login", response_model=dict)
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    
    # Get user
    user = repo.get_by_email(user_data.email)
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Set access token cookie
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=1800  # 30 minutes
    )
    
    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800  # 7 days
    )
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "title": user.title,
        "isAdmin": user.isAdmin,
        "isActive": user.isActive,
        "created_at": user.created_at,
        "token": access_token
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="token")
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=dict)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """Refresh access token using refresh token from cookie"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    from app.core.security import decode_token
    payload = decode_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    repo = UserRepository(db)
    user = repo.get_by_email(email)
    
    if not user or not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    new_access_token = create_access_token(data={"sub": user.email})
    
    # Set new access token cookie
    response.set_cookie(
        key="token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800
    )
    
    return {
        "message": "Token refreshed successfully",
        "access_token": new_access_token
    }
