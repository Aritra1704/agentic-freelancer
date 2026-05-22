"use client";

import { LeadInboxPayload } from "../../lib/types";

type LeadInboxProps = {
  inbox: LeadInboxPayload | null;
  isLoading: boolean;
  isRefreshing: boolean;
  actingLeadId: string | null;
  actingAction: "approve" | "reject" | null;
  onApprove: (leadId: string) => void;
  onReject: (leadId: string) => void;
  formatDate: (value: string | null) => string;
};

function formatStatusLabel(status: string | null) {
  return (status || "unknown").replaceAll("_", " ");
}

export default function LeadInbox({
  inbox,
  isLoading,
  isRefreshing,
  actingLeadId,
  actingAction,
  onApprove,
  onReject,
  formatDate
}: LeadInboxProps) {
  const leads = inbox?.leads || [];
  const platformEntries = Object.entries(inbox?.counts.by_platform || {});
  const statusEntries = Object.entries(inbox?.counts.by_status || {});

  return (
    <section className="rounded-[2rem] border border-black/10 bg-white/70 p-5 shadow-[0_18px_50px_rgba(16,20,24,0.08)] backdrop-blur sm:p-6">
      <div className="flex flex-col gap-3 border-b border-black/10 pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-black/45">Lead Inbox</p>
          <h2 className="mt-2 text-3xl font-semibold">Manual Lead Vetting</h2>
        </div>
        <p className="text-sm text-black/65">
          {isLoading ? "Loading lead inbox..." : `${leads.length} leads awaiting a manual decision`}
          {isRefreshing ? " Refreshing in background..." : ""}
        </p>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[0.75fr_1.25fr]">
        <div className="space-y-4">
          <article className="rounded-3xl border border-black/10 bg-fog/80 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-black/45">Platform Split</p>
            <div className="mt-4 space-y-3">
              {platformEntries.length ? (
                platformEntries.map(([platform, count]) => (
                  <div key={platform} className="flex items-center justify-between gap-3 text-sm text-black/72">
                    <span>{platform}</span>
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-black/70">
                      {count}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-black/55">No inbox leads yet.</p>
              )}
            </div>
          </article>

          <article className="rounded-3xl border border-black/10 bg-fog/80 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-black/45">Lead Statuses</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {statusEntries.length ? (
                statusEntries.map(([status, count]) => (
                  <span
                    key={status}
                    className="rounded-full border border-black/10 bg-white px-3 py-1 text-xs uppercase tracking-[0.18em] text-black/65"
                  >
                    {formatStatusLabel(status)} · {count}
                  </span>
                ))
              ) : (
                <p className="text-sm text-black/55">No active lead statuses to review.</p>
              )}
            </div>
          </article>
        </div>

        <div className="space-y-4">
          {isLoading && !inbox ? (
            <div className="rounded-3xl border border-dashed border-black/12 bg-white/55 px-4 py-16 text-center text-sm text-black/45">
              Loading lead inbox...
            </div>
          ) : null}

          {!isLoading && leads.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-black/12 bg-white/55 px-4 py-16 text-center text-sm text-black/45">
              No leads are waiting in the inbox. New scout output will appear here until you approve
              or reject it.
            </div>
          ) : null}

          {leads.map((lead) => {
            const isActing = actingLeadId === lead.id;

            return (
              <article
                key={lead.id}
                className="rounded-3xl border border-black/10 bg-white p-5 shadow-sm"
              >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="max-w-3xl">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-clay/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-clay">
                        {lead.platform || "Unknown Platform"}
                      </span>
                      <span className="rounded-full bg-black/[0.05] px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-black/60">
                        {formatStatusLabel(lead.status)}
                      </span>
                      {lead.job_id ? (
                        <span className="rounded-full bg-blue-500/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-blue-600">
                          {lead.job_id}
                        </span>
                      ) : null}
                      {lead.engagement_type ? (
                        <span className="rounded-full bg-purple-500/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-purple-600">
                          {lead.engagement_type}
                        </span>
                      ) : null}
                      {lead.valuation_label ? (
                        <span className={`rounded-full px-3 py-1 text-[11px] uppercase tracking-[0.2em] ${lead.valuation_label === "High" ? "bg-red-500/10 text-red-600" : "bg-yellow-500/10 text-yellow-600"}`}>
                          {lead.valuation_label} Value
                        </span>
                      ) : null}
                      {lead.priority !== null ? (
                        <span className="rounded-full bg-moss/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-moss">
                          Priority {lead.priority}
                        </span>
                      ) : null}
                      {lead.opportunity_score !== null ? (
                        <span className="rounded-full bg-moss/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-moss">
                          Score {lead.opportunity_score}
                        </span>
                      ) : null}
                    </div>

                    <h3 className="mt-4 text-xl font-semibold leading-7">
                      {lead.title || "Untitled Lead"}
                    </h3>

                    <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm text-black/58">
                      <span>Budget: {lead.budget || "Unknown"}</span>
                      <span>Updated: {formatDate(lead.last_updated_at)}</span>
                      {lead.url ? (
                        <a
                          href={lead.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-moss underline decoration-moss/30 underline-offset-4 transition hover:decoration-moss"
                        >
                          Open source listing
                        </a>
                      ) : null}
                    </div>

                    <p className="mt-4 text-sm leading-6 text-black/72">
                      {lead.description || "No description was stored for this lead."}
                    </p>
                  </div>

                  <div className="flex min-w-[220px] flex-col gap-3">
                    <button
                      type="button"
                      onClick={() => onApprove(lead.id)}
                      disabled={isActing}
                      className="rounded-2xl border border-moss/20 bg-moss px-4 py-3 text-sm font-medium text-white transition hover:bg-moss/90 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {isActing && actingAction === "approve" ? "Approving..." : "Approve To Task Board"}
                    </button>
                    <button
                      type="button"
                      onClick={() => onReject(lead.id)}
                      disabled={isActing}
                      className="rounded-2xl border border-red-700/15 bg-red-600/10 px-4 py-3 text-sm font-medium text-red-900 transition hover:bg-red-600/15 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {isActing && actingAction === "reject" ? "Rejecting..." : "Reject Lead"}
                    </button>
                  </div>
                </div>

                {(lead.tags.length || lead.suggested_stack.length) ? (
                  <div className="mt-5 flex flex-wrap gap-2">
                    {[...lead.tags, ...lead.suggested_stack]
                      .filter((value, index, all) => all.indexOf(value) === index)
                      .map((tag) => (
                        <span
                          key={tag}
                          className="rounded-full border border-black/10 bg-black/[0.03] px-3 py-1 text-xs text-black/65"
                        >
                          {tag}
                        </span>
                      ))}
                  </div>
                ) : null}

                {lead.qualification_notes ? (
                  <div className="mt-5 rounded-2xl border border-black/8 bg-black/[0.03] p-4">
                    <p className="text-[11px] uppercase tracking-[0.2em] text-black/45">
                      Qualification Notes
                    </p>
                    <p className="mt-2 text-sm leading-6 text-black/68">{lead.qualification_notes}</p>
                  </div>
                ) : null}

                {lead.technical_doubts.length ? (
                  <div className="mt-5 rounded-2xl border border-black/8 bg-black/[0.03] p-4">
                    <p className="text-[11px] uppercase tracking-[0.2em] text-black/45">
                      Vetting Questions
                    </p>
                    <div className="mt-3 space-y-2">
                      {lead.technical_doubts.slice(0, 5).map((question) => (
                        <p key={question} className="text-sm leading-6 text-black/68">
                          {question}
                        </p>
                      ))}
                    </div>
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
