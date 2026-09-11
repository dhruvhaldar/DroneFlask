export type CameraMode = "Chase" | "FPV" | "Orbit";
export type FlightMode = "Stabilized" | "Sport";
export type FlightState = {
  x: number; y: number; z: number; vx: number; vy: number; vz: number;
  yaw: number; pitch: number; roll: number; armed: boolean; landing: boolean;
  returning: boolean; paused: boolean; battery: number; elapsed: number;
  distance: number; gates: number; crashed: boolean; message: string;
};
export const gates = [
  { x: 0, y: 7, z: -30 }, { x: 0, y: 10, z: -65 },
  { x: 20, y: 13, z: -100 }, { x: 48, y: 10, z: -130 },
  { x: 80, y: 16, z: -165 }, { x: 100, y: 12, z: -200 },
];
export const obstacles = [
  { x: -43, z: -70, w: 23, d: 30, h: 18 },
  { x: -70, z: -120, w: 28, d: 24, h: 32 },
  { x: 54, z: -65, w: 20, d: 24, h: 23 },
  { x: 95, z: -110, w: 24, d: 26, h: 32 },
  { x: -35, z: -180, w: 30, d: 35, h: 20 },
];
export const initialFlight = (): FlightState => ({
  x: 0, y: 0.65, z: 0, vx: 0, vy: 0, vz: 0, yaw: 0, pitch: 0, roll: 0,
  armed: false, landing: false, returning: false, paused: false, battery: 100,
  elapsed: 0, distance: 0, gates: 0, crashed: false, message: "Preflight complete. Ready for takeoff.",
});
export function takeoff(s: FlightState) {
  if (s.crashed || s.battery <= 0) { s.message = "Reset the flight to launch again."; return; }
  s.armed = true; s.landing = false; s.returning = false;
  s.message = "Motors armed. Hold Space to climb.";
}
export function stepFlight(s: FlightState, keys: Set<string>, dt: number, mode: FlightMode, wind: number) {
  if (s.paused || s.crashed || !s.armed) return;
  dt = Math.min(dt, 0.04);
  const old = { x: s.x, y: s.y, z: s.z };
  const forward = Number(keys.has("KeyW") || keys.has("ArrowUp")) - Number(keys.has("KeyS") || keys.has("ArrowDown"));
  const right = Number(keys.has("KeyD") || keys.has("ArrowRight")) - Number(keys.has("KeyA") || keys.has("ArrowLeft"));
  const up = Number(keys.has("Space")) - Number(keys.has("ShiftLeft") || keys.has("ShiftRight"));
  const yawInput = Number(keys.has("KeyQ")) - Number(keys.has("KeyE"));
  const speed = mode === "Sport" ? 25 : 13;
  s.yaw += yawInput * dt * 1.3;
  let tx = (right * Math.cos(s.yaw) - forward * Math.sin(s.yaw)) * speed;
  let tz = (-forward * Math.cos(s.yaw) - right * Math.sin(s.yaw)) * speed;
  let ty = up * 7;
  if (s.returning) {
    tx = Math.max(-10, Math.min(10, -s.x)); tz = Math.max(-10, Math.min(10, -s.z));
    ty = Math.max(-4, Math.min(4, 40 - s.y));
    if (s.y < 36 && Math.hypot(s.x, s.z) > 2) { tx = 0; tz = 0; }
    if (Math.hypot(s.x, s.z) < 1) { s.returning = false; s.landing = true; }
  }
  if (s.landing) { tx = 0; tz = 0; ty = -2; }
  if (!s.landing && !s.returning && s.y < 3 && !up) ty = (3 - s.y) * 1.5;
  const blend = 1 - Math.exp(-dt * (mode === "Sport" ? 2.2 : 4));
  s.vx += (tx + (s.landing || s.returning ? 0 : wind * 0.3 * Math.sin(s.elapsed * .7)) - s.vx) * blend;
  s.vz += (tz - s.vz) * blend; s.vy += (ty - s.vy) * blend;
  s.pitch += (-forward * .3 - s.pitch) * blend; s.roll += (-right * .3 - s.roll) * blend;
  s.x += s.vx * dt; s.z += s.vz * dt; s.y += s.vy * dt;
  if (Math.abs(s.x) > 245 || Math.abs(s.z) > 245) {
    s.x = Math.max(-245, Math.min(245, s.x)); s.z = Math.max(-245, Math.min(245, s.z));
    s.vx = 0; s.vz = 0; s.message = "Flight boundary reached. Turn back toward the airfield.";
  }
  if (s.y > 100) { s.y = 100; s.vy = Math.min(0, s.vy); s.message = "Altitude ceiling: 100 m."; }
  const obstacle = obstacles.some(o => Math.abs(s.x - o.x) < o.w / 2 + .8 && Math.abs(s.z - o.z) < o.d / 2 + .8 && s.y < o.h + .5);
  if (obstacle || (s.y < .65 && s.vy < -4)) {
    s.crashed = true; s.armed = false; s.message = "Collision detected. Press R to reset your flight.";
    s.vx = s.vy = s.vz = 0; s.y = Math.max(.65, s.y); return;
  }
  if (s.y <= .65) {
    s.y = .65; s.vy = 0;
    if (s.landing || up < 0) { s.armed = false; s.landing = false; s.vx = s.vz = 0; s.message = "Touchdown. Motors disarmed."; }
  }
  s.distance += Math.hypot(s.x - old.x, s.y - old.y, s.z - old.z);
  s.elapsed += dt; s.battery = Math.max(0, s.battery - dt * .035 * (1 + Math.hypot(s.vx, s.vz) / 30));
  if (s.battery < 15 && !s.landing && !s.returning) { s.returning = true; s.message = "Low battery. Returning home automatically."; }
  if (s.battery <= 0) { s.returning = false; s.landing = true; }
  const gate = gates[s.gates];
  if (gate && (old.z - gate.z) * (s.z - gate.z) <= 0 && old.z !== s.z) {
    const t = (gate.z - old.z) / (s.z - old.z);
    if (Math.hypot(old.x + (s.x - old.x) * t - gate.x, old.y + (s.y - old.y) * t - gate.y) < 4.2) {
      s.gates++; s.message = s.gates === gates.length ? "Course complete. Beautiful flying!" : `Gate ${s.gates} cleared. On to the next.`;
    }
  }
}
