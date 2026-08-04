"use client";

import { useMemo, useState, useEffect } from "react";

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

const modeIcons: Record<FlightMode, string> = {
  "Manual": "🕹️",
  "Stabilize": "⚖️",
  "Altitude Hold": "↕️",
  "Position Hold": "📍"
};

const modeTooltips: Record<FlightMode, string> = {
  "Manual": "Direct pilot control with no stabilization",
  "Stabilize": "Self-levels the drone when sticks are released",
  "Altitude Hold": "Maintains current altitude automatically",
  "Position Hold": "Maintains current 3D position using GPS"
};

export function ControlPanel() {
  const [state, setState] = useState<ControlState>(initialState);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(false);
  const [hoveredMode, setHoveredMode] = useState<FlightMode | null>(null);
  const [confirmAction, setConfirmAction] = useState<"arm" | "disarm" | null>(null);

  const batteryPct = useMemo(() => Math.max(12, Math.round(100 - state.throttle * 0.62)), [state.throttle]);

  useEffect(() => {
    document.title = error ? "⚠️ Offline - Drone Control Station" : state.armed ? "🚨 Armed - Drone Control Station" : "🛡️ Safe - Drone Control Station";

    if (state.armed) {
      const handleBeforeUnload = (e: BeforeUnloadEvent) => {
        e.preventDefault();
        return (e.returnValue = "");
      };
      window.addEventListener("beforeunload", handleBeforeUnload);
      return () => window.removeEventListener("beforeunload", handleBeforeUnload);
    }
  }, [error, state.armed]);

  async function pushState(next: ControlState) {
    setState(next);
    setSaving(true);
    setError(false);
    try {
      const res = await fetch("/api/state", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(next)
      });
      if (!res.ok) throw new Error("Sync failed");
      const updated = (await res.json()) as ControlState;
      setState(updated);
    } catch {
      setError(true);
    } finally {
      setSaving(false);
    }
  }

  function updateAxis(axis: keyof Pick<ControlState, "throttle" | "pitch" | "roll" | "yaw">, value: number) {
    setConfirmAction(null);
    if (state[axis] === value) return;
    void pushState({ ...state, [axis]: value });
  }

  return (
    <div className="grid" style={{ marginTop: "1.1rem" }}>
      <section className="glass panel" aria-labelledby="controls-title">
        <h2 id="controls-title" className="section-title">Flight Controls</h2>
        <datalist id="center-snap"><option value="0" /></datalist>
        {(["throttle", "pitch", "roll", "yaw"] as const).map((axis) => (
          <div key={axis} style={{ marginBottom: "0.9rem" }}>
            <div className="row" onDoubleClick={() => updateAxis(axis, 0)} title={axis === "throttle" ? "Double-click to zero" : "Double-click to center"} style={{ userSelect: "none" }}>
              <span style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
                <label htmlFor={axis} style={{ textTransform: "capitalize", cursor: "pointer" }}>
                  {axis}
                </label>
                <span id={`${axis}-hint`} className="subtle" style={{ fontSize: "0.75rem" }}>
                  {axis === "throttle" ? (
                    <>Double-click or <kbd><abbr title="Escape" style={{ textDecoration: "none" }}>Esc</abbr></kbd> to zero</>
                  ) : (
                    <>Double-click or <kbd>0</kbd> / <kbd><abbr title="Center" style={{ textDecoration: "none" }}>C</abbr></kbd> to center</>
                  )}
                </span>
              </span>
              <output htmlFor={axis} className={`value ${state[axis] === 0 ? "subtle" : ""}`.trim()} aria-hidden="true">
                {state[axis] > 0 && axis !== "throttle" ? "+" : ""}
                {state[axis]}%
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
              aria-keyshortcuts={axis === "throttle" ? "Escape" : "Escape 0 c"}
              aria-valuetext={state[axis] > 0 && axis !== "throttle" ? `+${state[axis]}%` : `${state[axis]}%`}
              onChange={(event) => updateAxis(axis, Number(event.target.value))}
              onDoubleClick={() => updateAxis(axis, 0)}
              onKeyDown={(e) => {
                if (e.key === "Escape" || e.key === "0" || (axis !== "throttle" && e.key.toLowerCase() === "c")) {
                  updateAxis(axis, 0);
                }
              }}
            />
          </div>
        ))}
      </section>

      <section className="glass panel" aria-labelledby="mode-arm-title">
        <h2 id="mode-arm-title" className="section-title">Mode + Arm</h2>
        <div className="btn-group" role="group" aria-label="Flight Modes" style={{ marginBottom: "0.7rem" }}>
          {modes.map((mode) => (
            <button
              key={mode}
              className={state.mode === mode ? "active" : ""}
              aria-pressed={state.mode === mode}
              aria-disabled={saving ? "true" : undefined}
              aria-describedby="mode-description"
              onMouseEnter={() => setHoveredMode(mode)}
              onMouseLeave={() => setHoveredMode(null)}
              onFocus={() => setHoveredMode(mode)}
              onBlur={() => setHoveredMode(null)}
              onClick={() => {
                setConfirmAction(null);
                if (saving || state.mode === mode) return;
                void pushState({ ...state, mode });
              }}
              type="button"
              title={saving ? "Action unavailable while syncing" : undefined}
            >
              <span aria-hidden="true">{modeIcons[mode]} </span>{mode}
            </button>
          ))}
        </div>
        <p id="mode-description" className="subtle" style={{ fontSize: "0.85rem", marginBottom: "1rem", minHeight: "2.5em" }}>
          {modeTooltips[hoveredMode || state.mode]}
        </p>

        <button
          type="button"
          onClick={() => {
            if (saving) return;
            if (!state.armed && state.throttle > 0) {
              void pushState({ ...state, throttle: 0 });
              return;
            }
            if (!state.armed) {
              if (confirmAction === "arm") {
                void pushState({ ...state, armed: true });
                setConfirmAction(null);
              } else {
                setConfirmAction("arm");
              }
            } else {
              if (state.throttle > 0) {
                if (confirmAction === "disarm") {
                  void pushState({ ...state, armed: false });
                  setConfirmAction(null);
                } else {
                  setConfirmAction("disarm");
                }
              } else {
                void pushState({ ...state, armed: false });
                setConfirmAction(null);
              }
            }
          }}
          onBlur={() => setConfirmAction(null)}
          onKeyDown={(e) => {
            if (e.key === "Escape" && confirmAction) {
              e.stopPropagation();
              setConfirmAction(null);
            }
          }}
          className={state.armed ? "active" : ""}
          aria-disabled={saving ? "true" : undefined}
          aria-describedby={confirmAction ? "confirm-alert" : undefined}
          aria-keyshortcuts={confirmAction ? "Escape" : undefined}
          title={saving ? "Action unavailable while syncing" : (!state.armed && state.throttle > 0) ? "Click to set throttle to 0 so you can arm motors" : undefined}
          style={{
            width: "100%",
            borderColor: confirmAction ? "#ff8c8c" : undefined,
            boxShadow: confirmAction ? "0 0 0 1px #ff8c8c inset" : undefined
          }}
        >
          {confirmAction ? (
            <><span aria-hidden="true">⚠️</span> Confirm {confirmAction === "arm" ? "Arm" : "Disarm"}</>
          ) : (!state.armed && state.throttle > 0) ? (
            <><span aria-hidden="true">⬇️</span> Auto-Zero Throttle</>
          ) : state.armed ? (
            <><span aria-hidden="true">🔒</span> Disarm</>
          ) : (
            <><span aria-hidden="true">🚀</span> Arm Motors</>
          )}
        </button>

        <span className="status-pill" style={{ color: error || state.armed ? "#ff8c8c" : undefined, borderColor: error || state.armed ? "#ff8c8c" : undefined }}>{error ? <><span aria-hidden="true">⚠️</span> Offline</> : state.armed ? <><span aria-hidden="true">🚨</span> Armed</> : <><span aria-hidden="true">🛡️</span> Safe</>} · {state.mode}</span>

        <div style={{ minHeight: "4.25rem", marginTop: "0.75rem" }}>
          {confirmAction && (
            <div id="confirm-alert" role="alert">
              <p style={{ fontSize: "0.85rem", color: "#ff8c8c", fontWeight: 500 }}>
                {confirmAction === "arm"
                  ? "WARNING: Propellers will spin up. Ensure area is clear. Click again to confirm."
                  : "DANGER: Throttle is active. Drone will fall. Click again to confirm."}
              </p>
              <div className="row" style={{ marginTop: "0.5rem", marginBottom: 0 }}>
                <p className="subtle" style={{ fontSize: "0.85rem" }}>
                  Or press <kbd><abbr title="Escape" style={{ textDecoration: "none" }}>Esc</abbr></kbd> to cancel.
                </p>
                <button type="button" className="subtle" onMouseDown={(e) => e.preventDefault()} onClick={() => setConfirmAction(null)}>
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </section>

      <section className="glass panel" style={{ gridColumn: "1 / -1" }} aria-labelledby="telemetry-title">
        <h2 id="telemetry-title" className="section-title">Telemetry</h2>
        <dl className="grid" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", margin: 0 }} aria-busy={saving}>
          <div>
            <dt className="subtle"><span aria-hidden="true">🔋</span> Battery</dt>
            <dd className="value" style={{ margin: 0 }}>
              {batteryPct}%
              <meter value={batteryPct} min="0" max="100" low={20} high={80} optimum={100} aria-hidden="true" style={{ width: "100%", display: "block", marginTop: "0.25rem" }} />
            </dd>
          </div>
          <div>
            <dt className="subtle"><span aria-hidden="true">📶</span> Link Quality</dt>
            <dd className="value" style={{ margin: 0 }}>
              {Math.max(51, 100 - Math.abs(state.yaw))}%
              <meter value={Math.max(51, 100 - Math.abs(state.yaw))} min="0" max="100" low={30} high={70} optimum={100} aria-hidden="true" style={{ width: "100%", display: "block", marginTop: "0.25rem" }} />
            </dd>
          </div>
          <div>
            <dt className="subtle"><span aria-hidden="true">↕️</span> Vertical Speed</dt>
            <dd className="value" style={{ margin: 0 }}>{(state.throttle / 10).toFixed(1)} m/s</dd>
          </div>
          <div>
            <dt className="subtle"><span aria-hidden="true">📡</span> Status</dt>
            <dd className="value" style={{ margin: 0, color: error ? "#ff8c8c" : undefined }} title={error ? "Failed to sync control state. Check connection." : undefined}>
              {saving ? <span className="subtle"><span aria-hidden="true" className="spin">🔄</span> Syncing...</span> : error ? <><span aria-hidden="true">⚠️</span> Offline</> : <span className="subtle"><span aria-hidden="true">✓</span> Synced</span>}
            </dd>
          </div>
        </dl>
      </section>
    </div>
  );
}
