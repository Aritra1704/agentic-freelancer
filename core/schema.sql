-- SQL Schema for the shared Task Board
CREATE TABLE IF NOT EXISTS task_board (
    task_id UUID PRIMARY KEY,
    ticket_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    status VARCHAR(50) NOT NULL DEFAULT 'BACKLOG',
    assignee VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient polling
CREATE INDEX IF NOT EXISTS idx_task_status_priority ON task_board (status, priority);
