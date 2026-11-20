# FocusFlow

FocusFlow is a Flask and PostgreSQL task-management app for planning study work, grouping tasks into categories, tagging them, and logging timed focus sessions.

The project is built around a normalised relational schema with six tables, foreign keys, indexes, and a many-to-many relationship between tasks and tags.

## Implemented use cases

FocusFlow is a working Flask application whose routes use SQLAlchemy models and PostgreSQL for data access. The database access is part of the application rather than a standalone demonstration script.

| Use case | Status | Where it is implemented |
|---|---|---|
| Create and list users | Implemented | `POST /users`, `GET /users` |
| Create and list per-user categories | Implemented | `POST /categories`, `GET /categories` |
| Create, view, update, complete and delete tasks | Implemented | `/tasks` routes and dashboard |
| Filter tasks by user and status | Implemented | `GET /tasks?user_id=1&status=pending` |
| Assign an optional category to a task, validating category ownership | Implemented | Task create and update routes |
| Create tags, assign them to tasks and list a task's tags | Implemented | `/tags` and task-tag routes |
| Record a focus session for a task and list its sessions | Implemented | Task session routes |

The project is presented as an individual project. If any work was completed with a team, replace this statement with a clear description of your contribution before submission.

## Technologies

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Migrate (Alembic)
- PostgreSQL
- psycopg2
- HTML, CSS and vanilla JavaScript for the dashboard

## Project structure

```text
focusflow/
├── app/
│   ├── __init__.py      # Flask app factory, SQLAlchemy and Migrate setup
│   ├── models.py        # Database models and relationships
│   ├── routes.py        # REST API and dashboard route
│   └── templates/
│       └── index.html   # Task dashboard UI
├── migrations/          # Alembic migration history
├── config.py            # Loads DATABASE_URL from .env
├── run.py               # Application entry point
├── seed.py              # Safe sample-data seeder
├── requirements.txt
└── .env                 # Local database URL (not committed)
```

## Database design

### Tables

| Table | Purpose | Primary key |
|---|---|---|
| `users` | App users | `id` |
| `categories` | Per-user task groups | `id` |
| `tasks` | Work items owned by a user | `id` |
| `tags` | Reusable labels | `id` |
| `task_tags` | Junction table for tasks and tags | (`task_id`, `tag_id`) |
| `focus_sessions` | Timed work logged against a task | `id` |

### Relationships and cardinalities

| Relationship | Cardinality | Foreign key |
|---|---|---|
| User → Category | one-to-many | `categories.user_id` → `users.id` |
| User → Task | one-to-many | `tasks.user_id` → `users.id` |
| Category → Task | one-to-many, optional | `tasks.category_id` → `categories.id` |
| Task → FocusSession | one-to-many | `focus_sessions.task_id` → `tasks.id` |
| Task ↔ Tag | many-to-many | `task_tags.task_id` → `tasks.id` and `task_tags.tag_id` → `tags.id` |

A task can exist without a category (`category_id` is nullable). A tag can be assigned to many tasks, and a task can have many tags, through `task_tags`.

### ER diagram

```mermaid
erDiagram
    users {
        int id PK
        string username "unique not null"
        string email "unique not null"
        datetime created_at
    }

    categories {
        int id PK
        string name "not null"
        string color
        int user_id FK
    }

    tasks {
        int id PK
        string title "not null"
        string description
        string status "not null"
        string priority
        datetime due_date
        datetime created_at
        int user_id FK
        int category_id FK "nullable optional"
    }

    focus_sessions {
        int id PK
        datetime started_at "not null"
        datetime ended_at
        int duration_minutes "not null"
        string notes
        int task_id FK
    }

    tags {
        int id PK
        string name "unique not null"
    }

    task_tags {
        int task_id PK FK "composite PK with tag_id"
        int tag_id PK FK "composite PK with task_id"
        datetime added_at
    }

    users ||--o{ categories : owns
    users ||--o{ tasks : creates
    categories |o--o{ tasks : "optional category"
    tasks ||--o{ focus_sessions : logs
    tasks ||--o{ task_tags : "tagged with"
    tags ||--o{ task_tags : "applied to"
```

### Foreign keys

These constraints exist in PostgreSQL:

| Constraint | Definition |
|---|---|
| `categories_user_id_fkey` | `categories.user_id` → `users.id` |
| `tasks_user_id_fkey` | `tasks.user_id` → `users.id` |
| `tasks_category_id_fkey` | `tasks.category_id` → `categories.id` |
| `focus_sessions_task_id_fkey` | `focus_sessions.task_id` → `tasks.id` |
| `task_tags_task_id_fkey` | `task_tags.task_id` → `tasks.id` |
| `task_tags_tag_id_fkey` | `task_tags.tag_id` → `tags.id` |

The database uses the default `NO ACTION` / `RESTRICT` behaviour. SQLAlchemy also cascades deletes in the ORM for a user's categories and tasks, a task's focus sessions, and a task's tag links.

### Indexes

| Index | Table | Column(s) | Reason |
|---|---|---|---|
| `users_pkey` | `users` | `id` | Primary key |
| `users_username_key` | `users` | `username` | Unique username |
| `users_email_key` | `users` | `email` | Unique email |
| `categories_pkey` | `categories` | `id` | Primary key |
| `ix_categories_user_id` | `categories` | `user_id` | Foreign-key lookups by user |
| `tasks_pkey` | `tasks` | `id` | Primary key |
| `ix_tasks_user_id` | `tasks` | `user_id` | Filter dashboard tasks by user |
| `ix_tasks_category_id` | `tasks` | `category_id` | Filter tasks by category |
| `tags_pkey` | `tags` | `id` | Primary key |
| `tags_name_key` | `tags` | `name` | Unique tag names |
| `task_tags_pkey` | `task_tags` | (`task_id`, `tag_id`) | Composite primary key and lookup by task |
| `focus_sessions_pkey` | `focus_sessions` | `id` | Primary key |
| `ix_focus_sessions_task_id` | `focus_sessions` | `task_id` | List sessions for a task |

`task_tags.tag_id` is covered by the foreign key, but it does not have a separate single-column index. The composite primary key starts with `task_id`, which is the lookup used by the API.

## Setup

### 1. Create and activate a virtual environment

```bash
cd focusflow
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure PostgreSQL

Create a local database named `focusflow`:

```bash
createdb focusflow
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://localhost/focusflow
```

If your PostgreSQL user or password is different, use:

```env
DATABASE_URL=postgresql+psycopg2://USERNAME:PASSWORD@localhost:5432/focusflow
```

### 3. Run migrations

```bash
flask --app run.py db upgrade
```

This applies `migrations/versions/5b68cc60bdf8_create_initial_database_tables.py`, which creates all six tables, foreign keys and indexes.

To generate a new migration after a model change:

```bash
flask --app run.py db migrate -m "describe the change"
flask --app run.py db upgrade
```

### 4. Load sample data

The seeder only inserts missing rows. It does not delete or overwrite existing data.

```bash
python seed.py
```

### 5. Run the application

```bash
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

The dashboard loads tasks for user `id = 1`.

## Database assessment demonstrations

Run the read-only examples against the local PostgreSQL database from this folder:

```bash
psql -d focusflow -f assessment_queries.sql
```

The file demonstrates owner joins, the nullable `tasks.category_id` link, the `task_tags` many-to-many relationship, filtering, grouped counts and focus-session summaries. If your database has a different name, replace `focusflow` with that name.

### Preparation checklist

- Explain each table's purpose, primary key and foreign keys using the ER diagram above.
- Describe the optional `tasks.category_id` link and the composite key in `task_tags`.
- Run the examples in `assessment_queries.sql` and explain the JOIN, WHERE, GROUP BY and aggregate operations.
- Use the existing seeded records for the demonstration; `python seed.py` inserts missing sample rows without deleting or updating existing rows.
- Be ready to describe the indexes listed above and the routes that create, filter and retrieve tasks, tags and focus sessions.

No official assessment brief or rubric file is present in this project, so this checklist covers the database features documented here and should be compared with any separate instructions from your course.

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Task dashboard |
| `GET` | `/users` | List users |
| `POST` | `/users` | Create a user (`username`, `email`) |
| `GET` | `/categories` | List categories; optional `?user_id=` |
| `POST` | `/categories` | Create a category (`name`, `user_id`, optional `color`) |
| `GET` | `/tasks` | List tasks; optional `?user_id=` and `?status=` |
| `GET` | `/tasks/<id>` | Get one task |
| `POST` | `/tasks` | Create a task (`title`, `user_id`, optional `description`, `priority`, `category_id`) |
| `PATCH` | `/tasks/<id>` | Update title, description, priority, status or category |
| `DELETE` | `/tasks/<id>` | Delete a task |
| `DELETE` | `/tasks/<id>/delete` | Same delete route used by the dashboard |
| `PATCH` | `/tasks/<id>/complete` | Mark a task completed |
| `GET` | `/tags` | List tags |
| `POST` | `/tags` | Create a tag (`name`) |
| `POST` | `/tasks/<task_id>/tags/<tag_id>` | Assign a tag to a task |
| `GET` | `/tasks/<task_id>/tags` | List tags for a task |
| `POST` | `/tasks/<task_id>/sessions` | Create a focus session (`duration_minutes`, optional `notes`) |
| `GET` | `/tasks/<task_id>/sessions` | List focus sessions for a task |

### Example requests

Create a task:

```bash
curl -X POST http://127.0.0.1:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Revise SQL joins","user_id":1,"priority":"high"}'
```

Update a task:

```bash
curl -X PATCH http://127.0.0.1:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Revise SQL joins and keys"}'
```

Delete a task:

```bash
curl -X DELETE http://127.0.0.1:5000/tasks/1
```

## Sample data

The original database was too small to show the full design: one user, one category, one tag, a few tasks, one tag assignment and one focus session.

The local database was checked for assessment preparation on 2026-11-20 and contained 2 users, 4 categories, 15 tasks, 7 tags, 23 task-tag links and 11 focus sessions (62 rows across these six tables). Counts can change as the application is used. The sample data includes mixed task statuses and priorities, optional categories, multiple tags on tasks, and sessions linked to different tasks.

`seed.py` generated the additional sample records using stable usernames, category names, task titles, tag names and task/session details. It inserts only missing records and leaves existing rows, including the original user `asya`, unchanged. Running it again is safe and may insert zero rows when all sample records already exist.

Useful queries after seeding:

```sql
-- Tasks with owner and optional category
SELECT t.id, t.title, t.status, u.username, c.name AS category
FROM tasks t
JOIN users u ON u.id = t.user_id
LEFT JOIN categories c ON c.id = t.category_id
ORDER BY t.id;

-- Many-to-many tags
SELECT t.title, tag.name
FROM tasks t
JOIN task_tags tt ON tt.task_id = t.id
JOIN tags tag ON tag.id = tt.tag_id
ORDER BY t.title, tag.name;

-- Focus time per task
SELECT t.title, COUNT(fs.id) AS sessions, SUM(fs.duration_minutes) AS minutes
FROM tasks t
LEFT JOIN focus_sessions fs ON fs.task_id = t.id
GROUP BY t.id, t.title
ORDER BY minutes DESC NULLS LAST;
```
