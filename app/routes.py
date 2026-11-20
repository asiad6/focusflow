from flask import Blueprint, request, jsonify, render_template
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User, Category, Task, Tag, TaskTag, FocusSession

main = Blueprint("main", __name__)


def serialize_task(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "user_id": task.user_id,
        "category_id": task.category_id,
    }


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("email"):
        return jsonify({"error": "Username and email are required"}), 400

    user = User(
        username=data["username"],
        email=data["email"]
    )

    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 409

    return jsonify({
        "message": "User created successfully",
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 201


@main.route("/users", methods=["GET"])
def get_users():
    users = User.query.order_by(User.id).all()

    return jsonify([
        {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        for user in users
    ])


@main.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()

    if not data or not data.get("name") or not data.get("user_id"):
        return jsonify({"error": "Name and user_id are required"}), 400

    user = db.session.get(User, data["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    category = Category(
        name=data["name"],
        color=data.get("color", "#6366f1"),
        user_id=user.id
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        "id": category.id,
        "name": category.name,
        "color": category.color,
        "user_id": category.user_id
    }), 201


@main.route("/categories", methods=["GET"])
def get_categories():
    query = Category.query

    user_id = request.args.get("user_id", type=int)

    if user_id:
        query = query.filter_by(user_id=user_id)

    categories = query.order_by(Category.id).all()

    return jsonify([
        {
            "id": category.id,
            "name": category.name,
            "color": category.color,
            "user_id": category.user_id
        }
        for category in categories
    ])


@main.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or not data.get("title") or not data.get("user_id"):
        return jsonify({"error": "Title and user_id are required"}), 400

    user = db.session.get(User, data["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    category_id = data.get("category_id")

    if category_id is not None:
        category = db.session.get(Category, category_id)

        if not category or category.user_id != user.id:
            return jsonify({"error": "Invalid category"}), 400

    task = Task(
        title=data["title"],
        description=data.get("description"),
        priority=data.get("priority", "medium"),
        user_id=user.id,
        category_id=category_id
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(serialize_task(task)), 201


@main.route("/tasks", methods=["GET"])
def get_tasks():
    query = Task.query

    user_id = request.args.get("user_id", type=int)
    status = request.args.get("status")

    if user_id:
        query = query.filter_by(user_id=user_id)

    if status:
        query = query.filter_by(status=status)

    tasks = query.order_by(Task.created_at.desc()).all()

    return jsonify([serialize_task(task) for task in tasks])


@main.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(serialize_task(task))


@main.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json() or {}

    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"error": "Title cannot be empty"}), 400
        task.title = title

    if "description" in data:
        task.description = data["description"]

    if "priority" in data:
        task.priority = data["priority"]

    if "status" in data:
        task.status = data["status"]

    if "category_id" in data:
        category_id = data["category_id"]
        if category_id is not None:
            category = db.session.get(Category, category_id)
            if not category or category.user_id != task.user_id:
                return jsonify({"error": "Invalid category"}), 400
        task.category_id = category_id

    db.session.commit()

    return jsonify({
        "message": "Task updated successfully",
        **serialize_task(task)
    }), 200


@main.route("/tasks/<int:task_id>", methods=["DELETE"])
@main.route("/tasks/<int:task_id>/delete", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "message": "Task deleted successfully",
        "id": task_id
    }), 200


@main.route("/tasks/<int:task_id>/complete", methods=["PATCH"])
def complete_task(task_id):
    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    task.status = "completed"
    db.session.commit()

    return jsonify({
        "message": "Task completed successfully",
        "id": task.id,
        "status": task.status
    }), 200


@main.route("/tags", methods=["POST"])
def create_tag():
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({"error": "Tag name is required"}), 400

    name = data["name"].strip().lower()

    if not name:
        return jsonify({"error": "Tag name cannot be empty"}), 400

    existing_tag = Tag.query.filter_by(name=name).first()

    if existing_tag:
        return jsonify({"error": "Tag already exists"}), 409

    tag = Tag(name=name)

    db.session.add(tag)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Tag already exists"}), 409

    return jsonify({
        "id": tag.id,
        "name": tag.name
    }), 201


@main.route("/tags", methods=["GET"])
def get_tags():
    tags = Tag.query.order_by(Tag.name).all()

    return jsonify([
        {
            "id": tag.id,
            "name": tag.name
        }
        for tag in tags
    ])


@main.route("/tasks/<int:task_id>/tags/<int:tag_id>", methods=["POST"])
def assign_tag(task_id, tag_id):
    task = db.session.get(Task, task_id)
    tag = db.session.get(Tag, tag_id)

    if not task or not tag:
        return jsonify({"error": "Task or tag not found"}), 404

    existing = db.session.get(TaskTag, (task_id, tag_id))

    if existing:
        return jsonify({"error": "Tag already assigned"}), 409

    task_tag = TaskTag(task_id=task_id, tag_id=tag_id)

    db.session.add(task_tag)
    db.session.commit()

    return jsonify({
        "message": "Tag assigned successfully",
        "task_id": task_id,
        "tag_id": tag_id
    }), 201


@main.route("/tasks/<int:task_id>/tags", methods=["GET"])
def get_task_tags(task_id):
    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify([
        {
            "id": item.tag.id,
            "name": item.tag.name
        }
        for item in task.task_tags
    ])


@main.route("/tasks/<int:task_id>/sessions", methods=["POST"])
def create_focus_session(task_id):
    data = request.get_json()

    if not data or not data.get("duration_minutes"):
        return jsonify({"error": "Duration is required"}), 400

    try:
        duration = int(data["duration_minutes"])
    except (ValueError, TypeError):
        return jsonify({"error": "Duration must be a number"}), 400

    if duration <= 0:
        return jsonify({"error": "Duration must be positive"}), 400

    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    session = FocusSession(
        task_id=task.id,
        duration_minutes=duration,
        notes=data.get("notes")
    )

    db.session.add(session)
    db.session.commit()

    return jsonify({
        "message": "Focus session created successfully",
        "id": session.id,
        "task_id": session.task_id,
        "duration_minutes": session.duration_minutes
    }), 201


@main.route("/tasks/<int:task_id>/sessions", methods=["GET"])
def get_focus_sessions(task_id):
    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    sessions = FocusSession.query.filter_by(
        task_id=task_id
    ).order_by(FocusSession.started_at.desc()).all()

    return jsonify([
        {
            "id": session.id,
            "duration_minutes": session.duration_minutes,
            "notes": session.notes,
            "started_at": session.started_at.isoformat()
        }
        for session in sessions
    ])
