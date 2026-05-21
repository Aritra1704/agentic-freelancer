import { NextResponse } from "next/server";

import { runSalesTrigger } from "../../../../lib/server/task-board";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST() {
  try {
    const result = await runSalesTrigger();
    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to run sales trigger.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
