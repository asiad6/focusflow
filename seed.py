"""Insert extra sample data without deleting or updating existing rows."""

from datetime import datetime, timedelta, timezone

from app import create_app, db
from app.models import Category, FocusSession, Tag, Task, TaskTag, User

app = create_app()


def get_or_create(model, defaults=None, **lookup):
    instance = model.query.filter_by(**lookup).first()
    if instance:
        return instance, False

    params = dict(lookup)
    if defaults:
        params.update(defaults)

    instance = model(**params)
    db.session.add(instance)
    db.session.flush()
    return instance, True


def print_counts(label):
    print(f"\n{label}")
    print(f"  users:           {User.query.count()}")
    print(f"  categories:      {Category.query.count()}")
    print(f"  tags:            {Tag.query.count()}")
    print(f"  tasks:           {Task.query.count()}")
    print(f"  task_tags:       {TaskTag.query.count()}")
    print(f"  focus_sessions:  {FocusSession.query.count()}")


def seed():
    created = {
        "users": 0,
        "categories": 0,
        "tags": 0,
        "tasks": 0,
        "task_tags": 0,
        "focus_sessions": 0,
    }

    asya, asya_created = get_or_create(
        User,
        username="asya",
        defaults={"email": "asya@example.com"},
    )
    created["users"] += int(asya_created)

    jordan, jordan_created = get_or_create(
        User,
        username="jordan",
        defaults={"email": "jordan@example.com"},
    )
    created["users"] += int(jordan_created)

    university, created_flag = get_or_create(
        Category, name="University", user_id=asya.id, defaults={"color": "#6366f1"}
    )
    created["categories"] += int(created_flag)

    personal, created_flag = get_or_create(
        Category, name="Personal", user_id=asya.id, defaults={"color": "#22c55e"}
    )
    created["categories"] += int(created_flag)

    work, created_flag = get_or_create(
        Category, name="Work", user_id=asya.id, defaults={"color": "#f59e0b"}
    )
    created["categories"] += int(created_flag)

    coursework, created_flag = get_or_create(
        Category, name="Coursework", user_id=jordan.id, defaults={"color": "#38bdf8"}
    )
    created["categories"] += int(created_flag)

    tag_names = [
        "important",
        "study",
        "exam",
        "revision",
        "group-work",
        "project",
        "reading",
    ]
    tags = {}
    for name in tag_names:
        tag, created_flag = get_or_create(Tag, name=name)
        tags[name] = tag
        created["tags"] += int(created_flag)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    task_specs = [
        {
            "title": "Revise relational database normalisation",
            "description": "Go over 1NF, 2NF and 3NF with FocusFlow examples.",
            "status": "pending",
            "priority": "high",
            "user": asya,
            "category": university,
            "due_date": now + timedelta(days=3),
            "tags": ["study", "exam", "important"],
        },
        {
            "title": "Write SQL join examples for assessment",
            "description": "Prepare inner join queries across tasks, tags and sessions.",
            "status": "pending",
            "priority": "high",
            "user": asya,
            "category": university,
            "due_date": now + timedelta(days=4),
            "tags": ["study", "revision"],
        },
        {
            "title": "Prepare ER diagram notes",
            "description": "Document primary keys, foreign keys and cardinalities.",
            "status": "completed",
            "priority": "medium",
            "user": asya,
            "category": university,
            "due_date": now - timedelta(days=1),
            "tags": ["project", "important"],
        },
        {
            "title": "Read PostgreSQL indexing chapter",
            "description": "Focus on B-tree indexes used by foreign keys.",
            "status": "pending",
            "priority": "medium",
            "user": asya,
            "category": university,
            "due_date": now + timedelta(days=7),
            "tags": ["reading", "study"],
        },
        {
            "title": "Plan weekly study timetable",
            "description": "Block focus sessions around lectures and labs.",
            "status": "pending",
            "priority": "low",
            "user": asya,
            "category": personal,
            "due_date": now + timedelta(days=2),
            "tags": ["revision"],
        },
        {
            "title": "Backup FocusFlow database dump",
            "description": "Export a local dump before the assessment demo.",
            "status": "completed",
            "priority": "medium",
            "user": asya,
            "category": work,
            "due_date": now - timedelta(days=2),
            "tags": ["project"],
        },
        {
            "title": "Practice Flask API requests",
            "description": "Test create, read, update and delete for tasks.",
            "status": "pending",
            "priority": "high",
            "user": asya,
            "category": university,
            "due_date": now + timedelta(days=1),
            "tags": ["project", "study", "important"],
        },
        {
            "title": "Review many-to-many task tags",
            "description": "Check the task_tags junction table with sample queries.",
            "status": "pending",
            "priority": "medium",
            "user": asya,
            "category": university,
            "due_date": now + timedelta(days=5),
            "tags": ["study", "revision"],
        },
        {
            "title": "Draft group presentation slides",
            "description": "Outline the database design section of the talk.",
            "status": "pending",
            "priority": "high",
            "user": jordan,
            "category": coursework,
            "due_date": now + timedelta(days=6),
            "tags": ["group-work", "project"],
        },
        {
            "title": "Complete SQL worksheet 4",
            "description": "Joins, aggregation and foreign-key questions.",
            "status": "completed",
            "priority": "medium",
            "user": jordan,
            "category": coursework,
            "due_date": now - timedelta(days=3),
            "tags": ["study", "exam"],
        },
        {
            "title": "Read entity-relationship modelling notes",
            "description": "Identify one-to-many and many-to-many examples.",
            "status": "pending",
            "priority": "low",
            "user": jordan,
            "category": coursework,
            "due_date": now + timedelta(days=8),
            "tags": ["reading"],
        },
        {
            "title": "Record a 25-minute focus session log",
            "description": "Use FocusFlow to capture duration and notes.",
            "status": "pending",
            "priority": "medium",
            "user": jordan,
            "category": coursework,
            "due_date": now + timedelta(days=2),
            "tags": ["project"],
        },
    ]

    tasks_by_title = {}
    for spec in task_specs:
        task, created_flag = get_or_create(
            Task,
            title=spec["title"],
            user_id=spec["user"].id,
            defaults={
                "description": spec["description"],
                "status": spec["status"],
                "priority": spec["priority"],
                "category_id": spec["category"].id,
                "due_date": spec["due_date"],
            },
        )
        created["tasks"] += int(created_flag)
        tasks_by_title[spec["title"]] = task

        for tag_name in spec["tags"]:
            _, created_flag = get_or_create(
                TaskTag,
                task_id=task.id,
                tag_id=tags[tag_name].id,
            )
            created["task_tags"] += int(created_flag)

    session_specs = [
        ("Revise relational database normalisation", 25, "Covered 1NF and 2NF examples."),
        ("Revise relational database normalisation", 40, "Worked through 3NF task examples."),
        ("Write SQL join examples for assessment", 30, "Wrote joins for tasks and tags."),
        ("Prepare ER diagram notes", 20, "Mapped all six tables and keys."),
        ("Read PostgreSQL indexing chapter", 25, "Read foreign-key index section."),
        ("Practice Flask API requests", 45, "Tested task create, update and delete."),
        ("Review many-to-many task tags", 15, "Checked junction table rows."),
        ("Draft group presentation slides", 35, "Outlined the design section."),
        ("Complete SQL worksheet 4", 50, "Finished join and aggregation questions."),
        ("Record a 25-minute focus session log", 25, "First timed session for Jordan."),
    ]

    for title, duration, notes in session_specs:
        task = tasks_by_title[title]
        _, created_flag = get_or_create(
            FocusSession,
            task_id=task.id,
            duration_minutes=duration,
            notes=notes,
        )
        created["focus_sessions"] += int(created_flag)

    db.session.commit()
    return created


if __name__ == "__main__":
    with app.app_context():
        print_counts("Before seeding")
        created = seed()
        print("\nInserted (skipped rows that already existed):")
        for table_name, count in created.items():
            print(f"  {table_name}: {count}")
        print_counts("After seeding")
        print("\nExisting rows were not deleted or overwritten.")
