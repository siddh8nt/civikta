import { NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.text();
  const res = await fetch(`${BACKEND}/api/analytics/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Demo-User": req.headers.get("x-demo-user") ?? "demo-oversight",
      "X-Demo-Role": req.headers.get("x-demo-role") ?? "oversight",
    },
    body,
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
