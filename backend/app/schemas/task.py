from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.task import PriorityEnum, StageEnum


class SubTaskBase(BaseModel):
    title: str
    tag: Optional[str] = None
    date: Optional[datetime] = None
    
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class SubTaskCreate(SubTaskBase):
    pass


class SubTaskResponse(SubTaskBase):
    id: int
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TaskActivityBase(BaseModel):
    type: str
    activity: str


class TaskActivityCreate(TaskActivityBase):
    pass


class TaskActivityResponse(TaskActivityBase):
    id: int
    date: datetime
    user: dict

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.normal
    stage: StageEnum = StageEnum.todo
    date: Optional[datetime] = None
    assets: Optional[List[str]] = []
    links: Optional[str] = None
    
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class TaskCreate(TaskBase):
    team: Optional[List[int]] = []


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    stage: Optional[StageEnum] = None
    date: Optional[datetime] = None
    assets: Optional[List[str]] = None
    links: Optional[str] = None
    team: Optional[List[int]] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    isTrashed: bool
    created_at: datetime
    updated_at: Optional[datetime]
    team: List[dict]
    subTasks: List[SubTaskResponse]
    activities: List[dict]

    class Config:
        from_attributes = True


class TaskSimple(BaseModel):
    id: int
    title: str
    priority: str
    stage: str
    date: Optional[datetime]
    team: List[dict]

    class Config:
        from_attributes = True


class ChangeStage(BaseModel):
    stage: StageEnum


class ChangeSubTaskStatus(BaseModel):
    status: bool
