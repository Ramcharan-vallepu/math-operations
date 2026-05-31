-- Tasks table for TaskList-style CRUD endpoints.
CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    due_date TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT tasks_status_check CHECK (status IN ('pending', 'in_progress', 'completed'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status_due_date ON tasks (status, due_date);
