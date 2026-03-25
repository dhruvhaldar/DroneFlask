"use client";

import { useMemo, useState } from "react";

type FlightMode = "Manual" | "Stabilize" | "Altitude Hold" | "Position Hold";

type ControlState = {
  throttle: number;
  pitch: number;
  roll: number;
  yaw: number;
  mode: FlightMode;
  armed: boolean;
  updatedAt?: string;
};

const initialState: ControlState = {
  throttle: 0,
  pitch: 0,
  roll: 0,
  yaw: 0,
  mode: "Manual",
  armed: false
};

const modes: FlightMode[] = ["Manual", "Stabilize", "Altitude Hold", "Position Hold"];

export function ControlPanel() {
  const [state, setState] = useState<ControlState>(initialState);
  const [saving, setSaving] = useState(false);

  const batteryPct = useMemo(() => Math.max(12, Math.round(100 - state.throttle * 0.62)), [state.throttle]);

  async function pushState(next: ControlState) {
    setState(next);
    setSaving(true);
    try {
      const res = await fetch("/api/state", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(next)
      });
      const updated = (await res.json()) as ControlState;
      setState(updated);
    } finally {
      setSaving(false);
    }
  }

  function updateAxis(axis: keyof Pick<ControlState, "throttle" | "pitch" | "roll" | "yaw">, value: number) {
    void pushState({ ...state, [axis]: value });
  }

  return (
    <div className="grid" style={{ marginTop: "1.1rem" }}>
      <section className="glass panel">
        <h2 className="section-title">Flight Controls</h2>
        {(["throttle", "pitch", "roll", "yaw"] as const).map((axis) => (
          <div key={axis} style={{ marginBottom: "0.9rem" }}>
            <div className="row">
              <label htmlFor={axis} style={{ textTransform: "capitalize" }}>
                {axis}
              </label>
              <span className="value">{state[axis]}</span>
            </div>
            <input
              id={axis}
              type="range"
              min={axis === "throttle" ? 0 : -100}
              max={100}
              value={state[axis]}
              onChange={(event) => updateAxis(axis, Number(event.target.value))}
            />
          </div>
        ))}
      </section>

      <section className="glass panel">
        <h2 className="section-title">Mode + Arm</h2>
        <div className="btn-group" style={{ marginBottom: "0.7rem" }}>
          {modes.map((mode) => (
            <button
              key={mode}
              className={state.mode === mode ? "active" : ""}
              onClick={() => void pushState({ ...state, mode })}
              type="button"
            >
              {mode}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={() => void pushState({ ...state, armed: !state.armed })}
          className={state.armed ? "active" : ""}
          style={{ width: "100%" }}
        >
          {state.armed ? "Disarm" : "Arm Motors"}
        </button>

        <span className="status-pill">{state.armed ? "Armed" : "Safe"} · {state.mode}</span>
      </section>

      <section className="glass panel" style={{ gridColumn: "1 / -1" }}>
        <h2 className="section-title">Telemetry</h2>
        <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))" }}>
          <div>
            <p className="subtle">Battery</p>
            <p className="value">{batteryPct}%</p>
          </div>
          <div>
            <p className="subtle">Link Quality</p>
            <p className="value">{Math.max(51, 100 - Math.abs(state.yaw))}%</p>
          </div>
          <div>
            <p className="subtle">Vertical Speed</p>
            <p className="value">{(state.throttle / 10).toFixed(1)} m/s</p>
          </div>
          <div>
            <p className="subtle">Status</p>
            <p className="value">{saving ? "Syncing..." : "Synced"}</p>
          </div>
        </div>
      </section>
    </div>
  );
}
