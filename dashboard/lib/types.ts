export type Task = {
  task_id: string;
  ticket_name: string;
  description: string;
  priority: number;
  status: string;
  assignee: string | null;
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type BoardPayload = {
  statuses: string[];
  counts: Record<string, number>;
  tasks: Task[];
  columns: Record<string, Task[]>;
  updated_at: string;
};

export type TriggerSummary = {
  agent: "sales" | "legal";
  total_processed: number;
  run_at: string;
  [key: string]: string | number;
};

export type Lead = {
  id: string;
  platform: string | null;
  title: string | null;
  url: string | null;
  budget: string | null;
  description: string | null;
  status: string | null;
  technical_doubts: string[];
  suggested_stack: string[];
  qualification_notes: string | null;
  opportunity_score: number | null;
  tags: string[];
  task_board_task_id: string | null;
  created_at: string | null;
  last_updated_at: string | null;
};

export type LeadInboxPayload = {
  leads: Lead[];
  counts: {
    total: number;
    by_status: Record<string, number>;
    by_platform: Record<string, number>;
  };
  updated_at: string;
};
