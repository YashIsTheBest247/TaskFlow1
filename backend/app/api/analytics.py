from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from app.core.database import get_db
from app.utils.dependencies import get_current_user_from_cookie
from app.models import User, Task, TaskHistory
from datetime import datetime, timedelta
from typing import Dict, List

router = APIRouter()


@router.get("/summary")
def get_analytics_summary(
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Get summary analytics for authenticated user"""
    
    # Total tasks
    total_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.isTrashed == False
    ).count()
    
    # Completed tasks
    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.stage == "completed",
        Task.isTrashed == False
    ).count()
    
    # Pending tasks (todo + in progress)
    pending_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.stage.in_(["todo", "in progress"]),
        Task.isTrashed == False
    ).count()
    
    # Archived tasks
    archived_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.isTrashed == True
    ).count()
    
    # Completion percentage
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_percentage": round(completion_percentage, 2),
        "pending_tasks": pending_tasks,
        "archived_tasks": archived_tasks
    }


@router.get("/over-time")
def get_analytics_over_time(
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Get tasks completed over time"""
    
    # Last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    daily_completions = db.query(
        func.date(TaskHistory.timestamp).label('date'),
        func.count(TaskHistory.id).label('count')
    ).join(Task).filter(
        Task.user_id == current_user.id,
        TaskHistory.action_type == "completed",
        TaskHistory.timestamp >= thirty_days_ago
    ).group_by(func.date(TaskHistory.timestamp)).all()
    
    # Last 12 weeks
    twelve_weeks_ago = datetime.now() - timedelta(weeks=12)
    weekly_completions = db.query(
        func.strftime('%Y-%W', TaskHistory.timestamp).label('week'),
        func.count(TaskHistory.id).label('count')
    ).join(Task).filter(
        Task.user_id == current_user.id,
        TaskHistory.action_type == "completed",
        TaskHistory.timestamp >= twelve_weeks_ago
    ).group_by(func.strftime('%Y-%W', TaskHistory.timestamp)).all()
    
    # Last 12 months
    twelve_months_ago = datetime.now() - timedelta(days=365)
    monthly_completions = db.query(
        func.strftime('%Y-%m', TaskHistory.timestamp).label('month'),
        func.count(TaskHistory.id).label('count')
    ).join(Task).filter(
        Task.user_id == current_user.id,
        TaskHistory.action_type == "completed",
        TaskHistory.timestamp >= twelve_months_ago
    ).group_by(func.strftime('%Y-%m', TaskHistory.timestamp)).all()
    
    return {
        "daily": [{"date": str(d.date), "count": d.count} for d in daily_completions],
        "weekly": [{"week": w.week, "count": w.count} for w in weekly_completions],
        "monthly": [{"month": m.month, "count": m.count} for m in monthly_completions]
    }


@router.get("/productivity")
def get_productivity_analytics(
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Get productivity analytics"""
    
    # Most productive day of week
    day_completions = db.query(
        extract('dow', TaskHistory.timestamp).label('day_of_week'),
        func.count(TaskHistory.id).label('count')
    ).join(Task).filter(
        Task.user_id == current_user.id,
        TaskHistory.action_type == "completed"
    ).group_by(extract('dow', TaskHistory.timestamp)).order_by(func.count(TaskHistory.id).desc()).first()
    
    days_map = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
    most_productive_day = days_map.get(int(day_completions.day_of_week), 'N/A') if day_completions else 'N/A'
    
    # Average completion time
    completion_times = db.query(
        Task.created_at,
        TaskHistory.timestamp
    ).join(TaskHistory).filter(
        Task.user_id == current_user.id,
        TaskHistory.action_type == "completed"
    ).all()
    
    if completion_times:
        total_hours = sum([(h.timestamp - h.created_at).total_seconds() / 3600 for h in completion_times])
        avg_completion_hours = total_hours / len(completion_times)
        avg_completion_days = avg_completion_hours / 24
    else:
        avg_completion_days = 0
    
    # Priority distribution
    priority_dist = db.query(
        Task.priority,
        func.count(Task.id).label('count')
    ).filter(
        Task.user_id == current_user.id,
        Task.isTrashed == False
    ).group_by(Task.priority).all()
    
    priority_distribution = {p.priority.value: p.count for p in priority_dist}
    
    # Productivity score calculation
    total_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.isTrashed == False
    ).count()
    
    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.stage == "completed",
        Task.isTrashed == False
    ).count()
    
    # Tasks completed on time (before due date)
    on_time_tasks = db.query(Task).join(TaskHistory).filter(
        Task.user_id == current_user.id,
        TaskHistory.action_type == "completed",
        Task.date.isnot(None),
        TaskHistory.timestamp <= Task.date
    ).count()
    
    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 50
        on_time_rate = (on_time_tasks / max(1, completed_tasks)) * 30
        speed_score = (1 / max(1, avg_completion_days)) * 20
        productivity_score = min(100, max(0, completion_rate + on_time_rate + speed_score))
    else:
        productivity_score = 0
    
    return {
        "most_productive_day": most_productive_day,
        "average_completion_time_days": round(avg_completion_days, 2),
        "priority_distribution": priority_distribution,
        "productivity_score": round(productivity_score, 2)
    }
