from app.schemas.task import TaskCreate, TaskUpdate


def test_task_create_rejects_empty_title() -> None:
    try:
        TaskCreate(title="")
    except ValueError as error:
        assert "at least 1 character" in str(error)
    else:
        raise AssertionError("empty title should be rejected")


def test_task_update_accepts_partial_status_change() -> None:
    payload = TaskUpdate(status="done")
    assert payload.model_dump(exclude_unset=True) == {"status": "done"}
