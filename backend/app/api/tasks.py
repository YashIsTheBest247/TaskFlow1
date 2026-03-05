from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user_from_cookie
from app.repositories.task_repository import TaskRepository
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    SubTaskCreate,
    TaskActivityCreate,
    ChangeStage,
    ChangeSubTaskStatus
)
from app.models import User
from typing import List, Optional

router = APIRouter()


def serialize_task(task):
    """Helper function to serialize task with team members"""
    return {
        "id": task.id,
        "_id": str(task.id),
        "title": task.title,
        "description": task.description,
        "priority": task.priority.value if task.priority else None,
        "stage": task.stage.value if task.stage else None,
        "date": task.date,
        "assets": task.assets or [],
        "links": task.links,
        "isTrashed": task.isTrashed,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "team": [
            {
                "id": tm.user.id,
                "_id": str(tm.user.id),
                "name": tm.user.name,
                "email": tm.user.email,
                "role": tm.user.role,
                "title": tm.user.title,
                "isActive": tm.user.isActive
            }
            for tm in task.team
        ],
        "subTasks": [
            {
                "id": st.id,
                "_id": str(st.id),
                "title": st.title,
                "tag": st.tag,
                "date": st.date,
                "completed": st.completed,
                "created_at": st.created_at
            }
            for st in task.sub_tasks
        ],
        "activities": [
            {
                "id": act.id,
                "_id": str(act.id),
                "type": act.type,
                "activity": act.activity,
                "date": act.date,
                "user": {
                    "id": act.user.id,
                    "name": act.user.name,
                    "email": act.user.email
                }
            }
            for act in task.activities
        ]
    }


@router.post("/create", response_model=dict)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.create(task_data, current_user.id)
    
    return {
        "message": "Task created successfully",
        "task": serialize_task(task)
    }


@router.get("", response_model=dict)
def get_all_tasks(
    stage: str = Query("all"),
    isTrashed: str = Query("false"),
    search: str = Query(""),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    is_trashed_bool = isTrashed.lower() == "true"
    
    # Non-admin users only see their own tasks
    user_id = None if current_user.isAdmin else current_user.id
    
    tasks = repo.get_all(
        stage=stage,
        is_trashed=is_trashed_bool,
        search=search,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "tasks": [serialize_task(task) for task in tasks],
        "skip": skip,
        "limit": limit,
        "total": len(tasks)
    }


@router.get("/dashboard", response_model=dict)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    stats = repo.get_dashboard_stats(
        user_id=current_user.id,
        is_admin=current_user.isAdmin
    )
    
    # Serialize last 10 tasks
    serialized_last_10 = []
    for task in stats["last10Task"]:
        serialized_last_10.append({
            "_id": str(task.id),
            "title": task.title,
            "priority": task.priority.value if task.priority else None,
            "stage": task.stage.value if task.stage else None,
            "date": task.date,
            "team": [
                {
                    "id": tm.user.id,
                    "name": tm.user.name,
                    "email": tm.user.email,
                    "role": tm.user.role
                }
                for tm in task.team
            ]
        })
    
    # Serialize users
    serialized_users = []
    for user in stats["users"]:
        serialized_users.append({
            "_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "isActive": user.isActive,
            "createdAt": user.created_at
        })
    
    return {
        "totalTasks": stats["totalTasks"],
        "tasks": stats["tasks"],
        "graphData": stats["graphData"],
        "last10Task": serialized_last_10,
        "users": serialized_users
    }


@router.get("/{task_id}", response_model=dict)
def get_single_task(
    task_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to this task
    if not current_user.isAdmin:
        has_access = (
            task.user_id == current_user.id or
            any(tm.user_id == current_user.id for tm in task.team)
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this task"
            )
    
    return {
        "task": serialize_task(task)
    }


@router.put("/update/{task_id}", response_model=dict)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to update this task
    if not current_user.isAdmin and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    updated_task = repo.update(task_id, task_data)
    
    return {
        "message": "Task updated successfully",
        "task": serialize_task(updated_task)
    }


@router.put("/{task_id}", response_model=dict)
def trash_task(
    task_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access
    if not current_user.isAdmin and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to trash this task"
        )
    
    trashed_task = repo.trash(task_id)
    
    return {
        "message": "Task trashed successfully",
        "task": serialize_task(trashed_task)
    }


@router.delete("/delete-restore/{task_id}", response_model=dict)
def delete_or_restore_task(
    task_id: int,
    actionType: str = Query(...),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access
    if not current_user.isAdmin and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    
    if actionType == "delete":
        success = repo.delete(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )
        return {"message": "Task deleted successfully"}
    
    elif actionType == "restore":
        restored_task = repo.restore(task_id)
        return {
            "message": "Task restored successfully",
            "task": serialize_task(restored_task)
        }
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid action type"
    )


@router.post("/duplicate/{task_id}", response_model=dict)
def duplicate_task(
    task_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access
    if not current_user.isAdmin:
        has_access = (
            task.user_id == current_user.id or
            any(tm.user_id == current_user.id for tm in task.team)
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to duplicate this task"
            )
    
    duplicated_task = repo.duplicate(task_id, current_user.id)
    
    return {
        "message": "Task duplicated successfully",
        "task": serialize_task(duplicated_task)
    }


@router.put("/change-stage/{task_id}", response_model=dict)
def change_task_stage(
    task_id: int,
    stage_data: ChangeStage,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access
    if not current_user.isAdmin:
        has_access = (
            task.user_id == current_user.id or
            any(tm.user_id == current_user.id for tm in task.team)
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this task"
            )
    
    updated_task = repo.change_stage(task_id, stage_data.stage.value)
    
    return {
        "message": "Task stage updated successfully",
        "task": serialize_task(updated_task)
    }


@router.put("/create-subtask/{task_id}", response_model=dict)
def create_subtask(
    task_id: int,
    subtask_data: SubTaskCreate,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access
    if not current_user.isAdmin:
        has_access = (
            task.user_id == current_user.id or
            any(tm.user_id == current_user.id for tm in task.team)
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add subtask"
            )
    
    subtask = repo.create_subtask(task_id, subtask_data)
    
    return {
        "message": "Subtask created successfully",
        "subtask": {
            "id": subtask.id,
            "_id": str(subtask.id),
            "title": subtask.title,
            "tag": subtask.tag,
            "date": subtask.date,
            "completed": subtask.completed,
            "created_at": subtask.created_at
        }
    }


@router.put("/change-status/{task_id}/{subtask_id}", response_model=dict)
def change_subtask_status(
    task_id: int,
    subtask_id: int,
    status_data: ChangeSubTaskStatus,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access
    if not current_user.isAdmin:
        has_access = (
            task.user_id == current_user.id or
            any(tm.user_id == current_user.id for tm in task.team)
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update subtask"
            )
    
    subtask = repo.change_subtask_status(task_id, subtask_id, status_data.status)
    
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found"
        )
    
    return {
        "message": "Subtask status updated successfully",
        "subtask": {
            "id": subtask.id,
            "completed": subtask.completed
        }
    }


@router.post("/activity/{task_id}", response_model=dict)
def post_task_activity(
    task_id: int,
    activity_data: TaskActivityCreate,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access
    if not current_user.isAdmin:
        has_access = (
            task.user_id == current_user.id or
            any(tm.user_id == current_user.id for tm in task.team)
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add activity"
            )
    
    activity = repo.create_activity(task_id, current_user.id, activity_data)
    
    return {
        "message": "Activity posted successfully",
        "activity": {
            "id": activity.id,
            "type": activity.type,
            "activity": activity.activity,
            "date": activity.date,
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email
            }
        }
    }


@router.patch("/complete/{task_id}", response_model=dict)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Mark task as completed"""
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access
    if not current_user.isAdmin:
        has_access = (
            task.user_id == current_user.id or
            any(tm.user_id == current_user.id for tm in task.team)
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to complete this task"
            )
    
    updated_task = repo.change_stage(task_id, "completed")
    
    return {
        "message": "Task marked as completed",
        "task": serialize_task(updated_task)
    }


@router.patch("/archive/{task_id}", response_model=dict)
def archive_task(
    task_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Archive task (move to trash)"""
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access
    if not current_user.isAdmin and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive this task"
        )
    
    archived_task = repo.trash(task_id)
    
    return {
        "message": "Task archived successfully",
        "task": serialize_task(archived_task)
    }
