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

const modeTooltips: Record<FlightMode, string> = {
  "Manual": "Direct pilot control with no stabilization",
  "Stabilize": "Self-levels the drone when sticks are released",
  "Altitude Hold": "Maintains current altitude automatically",
  "Position Hold": "Maintains current 3D position using GPS"
};

export function ControlPanel() {
  const [state, setState] = useState<ControlState>(initialState);
  const [saving, setSaving] = useState(false);
  const [hoveredMode, setHoveredMode] = useState<FlightMode | null>(null);

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
        <datalist id="center-snap"><option value="0" /></datalist>
        {(["throttle", "pitch", "roll", "yaw"] as const).map((axis) => (
          <div key={axis} style={{ marginBottom: "0.9rem" }}>
            <div className="row">
              <label htmlFor={axis} style={{ textTransform: "capitalize" }}>
                {axis}
              </label>
              <span id={`${axis}-hint`} className="subtle" style={{ fontSize: "0.75rem", marginLeft: "0.5rem" }}>
                {axis === "throttle" ? "(Double-click or 'Esc' to zero)" : "(Double-click or '0' to center)"}
              </span>
              <output htmlFor={axis} className="value" aria-hidden="true">
                {state[axis] > 0 ? "+" : ""}
                {state[axis]}
              </output>
            </div>
            <input
              id={axis}
              type="range"
              list={axis === "throttle" ? undefined : "center-snap"}
              min={axis === "throttle" ? 0 : -100}
              max={100}
              value={state[axis]}
              title={axis === "throttle" ? "Drag to adjust throttle" : `Drag to adjust ${axis} (center snaps to 0)`}
              aria-describedby={`${axis}-hint`}
              onChange={(event) => updateAxis(axis, Number(event.target.value))}
              onDoubleClick={() => updateAxis(axis, 0)}
              onKeyDown={(e) => {
                if (e.key === "Escape" || e.key === "0" || (axis !== "throttle" && e.key === "c")) {
                  updateAxis(axis, 0);
                }
              }}
            />
          </div>
        ))}
      </section>

      <section className="glass panel">
        <h2 className="section-title">Mode + Arm</h2>
        <div className="btn-group" role="group" aria-label="Flight Modes" style={{ marginBottom: "0.7rem" }}>
          {modes.map((mode) => (
            <button
              key={mode}
              className={state.mode === mode ? "active" : ""}
              aria-pressed={state.mode === mode}
              aria-describedby="mode-description"
              onMouseEnter={() => setHoveredMode(mode)}
              onMouseLeave={() => setHoveredMode(null)}
              onFocus={() => setHoveredMode(mode)}
              onBlur={() => setHoveredMode(null)}
              onClick={() => void pushState({ ...state, mode })}
              type="button"
            >
              {mode}
            </button>
          ))}
        </div>
        <p id="mode-description" className="subtle" style={{ fontSize: "0.85rem", marginBottom: "1rem", minHeight: "2.5em" }} aria-live="polite">
          {modeTooltips[hoveredMode || state.mode]}
        </p>

        <button
          type="button"
          onClick={() => {
            if (!state.armed && state.throttle > 0) {
              void pushState({ ...state, throttle: 0 });
              return;
            }
            if (!state.armed) {
              if (window.confirm("WARNING: Propellers will spin up. Ensure the area is clear. Arm motors?")) {
                void pushState({ ...state, armed: true });
              }
            } else {
              void pushState({ ...state, armed: false });
            }
          }}
          className={state.armed ? "active" : ""}
          aria-pressed={(!state.armed && state.throttle > 0) ? undefined : state.armed}
          title={(!state.armed && state.throttle > 0) ? "Click to set throttle to 0 so you can arm motors" : undefined}
          style={{
            width: "100%",
            opacity: (!state.armed && state.throttle > 0) ? 0.8 : 1,
            cursor: "pointer"
          }}
        >
          {!state.armed && state.throttle > 0 ? "Zero Throttle to Arm" : state.armed ? "Disarm" : "Arm Motors"}
        </button>

        <span className="status-pill" aria-live="polite">{state.armed ? "🚨 Armed" : "🛡️ Safe"} · {state.mode}</span>
      </section>

      <section className="glass panel" style={{ gridColumn: "1 / -1" }}>
        <h2 className="section-title">Telemetry</h2>
        <dl className="grid" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", margin: 0 }} aria-busy={saving}>
          <div>
            <dt className="subtle">🔋 Battery</dt>
            <dd className="value" style={{ margin: 0 }}>{batteryPct}%</dd>
          </div>
          <div>
            <dt className="subtle">📶 Link Quality</dt>
            <dd className="value" style={{ margin: 0 }}>{Math.max(51, 100 - Math.abs(state.yaw))}%</dd>
          </div>
          <div>
            <dt className="subtle">↕️ Vertical Speed</dt>
            <dd className="value" style={{ margin: 0 }}>{(state.throttle / 10).toFixed(1)} m/s</dd>
          </div>
          <div>
            <dt className="subtle">Status</dt>
            <dd className="value" style={{ margin: 0 }} aria-live="polite">{saving ? "🔄 Syncing..." : "✓ Synced"}</dd>
          </div>
        </dl>
      </section>
    </div>
  );
}
