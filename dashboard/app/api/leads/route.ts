import { NextResponse } from "next/server";

import { getLeadInboxSnapshot } from "../../../lib/server/lead-inbox";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const snapshot = await getLeadInboxSnapshot();
    return NextResponse.json(snapshot, {
      headers: {
        "Cache-Control": "no-store"
      }
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to load lead inbox.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
