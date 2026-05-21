import { NextResponse } from "next/server";

import { getTaskBoardSnapshot } from "../../../lib/server/task-board";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const snapshot = await getTaskBoardSnapshot();
    return NextResponse.json(snapshot, {
      headers: {
        "Cache-Control": "no-store"
      }
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to load task board.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
