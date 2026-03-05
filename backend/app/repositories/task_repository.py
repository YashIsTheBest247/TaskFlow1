from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from app.models import Task, TaskTeamMember, SubTask, TaskActivity, TaskHistory, User
from app.schemas import TaskCreate, TaskUpdate, SubTaskCreate, TaskActivityCreate
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, task_data: TaskCreate, user_id: int) -> Task:
        # Create task history entry
        task_dict = task_data.model_dump(exclude={"team"})
        
        db_task = Task(
            user_id=user_id,
            **task_dict
        )
        self.db.add(db_task)
        self.db.flush()

        # Add team members
        if task_data.team:
            for member_id in task_data.team:
                team_member = TaskTeamMember(task_id=db_task.id, user_id=member_id)
                self.db.add(team_member)

        # Create history
        history = TaskHistory(
            task_id=db_task.id,
            action_type="created",
            previous_state=None
        )
        self.db.add(history)

        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).options(
            joinedload(Task.team).joinedload(TaskTeamMember.user),
            joinedload(Task.sub_tasks),
            joinedload(Task.activities).joinedload(TaskActivity.user)
        ).filter(Task.id == task_id).first()

    def get_all(
        self,
        stage: Optional[str] = None,
        is_trashed: bool = False,
        search: str = "",
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        query = self.db.query(Task).options(
            joinedload(Task.team).joinedload(TaskTeamMember.user),
            joinedload(Task.sub_tasks)
        )

        query = query.filter(Task.isTrashed == is_trashed)

        if stage and stage.lower() != "all":
            query = query.filter(Task.stage == stage.lower())

        if search:
            query = query.filter(Task.title.ilike(f"%{search}%"))

        if user_id:
            query = query.filter(
                or_(
                    Task.user_id == user_id,
                    Task.team.any(TaskTeamMember.user_id == user_id)
                )
            )

        return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if not task:
            return None

        # Save previous state
        previous_state = {
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value if task.priority else None,
            "stage": task.stage.value if task.stage else None,
            "date": task.date.isoformat() if task.date else None,
        }

        update_data = task_data.model_dump(exclude_unset=True, exclude={"team"})
        for field, value in update_data.items():
            setattr(task, field, value)

        # Update team members
        if task_data.team is not None:
            # Remove existing team members
            self.db.query(TaskTeamMember).filter(TaskTeamMember.task_id == task_id).delete()
            # Add new team members
            for member_id in task_data.team:
                team_member = TaskTeamMember(task_id=task_id, user_id=member_id)
                self.db.add(team_member)

        # Create history
        history = TaskHistory(
            task_id=task_id,
            action_type="updated",
            previous_state=previous_state
        )
        self.db.add(history)

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if not task:
            return False

        # Create history before deletion
        history = TaskHistory(
            task_id=task_id,
            action_type="deleted",
            previous_state={"title": task.title, "stage": task.stage.value if task.stage else None}
        )
        self.db.add(history)
        self.db.commit()

        self.db.delete(task)
        self.db.commit()
        return True

    def trash(self, task_id: int) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if not task:
            return None
        task.isTrashed = True
        
        # Create history
        history = TaskHistory(
            task_id=task_id,
            action_type="trashed",
            previous_state=None
        )
        self.db.add(history)
        
        self.db.commit()
        self.db.refresh(task)
        return task

    def restore(self, task_id: int) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if not task:
            return None
        task.isTrashed = False
        
        # Create history
        history = TaskHistory(
            task_id=task_id,
            action_type="restored",
            previous_state=None
        )
        self.db.add(history)
        
        self.db.commit()
        self.db.refresh(task)
        return task

    def duplicate(self, task_id: int, user_id: int) -> Optional[Task]:
        original_task = self.get_by_id(task_id)
        if not original_task:
            return None

        new_task = Task(
            user_id=user_id,
            title=f"{original_task.title} (Copy)",
            description=original_task.description,
            priority=original_task.priority,
            stage=original_task.stage,
            date=original_task.date,
            assets=original_task.assets,
            links=original_task.links,
        )
        self.db.add(new_task)
        self.db.flush()

        # Copy team members
        for team_member in original_task.team:
            new_team_member = TaskTeamMember(task_id=new_task.id, user_id=team_member.user_id)
            self.db.add(new_team_member)

        # Create history
        history = TaskHistory(
            task_id=new_task.id,
            action_type="created",
            previous_state={"duplicated_from": task_id}
        )
        self.db.add(history)

        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def change_stage(self, task_id: int, stage: str) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if not task:
            return None

        previous_stage = task.stage.value if task.stage else None
        task.stage = stage

        # Create history
        history = TaskHistory(
            task_id=task_id,
            action_type="stage_changed",
            previous_state={"previous_stage": previous_stage, "new_stage": stage}
        )
        self.db.add(history)

        # Mark as completed if stage is completed
        if stage == "completed":
            history_completed = TaskHistory(
                task_id=task_id,
                action_type="completed",
                previous_state=None
            )
            self.db.add(history_completed)

        self.db.commit()
        self.db.refresh(task)
        return task

    def create_subtask(self, task_id: int, subtask_data: SubTaskCreate) -> Optional[SubTask]:
        task = self.get_by_id(task_id)
        if not task:
            return None

        subtask = SubTask(
            task_id=task_id,
            **subtask_data.model_dump()
        )
        self.db.add(subtask)
        self.db.commit()
        self.db.refresh(subtask)
        return subtask

    def change_subtask_status(self, task_id: int, subtask_id: int, status: bool) -> Optional[SubTask]:
        subtask = self.db.query(SubTask).filter(
            SubTask.id == subtask_id,
            SubTask.task_id == task_id
        ).first()
        
        if not subtask:
            return None

        subtask.completed = status
        self.db.commit()
        self.db.refresh(subtask)
        return subtask

    def create_activity(self, task_id: int, user_id: int, activity_data: TaskActivityCreate) -> Optional[TaskActivity]:
        task = self.get_by_id(task_id)
        if not task:
            return None

        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            **activity_data.model_dump()
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def get_dashboard_stats(self, user_id: Optional[int] = None, is_admin: bool = False) -> Dict:
        # Base query
        query = self.db.query(Task).filter(Task.isTrashed == False)
        
        if not is_admin and user_id:
            query = query.filter(
                or_(
                    Task.user_id == user_id,
                    Task.team.any(TaskTeamMember.user_id == user_id)
                )
            )

        # Total tasks
        total_tasks = query.count()

        # Tasks by stage
        tasks_by_stage = {}
        for stage in ["todo", "in progress", "completed"]:
            count = query.filter(Task.stage == stage).count()
            tasks_by_stage[stage] = count

        # Tasks by priority for chart
        graph_data = {}
        for priority in ["low", "normal", "medium", "high"]:
            count = query.filter(Task.priority == priority).count()
            graph_data[priority] = count

        # Last 10 tasks
        last_10_tasks = query.order_by(Task.created_at.desc()).limit(10).all()

        # Users (only for admin)
        users = []
        if is_admin:
            users = self.db.query(User).order_by(User.created_at.desc()).limit(10).all()

        return {
            "totalTasks": total_tasks,
            "tasks": tasks_by_stage,
            "graphData": graph_data,
            "last10Task": last_10_tasks,
            "users": users
        }
