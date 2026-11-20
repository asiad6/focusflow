
from datetime import datetime

from app import db


# Each class below maps to a table in the database.
# Foreign keys store the links, and relationships make them easy to follow in Python.
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    categories = db.relationship(
        "Category", back_populates="user", cascade="all, delete-orphan"
    )
    tasks = db.relationship(
        "Task", back_populates="user", cascade="all, delete-orphan"
    )


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    color = db.Column(db.String(20), default="#6366f1")
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    user = db.relationship("User", back_populates="categories")
    tasks = db.relationship("Task", back_populates="category")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default="pending", nullable=False)
    priority = db.Column(db.String(20), default="medium")
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    # A task can be saved without a category.
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=True, index=True
    )

    user = db.relationship("User", back_populates="tasks")
    category = db.relationship("Category", back_populates="tasks")
    focus_sessions = db.relationship(
        "FocusSession", back_populates="task", cascade="all, delete-orphan"
    )
    task_tags = db.relationship(
        "TaskTag", back_populates="task", cascade="all, delete-orphan"
    )


class FocusSession(db.Model):
    __tablename__ = "focus_sessions"

    id = db.Column(db.Integer, primary_key=True)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    task_id = db.Column(
        db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True
    )

    task = db.relationship("Task", back_populates="focus_sessions")


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    task_tags = db.relationship(
        "TaskTag", back_populates="tag", cascade="all, delete-orphan"
    )


class TaskTag(db.Model):
    # The task and tag together make the primary key for this link table.
    __tablename__ = "task_tags"

    task_id = db.Column(
        db.Integer, db.ForeignKey("tasks.id"), primary_key=True
    )
    tag_id = db.Column(
        db.Integer, db.ForeignKey("tags.id"), primary_key=True
    )
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship("Task", back_populates="task_tags")
    tag = db.relationship("Tag", back_populates="task_tags")
