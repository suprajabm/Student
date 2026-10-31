from sqlalchemy import Column, Integer, String, Date, ForeignKey
from database import Base


# Student Table
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String)
    semester = Column(Integer)


# Assignment Table
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    subject = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    priority = Column(String, default="Medium")
    status = Column(String, default="Pending")
    student_id = Column(Integer, ForeignKey("students.id"))


# Exam Table
class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    exam_date = Column(Date, nullable=False)
    exam_time = Column(String, nullable=False)
    location = Column(String)
    student_id = Column(Integer, ForeignKey("students.id"))