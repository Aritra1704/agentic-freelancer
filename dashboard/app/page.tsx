"use client";

import { startTransition, useEffect, useState } from "react";

import LeadInbox from "./components/LeadInbox";
import { BoardPayload, LeadInboxPayload, TriggerSummary } from "../lib/types";

const METRIC_LABELS: Record<string, string> = {
  BACKLOG: "Queued",
  LEGAL_REVIEW: "Legal Gate",
  PENDING: "Ready For Dev",
  IN_PROGRESS: "In Flight",
  COMPLIANCE_CHECK: "Compliance Gate",
  READY_FOR_DELIVERY: "Ready To Send",
  COMPLETED: "Delivered",
  BLOCKED: "Blocked"
};

const STATUS_STYLES: Record<string, string> = {
  BACKLOG: "border-black/10 bg-white text-black/75",
  LEGAL_REVIEW: "border-clay/20 bg-clay/10 text-clay",
  PENDING: "border-moss/20 bg-moss/10 text-moss",
  IN_PROGRESS: "border-sky-700/20 bg-sky-700/10 text-sky-800",
  COMPLIANCE_CHECK: "border-amber-600/20 bg-amber-500/10 text-amber-800",
  READY_FOR_DELIVERY: "border-emerald-700/20 bg-emerald-600/10 text-emerald-800",
  COMPLETED: "border-ink/10 bg-ink text-white",
  BLOCKED: "border-red-700/20 bg-red-600/10 text-red-800"
};

function formatDate(value: string | null) {
  if (!value) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function formatAgentSummary(summary: TriggerSummary | null) {
  if (!summary) {
    return "No agent runs in this session yet.";
  }

  const parts = Object.entries(summary)
    .filter(([key]) => !["agent", "run_at"].includes(key))
    .map(([key, value]) => `${key.replaceAll("_", " ")}: ${value}`);

  return `${summary.agent.toUpperCase()} run at ${formatDate(summary.run_at)} • ${parts.join(" • ")}`;
}

export default function Page() {
  const [activeView, setActiveView] = useState<"inbox" | "board">("inbox");
  const [board, setBoard] = useState<BoardPayload | null>(null);
  const [inbox, setInbox] = useState<LeadInboxPayload | null>(null);
  const [isBoardLoading, setIsBoardLoading] = useState(true);
  const [isInboxLoading, setIsInboxLoading] = useState(true);
  const [isBoardRefreshing, setIsBoardRefreshing] = useState(false);
  const [isInboxRefreshing, setIsInboxRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runningAgent, setRunningAgent] = useState<"sales" | "legal" | null>(null);
  const [actingLeadId, setActingLeadId] = useState<string | null>(null);
  const [actingLeadAction, setActingLeadAction] = useState<"approve" | "reject" | null>(null);
  const [lastSummary, setLastSummary] = useState<TriggerSummary | null>(null);

  async function loadBoard(options?: { silent?: boolean }) {
    const silent = options?.silent ?? false;
    if (silent) {
      setIsBoardRefreshing(true);
    } else {
      setIsBoardLoading(true);
    }

    try {
      const response = await fetch("/api/tasks", {
        cache: "no-store"
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.error || "Unable to load task board.");
      }

      startTransition(() => {
        setBoard(payload);
      });
    } finally {
      setIsBoardLoading(false);
      setIsBoardRefreshing(false);
    }
  }

  async function loadInbox(options?: { silent?: boolean }) {
    const silent = options?.silent ?? false;
    if (silent) {
      setIsInboxRefreshing(true);
    } else {
      setIsInboxLoading(true);
    }

    try {
      const response = await fetch("/api/leads", {
        cache: "no-store"
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.error || "Unable to load lead inbox.");
      }

      startTransition(() => {
        setInbox(payload);
      });
    } finally {
      setIsInboxLoading(false);
      setIsInboxRefreshing(false);
    }
  }

  async function refreshAll(options?: { silent?: boolean }) {
    const silent = options?.silent ?? false;

    try {
      await Promise.all([loadBoard({ silent }), loadInbox({ silent })]);
      setError(null);
    } catch (loadError) {
      const message = loadError instanceof Error ? loadError.message : "Unable to refresh dashboard.";
      setError(message);
    }
  }

  async function runAgent(agent: "sales" | "legal") {
    setRunningAgent(agent);
    setError(null);

    try {
      const response = await fetch(`/api/trigger/${agent}`, {
        method: "POST"
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.error || `Unable to run ${agent} agent.`);
      }

      setLastSummary(payload);
      await refreshAll({ silent: true });
    } catch (runError) {
      const message = runError instanceof Error ? runError.message : `Unable to run ${agent} agent.`;
      setError(message);
    } finally {
      setRunningAgent(null);
    }
  }

  async function actOnLead(leadId: string, action: "approve" | "reject") {
    setActingLeadId(leadId);
    setActingLeadAction(action);
    setError(null);

    try {
      const response = await fetch(`/api/leads/${leadId}`, {
        method: action === "approve" ? "POST" : "DELETE"
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.error || `Unable to ${action} lead.`);
      }

      await refreshAll({ silent: true });
      if (action === "approve") {
        setActiveView("board");
      }
    } catch (actionError) {
      const message = actionError instanceof Error ? actionError.message : `Unable to ${action} lead.`;
      setError(message);
    } finally {
      setActingLeadId(null);
      setActingLeadAction(null);
    }
  }

  useEffect(() => {
    refreshAll().catch(() => null);

    const intervalId = window.setInterval(() => {
      refreshAll({ silent: true }).catch(() => null);
    }, 15000);

    return () => window.clearInterval(intervalId);
  }, []);

  const totalTasks = board?.tasks.length || 0;
  const totalInboxLeads = inbox?.counts.total || 0;

  return (
    <main className="min-h-screen px-5 py-8 text-ink sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="overflow-hidden rounded-[2rem] border border-black/10 bg-white/75 p-8 shadow-[0_24px_80px_rgba(16,20,24,0.12)] backdrop-blur">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="text-sm uppercase tracking-[0.35em] text-moss">Freelance-OS Dashboard</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
                Lead Inbox And Delivery Console
              </h1>
              <p className="mt-4 text-base leading-7 text-black/70 sm:text-lg">
                Review inbound leads before they become tasks, then drive approved work through the
                shared delivery board with manual Sales and Legal agent triggers.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={() => runAgent("sales")}
                disabled={runningAgent !== null}
                className="rounded-2xl border border-moss/20 bg-moss px-5 py-4 text-left text-white shadow-sm transition hover:bg-moss/90 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span className="block text-xs uppercase tracking-[0.25em] text-white/70">Trigger</span>
                <span className="mt-2 block text-lg font-medium">
                  {runningAgent === "sales" ? "Running Sales Scan..." : "Run Sales Scan"}
                </span>
              </button>

              <button
                type="button"
                onClick={() => runAgent("legal")}
                disabled={runningAgent !== null}
                className="rounded-2xl border border-clay/20 bg-clay px-5 py-4 text-left text-white shadow-sm transition hover:bg-clay/90 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span className="block text-xs uppercase tracking-[0.25em] text-white/70">Trigger</span>
                <span className="mt-2 block text-lg font-medium">
                  {runningAgent === "legal" ? "Performing Legal Review..." : "Perform Legal Review"}
                </span>
              </button>
            </div>
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-3">
            <div className="rounded-2xl border border-black/10 bg-black/[0.03] p-4 text-sm text-black/70">
              <p className="text-xs uppercase tracking-[0.2em] text-black/45">Lead Inbox</p>
              <p className="mt-3 leading-7">
                {totalInboxLeads} leads currently need approval or rejection before task creation.
              </p>
            </div>
            <div className="rounded-2xl border border-black/10 bg-black/[0.03] p-4 text-sm text-black/70">
              <p className="text-xs uppercase tracking-[0.2em] text-black/45">Latest Agent Activity</p>
              <p className="mt-3 leading-7">{formatAgentSummary(lastSummary)}</p>
            </div>
            <div className="rounded-2xl border border-black/10 bg-black/[0.03] p-4 text-sm text-black/70">
              <p className="text-xs uppercase tracking-[0.2em] text-black/45">Board Sync</p>
              <p className="mt-3 leading-7">
                {board ? `Last refreshed ${formatDate(board.updated_at)}` : "Waiting for first board snapshot."}
                {isBoardRefreshing || isInboxRefreshing ? " Refreshing in background..." : ""}
              </p>
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => setActiveView("inbox")}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                activeView === "inbox"
                  ? "border-moss/20 bg-moss text-white"
                  : "border-black/10 bg-white text-black/65 hover:bg-black/[0.03]"
              }`}
            >
              Lead Inbox
            </button>
            <button
              type="button"
              onClick={() => setActiveView("board")}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                activeView === "board"
                  ? "border-moss/20 bg-moss text-white"
                  : "border-black/10 bg-white text-black/65 hover:bg-black/[0.03]"
              }`}
            >
              Task Board
            </button>
          </div>

          {error ? (
            <div className="mt-6 rounded-2xl border border-red-700/15 bg-red-600/10 px-4 py-3 text-sm text-red-900">
              {error}
            </div>
          ) : null}
        </section>

        {activeView === "inbox" ? (
          <LeadInbox
            inbox={inbox}
            isLoading={isInboxLoading}
            isRefreshing={isInboxRefreshing}
            actingLeadId={actingLeadId}
            actingAction={actingLeadAction}
            onApprove={(leadId) => {
              actOnLead(leadId, "approve").catch(() => null);
            }}
            onReject={(leadId) => {
              actOnLead(leadId, "reject").catch(() => null);
            }}
            formatDate={formatDate}
          />
        ) : null}

        {activeView === "board" ? (
          <>
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {(board?.statuses || Object.keys(METRIC_LABELS)).map((status) => (
                <article
                  key={status}
                  className="rounded-3xl border border-black/10 bg-white/70 p-5 shadow-sm backdrop-blur"
                >
                  <p className="text-xs uppercase tracking-[0.2em] text-black/45">
                    {METRIC_LABELS[status] || status.replaceAll("_", " ")}
                  </p>
                  <div className="mt-4 flex items-end justify-between gap-3">
                    <p className="text-4xl font-semibold">{board?.counts?.[status] || 0}</p>
                    <span
                      className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.2em] ${
                        STATUS_STYLES[status] || STATUS_STYLES.BACKLOG
                      }`}
                    >
                      {status.replaceAll("_", " ")}
                    </span>
                  </div>
                </article>
              ))}
            </section>

            <section className="rounded-[2rem] border border-black/10 bg-white/70 p-5 shadow-[0_18px_50px_rgba(16,20,24,0.08)] backdrop-blur sm:p-6">
              <div className="flex flex-col gap-3 border-b border-black/10 pb-5 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.3em] text-black/45">Task Board</p>
                  <h2 className="mt-2 text-3xl font-semibold">Delivery Workflow</h2>
                </div>
                <p className="text-sm text-black/65">
                  {isBoardLoading ? "Loading task board..." : `${totalTasks} tasks across the shared workflow`}
                </p>
              </div>

              {isBoardLoading && !board ? (
                <div className="py-16 text-center text-sm text-black/55">Loading task board snapshot...</div>
              ) : null}

              {!isBoardLoading && board && totalTasks === 0 ? (
                <div className="py-16 text-center text-sm text-black/55">
                  No tasks are in `task_board` yet. Approve a lead from the inbox to create the first
                  task, then use the triggers here to move work through the lifecycle.
                </div>
              ) : null}

              {board && totalTasks > 0 ? (
                <div className="mt-6 overflow-x-auto pb-2">
                  <div className="flex min-w-max gap-4">
                    {board.statuses.map((status) => {
                      const tasks = board.columns?.[status] || [];

                      return (
                        <section
                          key={status}
                          className="w-[320px] shrink-0 rounded-[1.75rem] border border-black/10 bg-fog/90 p-4"
                        >
                          <div className="flex items-center justify-between gap-3">
                            <div>
                              <p className="text-xs uppercase tracking-[0.2em] text-black/45">
                                {METRIC_LABELS[status] || status.replaceAll("_", " ")}
                              </p>
                              <h3 className="mt-1 text-lg font-semibold">{status.replaceAll("_", " ")}</h3>
                            </div>
                            <span
                              className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.2em] ${
                                STATUS_STYLES[status] || STATUS_STYLES.BACKLOG
                              }`}
                            >
                              {tasks.length}
                            </span>
                          </div>

                          <div className="mt-4 space-y-3">
                            {tasks.length ? (
                              tasks.map((task) => (
                                <article
                                  key={task.task_id}
                                  className="rounded-2xl border border-black/10 bg-white p-4 shadow-sm"
                                >
                                  <div className="flex items-start justify-between gap-3">
                                    <div>
                                      <p className="text-xs uppercase tracking-[0.2em] text-black/45">
                                        Priority {task.priority}
                                      </p>
                                      <h4 className="mt-2 text-base font-semibold leading-6">
                                        {task.ticket_name}
                                      </h4>
                                    </div>
                                    <span className="rounded-full bg-black/[0.04] px-2.5 py-1 text-[11px] uppercase tracking-[0.2em] text-black/65">
                                      {task.assignee || "unassigned"}
                                    </span>
                                  </div>

                                  <p className="mt-3 text-sm leading-6 text-black/72">{task.description}</p>

                                  {task.notes ? (
                                    <div className="mt-4 rounded-2xl border border-black/8 bg-black/[0.03] p-3">
                                      <p className="text-[11px] uppercase tracking-[0.2em] text-black/45">Notes</p>
                                      <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-black/68">
                                        {task.notes}
                                      </p>
                                    </div>
                                  ) : null}

                                  <div className="mt-4 flex items-center justify-between gap-3 text-xs text-black/45">
                                    <span>ID {task.task_id.slice(0, 8)}</span>
                                    <span>Updated {formatDate(task.updated_at)}</span>
                                  </div>
                                </article>
                              ))
                            ) : (
                              <div className="rounded-2xl border border-dashed border-black/12 bg-white/55 px-4 py-8 text-center text-sm text-black/45">
                                No tasks in this state.
                              </div>
                            )}
                          </div>
                        </section>
                      );
                    })}
                  </div>
                </div>
              ) : null}
            </section>
          </>
        ) : null}
      </div>
    </main>
  );
}
