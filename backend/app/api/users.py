from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.utils.dependencies import get_current_user_from_cookie, get_current_admin_user
from app.repositories.user_repository import UserRepository
from app.schemas import UserUpdate, UserResponse, UserSimple, ChangePassword
from app.models import User, Task, TaskTeamMember, Notification
from typing import List

router = APIRouter()


@router.get("/get-team", response_model=List[UserSimple])
def get_team(
    search: str = Query(""),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    users = repo.get_all(search=search)
    return users


@router.put("/profile", response_model=dict)
def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    
    # Only allow updating own profile unless admin
    if not current_user.isAdmin:
        # Remove admin-only fields
        user_data.isActive = None
        user_data.role = None
    
    updated_user = repo.update(current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": updated_user.id,
            "name": updated_user.name,
            "email": updated_user.email,
            "role": updated_user.role,
            "title": updated_user.title,
            "isAdmin": updated_user.isAdmin,
            "isActive": updated_user.isActive,
        }
    }


@router.put("/{user_id}", response_model=dict)
def user_action(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    updated_user = repo.update(user_id, user_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "message": "User updated successfully",
        "user": {
            "id": updated_user.id,
            "name": updated_user.name,
            "email": updated_user.email,
            "role": updated_user.role,
            "isActive": updated_user.isActive,
        }
    }


@router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    repo = UserRepository(db)
    success = repo.delete(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}


@router.put("/change-password", response_model=dict)
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    updated_user = repo.change_password(current_user.id, password_data.password)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Password changed successfully"}


@router.get("/get-status", response_model=dict)
def get_user_task_status(
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    # Get task counts by stage for current user
    todo_count = db.query(Task).filter(
        Task.stage == "todo",
        Task.isTrashed == False,
        (Task.user_id == current_user.id) | (Task.team.any(TaskTeamMember.user_id == current_user.id))
    ).count()
    
    in_progress_count = db.query(Task).filter(
        Task.stage == "in progress",
        Task.isTrashed == False,
        (Task.user_id == current_user.id) | (Task.team.any(TaskTeamMember.user_id == current_user.id))
    ).count()
    
    completed_count = db.query(Task).filter(
        Task.stage == "completed",
        Task.isTrashed == False,
        (Task.user_id == current_user.id) | (Task.team.any(TaskTeamMember.user_id == current_user.id))
    ).count()
    
    return {
        "todo": todo_count,
        "in_progress": in_progress_count,
        "completed": completed_count
    }


@router.get("/notifications", response_model=List[dict])
def get_notifications(
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(20).all()
    
    return [
        {
            "id": n.id,
            "team": n.team,
            "text": n.text,
            "task": n.task,
            "notiType": n.notiType,
            "isRead": n.isRead,
            "created_at": n.created_at
        }
        for n in notifications
    ]


@router.put("/read-noti", response_model=dict)
def mark_notification_as_read(
    isReadType: str = Query(...),
    id: int = Query(None),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    if isReadType == "all":
        # Mark all notifications as read
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).all()
        
        for notification in notifications:
            if current_user.id not in notification.isRead:
                notification.isRead.append(current_user.id)
        
        db.commit()
        return {"message": "All notifications marked as read"}
    
    elif isReadType == "one" and id:
        # Mark single notification as read
        notification = db.query(Notification).filter(
            Notification.id == id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        if current_user.id not in notification.isRead:
            notification.isRead.append(current_user.id)
        
        db.commit()
        return {"message": "Notification marked as read"}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid parameters"
    )
