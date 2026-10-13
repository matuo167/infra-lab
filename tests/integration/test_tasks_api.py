import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_task_lifecycle_and_persistence(client: TestClient) -> None:
    created = client.post(
        "/api/tasks",
        json={
            "title": "Write runbook",
            "description": "Document the deployment rollback path",
            "priority": "high",
            "due_date": "2026-12-31",
        },
    )
    assert created.status_code == 201
    task = created.json()
    assert task["status"] == "todo"
    assert task["priority"] == "high"

    task_id = task["id"]
    fetched = client.get(f"/api/tasks/{task_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Write runbook"

    updated = client.patch(f"/api/tasks/{task_id}", json={"status": "done"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"

    filtered = client.get("/api/tasks", params={"status": "done", "limit": 1})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["id"] == task_id

    deleted = client.delete(f"/api/tasks/{task_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_validation_and_pagination(client: TestClient) -> None:
    for index in range(3):
        response = client.post("/api/tasks", json={"title": f"Task {index}", "priority": "low"})
        assert response.status_code == 201

    invalid = client.post("/api/tasks", json={"title": "", "status": "unknown"})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "validation_error"

    page = client.get("/api/tasks", params={"limit": 2, "offset": 1})
    assert page.status_code == 200
    assert page.json()["total"] == 3
    assert len(page.json()["items"]) == 2


def test_health_and_metrics(client: TestClient) -> None:
    assert client.get("/health/live").json() == {"status": "ok"}
    assert client.get("/health/ready").status_code == 200
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "http_requests_total" in metrics.text


def test_missing_task_has_consistent_error(client: TestClient) -> None:
    response = client.get("/api/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "task_not_found"
