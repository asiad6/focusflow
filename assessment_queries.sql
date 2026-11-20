-- SQL examples for FocusFlow
-- PostgreSQL. These queries only read data.
-- Run from the project folder with: psql -d focusflow -f assessment_queries.sql

-- 1. Show tasks with their owner and category, if they have one.
SELECT t.id AS task_id, t.title, u.username, c.name AS category
FROM tasks AS t
JOIN users AS u ON u.id = t.user_id
LEFT JOIN categories AS c ON c.id = t.category_id
ORDER BY t.id;

-- 2. Show tasks that don't have a category.
SELECT t.id, t.title, u.username
FROM tasks AS t
JOIN users AS u ON u.id = t.user_id
WHERE t.category_id IS NULL
ORDER BY t.id;

-- 3. Show each task's tags.
SELECT t.id AS task_id, t.title, tg.name AS tag, tt.added_at
FROM tasks AS t
JOIN task_tags AS tt ON tt.task_id = t.id
JOIN tags AS tg ON tg.id = tt.tag_id
ORDER BY t.id, tg.name;

-- 4. Count tasks by status.
SELECT status, COUNT(*) AS task_count
FROM tasks
GROUP BY status
ORDER BY task_count DESC, status;

-- 5. Count tasks for each user, including users with none.
SELECT u.id AS user_id, u.username, COUNT(t.id) AS task_count
FROM users AS u
LEFT JOIN tasks AS t ON t.user_id = u.id
GROUP BY u.id, u.username
ORDER BY task_count DESC, u.username;

-- 6. Find pending high-priority tasks. Try changing the filter values.
SELECT t.id, t.title, t.status, t.priority, t.due_date
FROM tasks AS t
WHERE t.status = 'pending' AND t.priority = 'high'
ORDER BY t.due_date NULLS LAST, t.id;

-- 7. Add up focus time for each task, including tasks with no sessions.
SELECT t.id AS task_id, t.title, COUNT(fs.id) AS session_count,
       COALESCE(SUM(fs.duration_minutes), 0) AS total_focus_minutes,
       ROUND(AVG(fs.duration_minutes), 1) AS average_session_minutes
FROM tasks AS t
LEFT JOIN focus_sessions AS fs ON fs.task_id = t.id
GROUP BY t.id, t.title
ORDER BY total_focus_minutes DESC, t.id;
