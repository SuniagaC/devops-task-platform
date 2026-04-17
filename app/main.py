from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from .db import Base, engine, get_db
from .schemas import TaskCreate, TaskResponse, TaskUpdate
from .crud import create_task, list_tasks, get_task, update_task, delete_task
from .metrics import PrometheusMiddleware, metrics_endpoint

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevOps Task Platform", version="1.0.0")
app.add_middleware(PrometheusMiddleware)


@app.get("/")
def root():
    return {"message": "DevOps Task Platform"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database not ready: {exc}")


@app.get("/metrics")
def metrics():
    return metrics_endpoint()


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_new_task(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db, task)


@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return list_tasks(db)


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_single_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_existing_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = update_task(db, task_id, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def remove_task(task_id: int, db: Session = Depends(get_db)):
    deleted = delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return
