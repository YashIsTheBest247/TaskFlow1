from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PriorityEnum(str, enum.Enum):
    low = "low"
    normal = "normal"
    medium = "medium"
    high = "high"


class StageEnum(str, enum.Enum):
    todo = "todo"
    in_progress = "in progress"
    completed = "completed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(SQLEnum(PriorityEnum), default=PriorityEnum.normal, index=True)
    stage = Column(SQLEnum(StageEnum), default=StageEnum.todo, index=True)
    date = Column(DateTime(timezone=True), nullable=True)
    assets = Column(JSON, default=list)
    links = Column(Text, nullable=True)
    isTrashed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="tasks", foreign_keys=[user_id])
    team = relationship("TaskTeamMember", back_populates="task", cascade="all, delete-orphan")
    sub_tasks = relationship("SubTask", back_populates="task", cascade="all, delete-orphan")
    activities = relationship("TaskActivity", back_populates="task", cascade="all, delete-orphan")
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="task", cascade="all, delete-orphan")


class TaskTeamMember(Base):
    __tablename__ = "task_team_members"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Relationships
    task = relationship("Task", back_populates="team")
    user = relationship("User", back_populates="assigned_tasks")


class SubTask(Base):
    __tablename__ = "sub_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    tag = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="sub_tasks")


class TaskActivity(Base):
    __tablename__ = "task_activities"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False)
    activity = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="activities")
    user = relationship("User", back_populates="activities")


class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False, index=True)
    previous_state = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="history")
