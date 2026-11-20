-- FocusFlow database assessment demonstrations
-- PostgreSQL; all statements are read-only SELECT queries.
-- Run from the project folder with: psql -d focusflow -f assessment_queries.sql

-- 1. Tasks with their owner and optional category.
SELECT t.id AS task_id, t.title, u.username, c.name AS category
FROM tasks AS t
JOIN users AS u ON u.id = t.user_id
LEFT JOIN categories AS c ON c.id = t.category_id
ORDER BY t.id;

-- 2. Tasks without a category (the optional category relationship).
SELECT t.id, t.title, u.username
FROM tasks AS t
JOIN users AS u ON u.id = t.user_id
WHERE t.category_id IS NULL
ORDER BY t.id;

-- 3. Tasks and tags through the task_tags many-to-many junction table.
SELECT t.id AS task_id, t.title, tg.name AS tag, tt.added_at
FROM tasks AS t
JOIN task_tags AS tt ON tt.task_id = t.id
JOIN tags AS tg ON tg.id = tt.tag_id
ORDER BY t.id, tg.name;

-- 4. Aggregate task counts by status.
SELECT status, COUNT(*) AS task_count
FROM tasks
GROUP BY status
ORDER BY task_count DESC, status;

-- 5. Aggregate task counts per user, retaining users with no tasks.
SELECT u.id AS user_id, u.username, COUNT(t.id) AS task_count
FROM users AS u
LEFT JOIN tasks AS t ON t.user_id = u.id
GROUP BY u.id, u.username
ORDER BY task_count DESC, u.username;

-- 6. Filter tasks by status and priority. Adjust the values to demonstrate filters.
SELECT t.id, t.title, t.status, t.priority, t.due_date
FROM tasks AS t
WHERE t.status = 'pending' AND t.priority = 'high'
ORDER BY t.due_date NULLS LAST, t.id;

-- 7. Focus-session summary per task, including tasks with no sessions.
SELECT t.id AS task_id, t.title, COUNT(fs.id) AS session_count,
       COALESCE(SUM(fs.duration_minutes), 0) AS total_focus_minutes,
       ROUND(AVG(fs.duration_minutes), 1) AS average_session_minutes
FROM tasks AS t
LEFT JOIN focus_sessions AS fs ON fs.task_id = t.id
GROUP BY t.id, t.title
ORDER BY total_focus_minutes DESC, t.id;
