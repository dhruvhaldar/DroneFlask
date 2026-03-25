import { NextResponse } from "next/server";

export const runtime = "nodejs";

let lastState = {
  throttle: 0,
  pitch: 0,
  roll: 0,
  yaw: 0,
  mode: "Manual",
  armed: false,
  updatedAt: new Date().toISOString()
};

export async function GET() {
  return NextResponse.json(lastState);
}

export async function POST(req: Request) {
  const incoming = (await req.json()) as Partial<typeof lastState>;
  lastState = {
    ...lastState,
    ...incoming,
    updatedAt: new Date().toISOString()
  };
  return NextResponse.json(lastState);
}
