from pydantic import BaseModel, EmailStr
from datetime import date


# Student Schemas
class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    semester: int


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    department: str
    semester: int

    class Config:
        from_attributes = True


# Assignment Schemas
class AssignmentCreate(BaseModel):
    title: str
    description: str
    subject: str
    due_date: date
    priority: str = "Medium"
    status: str = "Pending"
    student_id: int


class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: str
    subject: str
    due_date: date
    priority: str
    status: str
    student_id: int

    class Config:
        from_attributes = True


# Exam Schemas
class ExamCreate(BaseModel):
    subject: str
    exam_date: date
    exam_time: str
    location: str
    student_id: int


class ExamResponse(BaseModel):
    id: int
    subject: str
    exam_date: date
    exam_time: str
    location: str
    student_id: int

    class Config:
        from_attributes = True