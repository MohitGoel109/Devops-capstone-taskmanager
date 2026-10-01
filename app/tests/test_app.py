import os

from app.app import create_app, db


def build_app():
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with test_app.app_context():
        db.create_all()
    return test_app


def test_health():
    app = build_app()
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_register_login_logout():
    app = build_app()
    client = app.test_client()

    response = client.post("/register", data={"username": "alice", "password": "secret"}, follow_redirects=True)
    assert response.status_code == 200

    response = client.post("/login", data={"username": "alice", "password": "secret"}, follow_redirects=True)
    assert response.status_code == 200

    response = client.get("/tasks")
    assert response.status_code == 200

    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


def test_task_create():
    app = build_app()
    client = app.test_client()
    client.post("/register", data={"username": "bob", "password": "pass"})

    response = client.post("/tasks/create", data={"title": "Study", "description": "Review Docker"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Study" in response.data


def test_task_list_api():
    app = build_app()
    client = app.test_client()
    client.post("/register", data={"username": "charlie", "password": "pw"})
    client.post("/tasks/create", data={"title": "Deploy", "description": "Run pipeline"})

    response = client.get("/api/tasks")
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Deploy"


def test_not_found_handler():
    app = build_app()
    client = app.test_client()
    response = client.get("/definitely-missing-page")
    assert response.status_code == 404
    assert b"404" in response.data
