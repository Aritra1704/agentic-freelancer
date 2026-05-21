import { NextResponse } from "next/server";

import { runLegalTrigger } from "../../../../lib/server/task-board";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST() {
  try {
    const result = await runLegalTrigger();
    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to run legal trigger.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
