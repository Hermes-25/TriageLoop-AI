import { NextRequest, NextResponse } from "next/server";
import { handleVercelDemo } from "@/app/lib/vercel-demo";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type RouteContext = { params: Promise<{ path: string[] }> };

async function proxy(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  if (process.env.VERCEL === "1" || process.env.TRIAGELOOP_PRESENTATION_ADAPTER === "1") {
    return handleVercelDemo(request, path);
  }
  const base = process.env.TRIAGELOOP_API_URL ?? process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
  const upstream = new URL(path.join("/"), `${base}/`);
  upstream.search = request.nextUrl.search;
  const body = request.method === "GET" || request.method === "HEAD" ? undefined : await request.text();

  try {
    const response = await fetch(upstream, {
      method: request.method,
      headers: body ? { "Content-Type": request.headers.get("content-type") ?? "application/json" } : undefined,
      body,
      cache: "no-store",
    });
    return new NextResponse(response.body, {
      status: response.status,
      headers: { "Content-Type": response.headers.get("content-type") ?? "application/json" },
    });
  } catch {
    return NextResponse.json(
      { detail: "TriageLoop decision service is unavailable. Start the FastAPI service and retry." },
      { status: 503 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
