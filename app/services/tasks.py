from collections.abc import Mapping
from datetime import UTC, datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def _base_query() -> Select[tuple[Task]]:
    return select(Task)


def list_tasks(
    db: Session,
    *,
    status: str | None,
    priority: str | None,
    q: str | None,
    sort_by: str,
    sort_order: str,
    limit: int,
    offset: int,
) -> tuple[list[Task], int]:
    query = _base_query()
    count_query = select(func.count()).select_from(Task)
    filters = []
    if status:
        filters.append(Task.status == status)
    if priority:
        filters.append(Task.priority == priority)
    if q:
        filters.append(Task.title.ilike(f"%{q}%"))
    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)

    sort_column = {
        "priority": Task.priority,
        "due_date": Task.due_date,
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
    }[sort_by]
    query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
    items = list(db.scalars(query.limit(limit).offset(offset)).all())
    total = db.scalar(count_query) or 0
    return items, total


def create_task(db: Session, payload: TaskCreate) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, payload: TaskUpdate) -> Task:
    changes: Mapping[str, object] = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(task, field, value)
    task.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
