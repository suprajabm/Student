from datetime import date, timedelta
from datetime import date
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models
import schemas

app = FastAPI()

Base.metadata.create_all(bind=engine)


# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Home API
@app.get("/")
def home():
    return {"message": "Student Management System Backend is running!"}


# Add a student
@app.post("/students/", response_model=schemas.StudentResponse)
def add_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):

    existing_student = db.query(models.Student).filter(
        models.Student.email == student.email
    ).first()

    if existing_student:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_student = models.Student(**student.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


# View all students
@app.get("/students/", response_model=list[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


# Add an assignment
@app.post("/assignments/", response_model=schemas.AssignmentResponse)
def add_assignment(
    assignment: schemas.AssignmentCreate,
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(
        models.Student.id == assignment.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    new_assignment = models.Assignment(**assignment.model_dump())

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment


# View all assignments
@app.get("/assignments/", response_model=list[schemas.AssignmentResponse])
def get_assignments(db: Session = Depends(get_db)):
    return db.query(models.Assignment).all()

# Update an assignment
@app.put("/assignments/{assignment_id}")
def update_assignment(
    assignment_id: int,
    updated_data: schemas.AssignmentCreate,
    db: Session = Depends(get_db)
):
    assignment = db.query(models.Assignment).filter(
        models.Assignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    student = db.query(models.Student).filter(
        models.Student.id == updated_data.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for key, value in updated_data.model_dump().items():
        setattr(assignment, key, value)

    db.commit()
    db.refresh(assignment)

    return assignment


# Delete an assignment
@app.delete("/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    assignment = db.query(models.Assignment).filter(
        models.Assignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(assignment)
    db.commit()

    return {"message": "Assignment deleted successfully"}

# Add an exam
@app.post("/exams/", response_model=schemas.ExamResponse)
def add_exam(exam: schemas.ExamCreate, db: Session = Depends(get_db)):

    student = db.query(models.Student).filter(
        models.Student.id == exam.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    new_exam = models.Exam(**exam.model_dump())

    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)

    return new_exam


# View all exams
@app.get("/exams/", response_model=list[schemas.ExamResponse])
def get_exams(db: Session = Depends(get_db)):
    return db.query(models.Exam).all()


# Delete an exam
@app.delete("/exams/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):

    exam = db.query(models.Exam).filter(
        models.Exam.id == exam_id
    ).first()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    db.delete(exam)
    db.commit()

    return {"message": "Exam deleted successfully"}

# Smart Task Prioritization
@app.get("/smart-priorities/")
def smart_priorities(db: Session = Depends(get_db)):

    today = date.today()
    tasks = []

    # Check pending assignments
    assignments = db.query(models.Assignment).filter(
        models.Assignment.status != "Completed"
    ).all()

    for assignment in assignments:

        days_left = (assignment.due_date - today).days

        priority_score = {
            "High": 30,
            "Medium": 20,
            "Low": 10
        }.get(assignment.priority, 10)

        if days_left < 0:
            urgency_score = 50
        elif days_left == 0:
            urgency_score = 45
        elif days_left <= 2:
            urgency_score = 40
        elif days_left <= 7:
            urgency_score = 30
        else:
            urgency_score = 10

        total_score = priority_score + urgency_score

        tasks.append({
            "task": assignment.title,
            "subject": assignment.subject,
            "type": "Assignment",
            "due_date": str(assignment.due_date),
            "days_left": days_left,
            "priority_score": total_score
        })

    # Check upcoming exams
    exams = db.query(models.Exam).all()

    for exam in exams:

        days_left = (exam.exam_date - today).days

        if days_left < 0:
            urgency_score = 50
        elif days_left == 0:
            urgency_score = 45
        elif days_left <= 2:
            urgency_score = 40
        elif days_left <= 7:
            urgency_score = 30
        else:
            urgency_score = 10

        tasks.append({
            "task": exam.subject + " Exam",
            "subject": exam.subject,
            "type": "Exam",
            "due_date": str(exam.exam_date),
            "days_left": days_left,
            "priority_score": urgency_score + 20
        })

    # Sort tasks by highest priority score
    tasks.sort(
        key=lambda x: x["priority_score"],
        reverse=True
    )

    return {
        "message": "Tasks prioritized successfully",
        "prioritized_tasks": tasks
    }

# Missed Task Rescheduling
@app.get("/reschedule-missed-tasks/")
def reschedule_missed_tasks(db: Session = Depends(get_db)):

    today = date.today()
    missed_tasks = []

    assignments = db.query(models.Assignment).filter(
        models.Assignment.status != "Completed"
    ).all()

    for assignment in assignments:

        if assignment.due_date < today:

            new_due_date = today + timedelta(days=2)

            missed_tasks.append({
                "assignment_id": assignment.id,
                "title": assignment.title,
                "old_due_date": str(assignment.due_date),
                "suggested_due_date": str(new_due_date),
                "message": "This assignment is overdue. A new deadline is suggested."
            })

    return {
        "message": "Missed tasks checked successfully",
        "missed_tasks": missed_tasks
    }
# Workload Analysis
@app.get("/workload/{student_id}")
def workload_analysis(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    pending_assignments = db.query(models.Assignment).filter(
        models.Assignment.student_id == student_id,
        models.Assignment.status != "Completed"
    ).all()

    upcoming_exams = db.query(models.Exam).filter(
        models.Exam.student_id == student_id,
        models.Exam.exam_date >= date.today()
    ).all()

    return {
        "student_name": student.name,
        "pending_assignments": len(pending_assignments),
        "upcoming_exams": len(upcoming_exams),
        "total_pending_tasks": len(pending_assignments) + len(upcoming_exams),
        "assignment_details": [
            {
                "title": a.title,
                "subject": a.subject,
                "due_date": str(a.due_date)
            }
            for a in pending_assignments
        ],
        "exam_details": [
            {
                "subject": e.subject,
                "exam_date": str(e.exam_date)
            }
            for e in upcoming_exams
        ]
    }