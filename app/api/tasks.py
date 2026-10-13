from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.task import Task
from app.schemas.task import Priority, Status, TaskCreate, TaskList, TaskRead, TaskUpdate
from app.services.tasks import create_task, delete_task, list_tasks, update_task

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
DbSession = Annotated[Session, Depends(get_db)]


def get_task_or_404(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=404, detail={"code": "task_not_found", "message": "Task not found"}
        )
    return task


@router.get("", response_model=TaskList)
def get_tasks(
    db: DbSession,
    status_filter: Annotated[Status | None, Query(alias="status")] = None,
    priority: Priority | None = None,
    q: Annotated[str | None, Query(max_length=120)] = None,
    sort_by: Literal["priority", "due_date", "created_at", "updated_at"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TaskList:
    items, total = list_tasks(
        db,
        status=status_filter,
        priority=priority,
        q=q,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    return TaskList(
        items=[TaskRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def post_task(payload: TaskCreate, db: DbSession) -> Task:
    return create_task(db, payload)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: DbSession) -> Task:
    return get_task_or_404(db, task_id)


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(task_id: int, payload: TaskUpdate, db: DbSession) -> Task:
    return update_task(db, get_task_or_404(db, task_id), payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task(task_id: int, db: DbSession) -> Response:
    delete_task(db, get_task_or_404(db, task_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
