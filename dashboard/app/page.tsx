"use client";

import { useEffect, useState } from "react";

type Lead = {
  id: string;
  title: string;
  platform: string;
  budget: string;
  status: string;
  suggested_stack: string[];
  pitch_content?: string | null;
};

type Summary = {
  counts: Record<string, number>;
  recent: Lead[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function Page() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);

  useEffect(() => {
    const load = async () => {
      const [summaryResponse, leadsResponse] = await Promise.all([
        fetch(`${API_BASE}/dashboard/summary`).then((res) => res.json()),
        fetch(`${API_BASE}/leads`).then((res) => res.json())
      ]);
      setSummary(summaryResponse);
      setLeads(leadsResponse);
    };

    load().catch(() => {
      setSummary({ counts: {}, recent: [] });
      setLeads([]);
    });
  }, []);

  return (
    <main className="min-h-screen px-6 py-10 text-ink">
      <div className="mx-auto max-w-6xl space-y-8">
        <section className="rounded-[2rem] border border-black/10 bg-white/70 p-8 shadow-xl backdrop-blur">
          <p className="text-sm uppercase tracking-[0.3em] text-moss">Freelance-OS</p>
          <h1 className="mt-3 text-5xl font-semibold tracking-tight">Control Tower</h1>
          <p className="mt-4 max-w-2xl text-lg text-black/70">
            Live lead pipeline, strategy outputs, and execution signals from the Freelance-OS agent stack.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-4">
          {Object.entries(summary?.counts || {}).map(([status, count]) => (
            <div key={status} className="rounded-3xl border border-black/10 bg-fog p-5 shadow-sm">
              <p className="text-xs uppercase tracking-[0.2em] text-black/55">{status}</p>
              <p className="mt-3 text-4xl font-semibold">{count}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-3xl border border-black/10 bg-white/80 p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold">Lead Inbox</h2>
              <span className="rounded-full bg-clay px-3 py-1 text-xs font-medium text-white">
                {leads.length} total
              </span>
            </div>
            <div className="mt-6 space-y-4">
              {leads.map((lead) => (
                <article key={lead.id} className="rounded-2xl border border-black/10 bg-white p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-medium">{lead.title}</h3>
                      <p className="text-sm text-black/60">{lead.platform} · {lead.budget}</p>
                    </div>
                    <span className="rounded-full border border-moss/20 bg-moss/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-moss">
                      {lead.status}
                    </span>
                  </div>
                  {lead.suggested_stack?.length ? (
                    <p className="mt-3 text-sm text-black/70">
                      Stack: {lead.suggested_stack.join(", ")}
                    </p>
                  ) : null}
                </article>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-black/10 bg-ink p-6 text-white shadow-sm">
            <h2 className="text-2xl font-semibold">Recent Strategy Signal</h2>
            <div className="mt-6 space-y-4">
              {(summary?.recent || []).map((lead) => (
                <article key={lead.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-white/55">{lead.status}</p>
                  <h3 className="mt-2 text-lg font-medium">{lead.title}</h3>
                  <p className="mt-2 line-clamp-4 text-sm text-white/70">
                    {lead.pitch_content || "No strategy draft yet."}
                  </p>
                </article>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
