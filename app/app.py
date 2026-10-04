import os
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
from sqlalchemy import inspect, text
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()

PRIORITIES = ("High", "Medium", "Low")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    tasks = db.relationship("Task", backref="user", cascade="all, delete-orphan")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.String(10), default="Medium", nullable=False, server_default="Medium")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


def clean_priority(value):
    """Return a valid priority string, or None if the value is not allowed."""
    value = (value or "Medium").strip().capitalize()
    return value if value in PRIORITIES else None


def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "created_at": task.created_at.isoformat(),
    }


def ensure_priority_column():
    """Add the priority column to an existing tasks table (create_all does not alter tables)."""
    columns = [c["name"] for c in inspect(db.engine).get_columns("tasks")]
    if "priority" not in columns:
        try:
            with db.engine.begin() as conn:
                conn.execute(
                    text("ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'Medium'")
                )
        except Exception:
            # Another pod may have added the column at the same moment.
            pass


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///taskmanager.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    PrometheusMetrics(app)

    @app.get("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("tasks_page"))
        return redirect(url_for("login"))

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                return render_template("register.html", error="Username and password are required."), 400

            existing = db.session.execute(
                db.select(User).where(User.username == username)
            ).scalar_one_or_none()
            if existing:
                return render_template("register.html", error="Username already exists."), 409

            user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("tasks_page"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            user = db.session.execute(
                db.select(User).where(User.username == username)
            ).scalar_one_or_none()

            if user and check_password_hash(user.password_hash, password):
                session["user_id"] = user.id
                session["username"] = user.username
                return redirect(url_for("tasks_page"))

            return render_template("login.html", error="Invalid username or password."), 401

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/tasks")
    def tasks_page():
        if "user_id" not in session:
            return redirect(url_for("login"))

        tasks = Task.query.filter_by(user_id=session["user_id"]).order_by(Task.created_at.desc()).all()
        return render_template("tasks.html", tasks=tasks, username=session["username"])

    @app.route("/api/tasks", methods=["GET", "POST"])
    def api_tasks():
        if "user_id" not in session:
            return jsonify({"error": "unauthorized"}), 401

        if request.method == "GET":
            tasks = Task.query.filter_by(user_id=session["user_id"]).order_by(Task.created_at.desc()).all()
            return jsonify([task_to_dict(t) for t in tasks])

        payload = request.get_json(silent=True) or {}
        title = (payload.get("title") or "").strip()
        description = (payload.get("description") or "").strip()

        if not title:
            return jsonify({"error": "title is required"}), 400

        priority = clean_priority(payload.get("priority"))
        if priority is None:
            return jsonify({"error": "priority must be High, Medium or Low"}), 400

        task = Task(
            title=title,
            description=description or None,
            completed=False,
            priority=priority,
            user_id=session["user_id"],
        )
        db.session.add(task)
        db.session.commit()

        return jsonify(task_to_dict(task)), 201

    @app.route("/api/tasks/<int:task_id>", methods=["GET", "PUT", "DELETE"])
    def api_task_detail(task_id):
        if "user_id" not in session:
            return jsonify({"error": "unauthorized"}), 401

        task = Task.query.filter_by(id=task_id, user_id=session["user_id"]).first()
        if not task:
            return jsonify({"error": "task not found"}), 404

        if request.method == "GET":
            return jsonify(task_to_dict(task))

        if request.method == "PUT":
            payload = request.get_json(silent=True) or {}
            if "title" in payload and str(payload["title"]).strip():
                task.title = str(payload["title"]).strip()
            if "description" in payload:
                task.description = payload["description"]
            if "completed" in payload:
                task.completed = bool(payload.get("completed"))
            if "priority" in payload:
                priority = clean_priority(payload["priority"])
                if priority is None:
                    return jsonify({"error": "priority must be High, Medium or Low"}), 400
                task.priority = priority

            if not task.title:
                return jsonify({"error": "title is required"}), 400

            db.session.commit()
            return jsonify(task_to_dict(task))

        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "task deleted"})

    @app.route("/tasks/create", methods=["POST"])
    def create_task():
        if "user_id" not in session:
            return redirect(url_for("login"))

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title:
            tasks = Task.query.filter_by(user_id=session["user_id"]).order_by(Task.created_at.desc()).all()
            return render_template("tasks.html", error="Task title is required", tasks=tasks, username=session["username"]), 400

        priority = clean_priority(request.form.get("priority")) or "Medium"
        task = Task(
            title=title,
            description=description or None,
            completed=False,
            priority=priority,
            user_id=session["user_id"],
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("tasks_page"))

    @app.route("/tasks/<int:task_id>/update", methods=["POST"])
    def update_task(task_id):
        if "user_id" not in session:
            return redirect(url_for("login"))

        task = Task.query.filter_by(id=task_id, user_id=session["user_id"]).first()
        if not task:
            return render_template("404.html"), 404

        task.title = request.form.get("title", task.title).strip()
        task.description = request.form.get("description", task.description or "").strip() or None
        task.completed = "completed" in request.form
        if "priority" in request.form:
            task.priority = clean_priority(request.form.get("priority")) or task.priority
        if not task.title:
            tasks = Task.query.filter_by(user_id=session["user_id"]).order_by(Task.created_at.desc()).all()
            return render_template("tasks.html", error="Task title is required", tasks=tasks, username=session["username"]), 400

        db.session.commit()
        return redirect(url_for("tasks_page"))

    @app.route("/tasks/<int:task_id>/delete", methods=["POST"])
    def delete_task(task_id):
        if "user_id" not in session:
            return redirect(url_for("login"))

        task = Task.query.filter_by(id=task_id, user_id=session["user_id"]).first()
        if task:
            db.session.delete(task)
            db.session.commit()
        return redirect(url_for("tasks_page"))

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "not found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "internal server error"}), 500
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()
        ensure_priority_column()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)