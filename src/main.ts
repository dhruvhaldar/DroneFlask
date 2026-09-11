import { createIcons, Drone, CircleHelp, SlidersHorizontal, RotateCcw, RadioTower, Info, Power, ArrowDownToLine, House, ArrowUpRight, Lightbulb, ShieldCheck, Camera, Maximize, ScanLine, Map, Video, ScanEye, Orbit, Pause, MoveVertical, Gauge, BatteryFull, Timer, Flag, Keyboard, X, ArrowRight, NotebookPen, Download } from "lucide";
const icons = { Drone, CircleHelp, SlidersHorizontal, RotateCcw, RadioTower, Info, Power, ArrowDownToLine, House, ArrowUpRight, Lightbulb, ShieldCheck, Camera, Maximize, ScanLine, Map, Video, ScanEye, Orbit, Pause, MoveVertical, Gauge, BatteryFull, Timer, Flag, Keyboard, X, ArrowRight, NotebookPen, Download };
import { FlightWorld } from "./world";
import { gates, initialFlight, stepFlight, takeoff, type CameraMode, type FlightMode } from "./flight";
import "./style.css";
import { locations } from "./geography";

const icon = (name: string, cls = "") => `<i data-lucide="${name}" class="${cls}"></i>`;
const app = document.querySelector<HTMLDivElement>("#app")!;
app.innerHTML = `
<a class="skip-link" href="#flight-view">Skip to flight simulator</a>
<header class="app-header">
  <a class="brand" href="./" aria-label="Droneverse home"><span class="brand-mark">${icon("drone")}</span>Droneverse<span class="version">SIMULATOR</span></a>
  <nav aria-label="Main navigation"><button class="nav-active" id="nav-fly">Flight simulator</button><button id="nav-log">Flight log <span id="log-count">0</span></button></nav>
  <div class="header-right"><span class="local-status"><b></b> Local simulation</span><button class="icon-button" id="help" aria-label="Keyboard shortcuts">${icon("circle-help")}</button><span class="avatar">P</span></div>
</header>
<main id="main-content">
  <div class="page-heading"><div><div class="eyebrow">YOUR AIRSPACE. YOUR ADVENTURE.</div><h1>Let’s take flight<span>.</span></h1><p>A little practice. A whole new perspective.</p></div><div class="heading-actions"><button class="button" id="settings">${icon("sliders-horizontal")} Environment</button><button class="button" id="reset">${icon("rotate-ccw")} Reset flight</button></div></div>
  <div class="workspace">
    <aside class="sidebar">
      <section class="card aircraft-card"><div class="section-title"><h2>Your aircraft</h2><span class="tag">QUADCOPTER</span></div>
        <div class="drone-art" aria-hidden="true"><div class="art-grid"></div><svg viewBox="0 0 260 130"><defs><linearGradient id="shell" x2=".7" y2="1"><stop stop-color="#f5f6f2"/><stop offset="1" stop-color="#aab8ae"/></linearGradient></defs><ellipse cx="130" cy="108" rx="78" ry="8" fill="#244d35" opacity=".09"/><g stroke="#58685e" stroke-width="9" stroke-linecap="round"><path d="m125 68-49-27m63 28 49-29m-62 32-50 25m63-27 50 27"/></g><g fill="#34463c"><ellipse cx="72" cy="39" rx="40" ry="6" transform="rotate(-12 72 39)"/><ellipse cx="190" cy="39" rx="40" ry="6" transform="rotate(12 190 39)"/><ellipse cx="73" cy="99" rx="40" ry="6" transform="rotate(12 73 99)"/><ellipse cx="190" cy="99" rx="40" ry="6" transform="rotate(-12 190 99)"/></g><path d="m112 47 33-2 12 37-18 16-26-7-8-22Z" fill="url(#shell)" stroke="#929f95"/><path d="m118 51 21-1 6 19-29 1Z" fill="#546a5c"/><circle cx="128" cy="88" r="7" fill="#273b30"/><circle cx="128" cy="88" r="3" fill="#699c91"/><g fill="#f17848"><circle cx="73" cy="96" r="3"/><circle cx="190" cy="96" r="3"/></g></svg></div>
        <div class="aircraft-name"><div><h3>Scout X4</h3><span>The everyday explorer</span></div><span class="ready-dot" id="aircraft-status">Ready</span></div>
        <div class="aircraft-specs"><div><span>WEIGHT</span><b>650 <small>g</small></b></div><div><span>MAX SPEED</span><b>25 <small>m/s</small></b></div><div><span>CEILING</span><b>100 <small>m</small></b></div></div>
      </section>
      <section class="card controls-card"><div class="section-title"><h2>Flight controls</h2>${icon("radio-tower")}</div>
        <label class="field-label" for="flight-mode">Flight mode ${icon("info")}</label><select id="flight-mode"><option>Stabilized</option><option>Sport</option></select><p class="field-note" id="mode-note">Auto-leveling and altitude hold. Find your flow.</p>
        <button class="button primary launch" id="launch">${icon("power")} Arm & take off <kbd>F</kbd></button>
        <div class="paired"><button class="button" id="land">${icon("arrow-down-to-line")} Land</button><button class="button" id="return">${icon("house")} Return</button></div>
        <div class="control-divider"></div><div class="section-title"><h2>Keyboard controls</h2><button class="text-button" id="all-keys">View all ${icon("arrow-up-right")}</button></div>
        <div class="key-row"><div class="keys"><kbd>W</kbd><span><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd></span></div><div><b>Move around</b><small>Forward, left, back, right</small></div></div>
        <div class="key-row compact"><span><kbd>Q</kbd><kbd>E</kbd></span><div><b>Rotate</b><small>Yaw left / right</small></div></div>
        <div class="key-row compact"><span><kbd class="wide">Space</kbd><kbd class="wide">Shift</kbd></span><div><b>Altitude</b><small>Ascend / descend</small></div></div>
        <div class="tip">${icon("lightbulb")} Release the keys to hover in place.</div>
      </section>
      <div class="sidebar-foot">${icon("shield-check")} All the freedom. No real-world risk.</div>
    </aside>
    <div class="flight-column">
      <section class="viewport" id="flight-view" tabindex="0" aria-label="Flight simulator. Press F to take off. WASD to move, Space to ascend, Shift to descend.">
        <div id="world"></div><div id="map-status" class="map-status" role="status">Loading textured 3D capture… <button id="map-retry" type="button">Retry</button></div>
        <div class="viewport-top"><div class="scene-label"><span class="live-dot"></span><b><span id="location-name">Exton campus · 3D capture</span></b><span class="scene-divider"></span><span id="time-label">Daylight</span></div><div class="view-actions"><button id="record" class="view-button" aria-label="Record flight telemetry"><span class="record-dot"></span><span id="record-text">REC</span></button><button id="screenshot" class="view-button" aria-label="Save scene screenshot">${icon("camera")}</button><button id="fullscreen" class="view-button" aria-label="Toggle fullscreen">${icon("maximize")}</button></div></div>
        <div class="compass"><span>NW</span><span class="compass-tick">╵ ╵ ╵</span><b id="heading">N</b><span class="compass-tick">╵ ╵ ╵</span><span>NE</span><div class="compass-pointer"></div></div>
        <div class="hud-left"><div><span>ALTITUDE</span><b><span id="hud-alt">0.0</span><small> m</small></b></div><div class="hud-scale">─<br>─<br>──<br>─<br>─</div><div><span>VELOCITY</span><b><span id="hud-speed">0.0</span><small> m/s</small></b></div></div>
        <div class="crosshair"><span></span><span></span><span></span><span></span></div>
        <div class="training-label"><span class="training-icon">${icon("scan-line")}</span><div><span>TRAINING COURSE</span><b id="course-label">Gate 01 of 06</b></div><span id="gate-distance">31 m</span></div>
        <div class="minimap"><div class="map-header"><b>LIVE MAP</b><span>N ↑</span></div><div id="geo-minimap"></div><div class="map-footer"><span id="map-coords"></span></div></div>
        <div class="viewport-bottom"><div class="camera-switch" role="group" aria-label="Camera mode"><button data-camera="Chase">${icon("video")} Chase</button><button data-camera="FPV">${icon("scan-eye")} FPV</button><button class="active" data-camera="Orbit">${icon("orbit")} Orbit</button></div><span class="view-hint" id="view-hint">Drag to rotate the scene · Scroll to zoom</span><button class="view-button pause" id="pause" aria-label="Pause simulation">${icon("pause")}</button></div>
        <div class="pause-overlay" id="pause-overlay" hidden><span>${icon("pause")}</span><h2>Taking a breather.</h2><p>Press P or click below to resume your flight.</p><button class="button primary" id="resume">Resume flight</button></div>
        <div class="world-error" id="world-error" hidden><h2>3D graphics unavailable</h2><p>This simulator needs WebGL 2. Enable hardware acceleration in your browser and reload.</p></div>
      </section>
      <section class="telemetry" aria-label="Live flight telemetry"><div class="metric"><span>${icon("move-vertical")} ALTITUDE</span><div><b id="altitude">0.0</b><small>m</small></div><em>Above ground level</em></div><div class="metric"><span>${icon("gauge")} GROUND SPEED</span><div><b id="speed">0.0</b><small>m/s</small></div><em id="speed-note">Holding position</em></div><div class="metric"><span>${icon("battery-full")} BATTERY</span><div><b id="battery">100</b><small>%</small><span class="battery-bar"><i id="battery-fill"></i></span></div><em id="battery-note">Healthy · simulated battery</em></div><div class="metric"><span>${icon("timer")} FLIGHT TIME</span><div><b id="flight-time">00:00</b></div><em><span id="distance">0</span> m traveled</em></div></section>
      <div class="flight-status"><span><b class="status-dot"></b><span id="status-text" role="status">Preflight complete. Ready for takeoff.</span></span><span class="engine-status">THREE.JS <b>·</b> <span id="fps">60</span> FPS</span></div>
      <section class="mission-card"><div class="mission-symbol">${icon("flag")}</div><div class="mission-copy"><span>GET YOUR WINGS</span><h3>A good flight starts with a little curiosity.</h3><p>Take off, find the orange gates, and explore the landscape at your own pace.</p></div><div class="mission-progress"><div><b id="gate-count">0 / 6</b><span>gates cleared</span></div><div class="progress-track"><i id="gate-progress"></i></div></div></section>
    </div>
  </div>
  <footer><span>Made for the joy of flying.</span><span><span class="footer-dot"></span> Simulation only <span class="footer-divider">/</span> Keyboard recommended ${icon("keyboard")}</span></footer>
</main>
<dialog id="help-dialog"><div class="dialog-heading"><div><span class="eyebrow">FLIGHT SCHOOL</span><h2>Your keyboard. Your cockpit.</h2></div><button class="icon-button close-dialog" aria-label="Close">${icon("x")}</button></div><p>Arm your drone, then hold Space to climb. In Stabilized mode, releasing the controls brakes and holds altitude.</p><div class="shortcut-grid">${[["F", "Arm & take off"], ["W A S D / ↑ ← ↓ →", "Move relative to the drone"], ["Space / Shift", "Ascend / descend"], ["Q / E", "Rotate left / right"], ["L", "Land gently"], ["H", "Return home & land"], ["C", "Cycle cameras"], ["P", "Pause / resume"], ["R", "Reset flight"], ["?", "Open this guide"]].map(([key, label]) => `<div><kbd>${key}</kbd><span>${label}</span></div>`).join("")}</div><div class="dialog-tip">Chase: scroll to zoom. Orbit: drag to look around, scroll to zoom. Fly through the orange gate to advance the course. The default scene is a photographed 3D campus, with limited capture coverage. Flight follows the loaded surface, including roofs. Other locations use terrain maps.</div><button class="button primary close-dialog">Ready to explore ${icon("arrow-right")}</button></dialog>
<dialog id="settings-dialog"><div class="dialog-heading"><div><span class="eyebrow">MAKE IT YOURS</span><h2>Flight environment</h2></div><button class="icon-button close-dialog" aria-label="Close">${icon("x")}</button></div><label class="field-label" for="location">Launch location</label><select id="location">${locations.map((l, i) => `<option value="${i}">${l.name}</option>`).join("")}</select><p class="field-note">Changing location resets your flight. Exton: textured 3D buildings and vegetation (campus coverage). Other locations: terrain maps.</p><label class="setting-row"><span><b>Blue hour</b><small>A cooler sky and softer map lighting</small></span><input id="night" type="checkbox" role="switch" /></label><label class="setting-row"><span><b>Flight trail</b><small>See where you have been</small></span><input id="trail" type="checkbox" role="switch" checked /></label><label class="setting-row"><span><b>Motor audio</b><small>Procedural propeller sound</small></span><input id="sound" type="checkbox" role="switch" /></label><label class="setting-row" for="wind"><span><b>Wind strength</b><small>Crosswind adds a little challenge</small></span><output id="wind-value">0 m/s</output></label><input id="wind" type="range" min="0" max="10" step="1" value="0" /><button class="button primary close-dialog">Back to the landscape ${icon("arrow-right")}</button></dialog>
<dialog id="log-dialog"><div class="dialog-heading"><div><span class="eyebrow">YOUR FLIGHT RECORDER</span><h2>Flight log</h2></div><button class="icon-button close-dialog" aria-label="Close">${icon("x")}</button></div><p>Record live telemetry with REC. Save the session as a CSV to explore your flight data.</p><div id="log-content" class="log-empty">${icon("notebook-pen")}<h3>Your next adventure goes here.</h3><p>Start recording from the flight view.</p></div><button class="button primary" id="export" disabled>${icon("download")} Export telemetry CSV</button></dialog>
<div class="toast" id="toast" role="status" hidden></div>
`;
createIcons({ icons });
const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
let state = initialFlight();
const keys = new Set<string>();
let mode: FlightMode = "Stabilized", wind = 0;
let world: FlightWorld | undefined;
let recording = false;
let flightNumber = 1;
const samples: { flight: number; time: number; x: number; altitude: number; z: number; speed: number; battery: number }[] = [];
let lastSample = -1;
let audio: AudioContext | undefined, oscillator: OscillatorNode | undefined, volume: GainNode | undefined;
let sound = false;
let lastFrame = performance.now(), lastUI = 0, frames = 0, lastFPS = performance.now();
let toastTimer: ReturnType<typeof setTimeout>;
function toast(message: string) { $("toast").textContent = message; $("toast").hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => $("toast").hidden = true, 3500); }
function reset() { flightNumber++; state = initialFlight(); keys.clear(); world?.clearTrail(); lastSample = -1; toast("New flight. The landscape is yours."); refresh(); }
function launch() { if (!world?.ready) { toast("Wait for the 3D scene to finish loading."); return; } if (!state.armed) camera("Chase"); if (state.armed) { state.landing = true; state.returning = false; state.message = "Landing. Hold position for touchdown."; } else takeoff(state); refresh(); }
function land() { if (!state.armed) { toast("Take off first to begin a flight."); return; } state.landing = true; state.returning = false; state.message = "Descending for a gentle landing."; }
function returnHome() { if (!state.armed) { toast("You are already on the ground."); return; } state.returning = true; state.landing = false; state.message = "Returning home. Climbing to a clear transit altitude."; }
function pause() { state.paused = !state.paused; keys.clear(); refresh(); }
function camera(mode: CameraMode) { if (!world) return; world.cameraMode = mode; document.querySelectorAll<HTMLButtonElement>("[data-camera]").forEach(b => b.classList.toggle("active", b.dataset.camera === mode)); $("view-hint").textContent = mode === "Orbit" ? "Drag to orbit · Scroll to zoom" : mode === "FPV" ? "Pilot’s view · C to switch camera" : "Scroll to zoom · C to switch camera"; }
function showDialog(id: string) { keys.clear(); ($(id) as HTMLDialogElement).showModal(); }
$("launch").onclick = launch; $("land").onclick = land; $("return").onclick = returnHome;
$("reset").onclick = reset; $("pause").onclick = pause; $("resume").onclick = pause;
$("help").onclick = $("all-keys").onclick = () => showDialog("help-dialog");
$("settings").onclick = () => showDialog("settings-dialog");
$("nav-log").onclick = () => { updateLog(); showDialog("log-dialog"); };
$("nav-fly").onclick = () => $("flight-view").focus();
for (const b of document.querySelectorAll<HTMLButtonElement>(".close-dialog")) b.onclick = () => b.closest("dialog")?.close();
for (const dialog of document.querySelectorAll("dialog")) dialog.addEventListener("click", e => { if (e.target === dialog) { const r = dialog.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close(); } });
document.querySelectorAll<HTMLButtonElement>("[data-camera]").forEach(b => b.onclick = () => camera(b.dataset.camera as CameraMode));
$("flight-mode").onchange = () => { mode = $<HTMLSelectElement>("flight-mode").value as FlightMode; $("mode-note").textContent = mode === "Sport" ? "More speed, more momentum. Make every turn count." : "Auto-leveling and altitude hold. Find your flow."; };
$("night").onchange = () => { const night = $<HTMLInputElement>("night").checked; world?.setNight(night); $("time-label").textContent = night ? "Blue hour" : "Daylight"; };
$("trail").onchange = () => { if (world) world.trailOn = $<HTMLInputElement>("trail").checked; };
$("wind").oninput = () => { wind = +$<HTMLInputElement>("wind").value; $("wind-value").textContent = `${wind} m/s`; };
$("sound").onchange = async () => {
  sound = $<HTMLInputElement>("sound").checked;
  try {
    if (sound && !audio) { audio = new AudioContext(); oscillator = audio.createOscillator(); volume = audio.createGain(); oscillator.type = "sawtooth"; volume.gain.value = 0; oscillator.connect(volume); volume.connect(audio.destination); oscillator.start(); }
    if (sound) await audio?.resume();
  } catch { sound = false; $<HTMLInputElement>("sound").checked = false; toast("Audio is unavailable in this browser."); }
};
$("screenshot").onclick = () => { world?.screenshot(); toast("Scene screenshot saved."); };
$("fullscreen").onclick = async () => { try { if (document.fullscreenElement) await document.exitFullscreen(); else await $("flight-view").requestFullscreen(); } catch { toast("Fullscreen is unavailable in this browser."); } };
$("record").onclick = () => { recording = !recording; $("record").classList.toggle("recording", recording); $("record-text").textContent = recording ? "REC ●" : "REC"; toast(recording ? "Recording telemetry. Take off to capture samples." : `Recording stopped. ${samples.length} samples in your flight log.`); };
function updateLog() {
  if (!samples.length) return;
  const last = samples[samples.length - 1];
  $("log-content").innerHTML = `<div class="log-stats"><div><b>${samples.length}</b><span>samples recorded</span></div><div><b>${Math.max(...samples.map(s => s.altitude)).toFixed(1)} m</b><span>maximum altitude</span></div></div><p>Latest sample · ${last.time.toFixed(1)} s · ${last.speed.toFixed(1)} m/s</p>`;
  $<HTMLButtonElement>("export").disabled = false;
}
$("export").onclick = () => {
  const csv = "flight,time_s,x_m,altitude_m,z_m,speed_m_s,battery_percent\n" + samples.map(s => Object.values(s).map(v => v.toFixed(3)).join(",")).join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  const a = document.createElement("a"); a.href = url; a.download = "droneverse-flight.csv"; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
};
const flightKeys = new Set(["KeyW", "KeyA", "KeyS", "KeyD", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "KeyQ", "KeyE", "Space", "ShiftLeft", "ShiftRight", "KeyF", "KeyL", "KeyH", "KeyC", "KeyP", "KeyR"]);
window.addEventListener("keydown", e => {
  if (document.querySelector("dialog[open]") || (e.target as HTMLElement).matches("input, select, textarea") || e.ctrlKey || e.metaKey || e.altKey) return;
  if (e.code === "Space" && (e.target as HTMLElement).closest("button")) return;
  if (flightKeys.has(e.code)) e.preventDefault();
  keys.add(e.code);
  if (e.repeat) return;
  switch (e.code) {
    case "KeyF": launch(); break; case "KeyL": land(); break; case "KeyH": returnHome(); break;
    case "KeyP": pause(); break; case "KeyR": reset(); break;
    case "KeyC": { const modes: CameraMode[] = ["Chase", "FPV", "Orbit"]; camera(modes[(modes.indexOf(world?.cameraMode || "Chase") + 1) % 3]); break; }
    case "Slash": if (e.shiftKey) showDialog("help-dialog"); break;
  }
});
window.addEventListener("keyup", e => keys.delete(e.code));
function loseFocus() { keys.clear(); if (state.armed) { state.paused = true; refresh(); } }
window.addEventListener("blur", loseFocus);
document.addEventListener("visibilitychange", () => { if (document.hidden) loseFocus(); });
// Pointer buttons should return keyboard focus to the flight surface.
for (const id of ["launch", "land", "return", "reset", "pause", "resume"]) $(id).addEventListener("click", () => $("flight-view").focus({ preventScroll: true }));
function refresh() {
  const altitude = Math.max(0, state.y - .65), speed = Math.hypot(state.vx, state.vz);
  $("altitude").textContent = $("hud-alt").textContent = altitude.toFixed(1);
  $("speed").textContent = $("hud-speed").textContent = speed.toFixed(1);
  $("battery").textContent = Math.ceil(state.battery).toString(); $("battery-fill").style.width = `${state.battery}%`;
  $("battery-note").textContent = state.battery < 15 ? "Low battery · auto return" : "Healthy · simulated battery";
  $("flight-time").textContent = `${Math.floor(state.elapsed / 60).toString().padStart(2, "0")}:${Math.floor(state.elapsed % 60).toString().padStart(2, "0")}`;
  $("distance").textContent = Math.round(state.distance).toString();
  $("speed-note").textContent = speed < .5 ? "Holding position" : mode === "Sport" ? "Sport flight" : "Cruising steadily";
  $("status-text").textContent = state.message;
  $("aircraft-status").textContent = state.crashed ? "Crashed" : state.paused ? "Paused" : state.armed ? "In flight" : "Ready";
  const launchMarkup = `${icon(state.armed ? "arrow-down-to-line" : "power")} ${state.armed ? "Land aircraft" : "Arm & take off"} <kbd>F</kbd>`;
  if ($("launch").dataset.armed !== String(state.armed)) { $("launch").innerHTML = launchMarkup; $("launch").dataset.armed = String(state.armed); createIcons({ icons, root: $("launch") }); }
  $("pause-overlay").hidden = !state.paused;
  $("pause").setAttribute("aria-label", state.paused ? "Resume simulation" : "Pause simulation");
  const heading = ((-state.yaw * 180 / Math.PI) % 360 + 360) % 360;
  $("heading").textContent = `${heading.toFixed(0).padStart(3, "0")}°`;
  const coordinates = world?.coordinates(state.x, state.z);
  $("map-coords").textContent = coordinates ? `${coordinates[1].toFixed(5)}, ${coordinates[0].toFixed(5)}` : "Loading…";
  $<HTMLButtonElement>("launch").disabled = !world?.ready;
  $("gate-count").textContent = `${state.gates} / 6`; $("gate-progress").style.width = `${state.gates / 6 * 100}%`;
  $("course-label").textContent = state.gates === 6 ? "Course complete!" : `Gate 0${state.gates + 1} of 06`;
  const g = gates[state.gates]; $("gate-distance").textContent = g ? `${Math.round(Math.hypot(g.x - state.x, g.y - state.y, g.z - state.z))} m` : "✓";
}
try {
  world = new FlightWorld($("world"), $("geo-minimap"), (message, ready) => { $("map-status").firstChild!.textContent = message + " "; $("map-status").classList.toggle("map-ready", ready); $("map-status").dataset.ready = String(ready); });
  world.start((now: number) => {
    const dt = Math.min((now - lastFrame) / 1000, .04); lastFrame = now;
    const dialogOpen = !!document.querySelector("dialog[open]");
    if (!dialogOpen && world!.ready) { const previous = { x: state.x, z: state.z }; stepFlight(state, keys, dt, mode, wind); world!.constrainFlight(state, previous); }
    world!.update(state, dt);
    if (volume && audio && oscillator) { volume.gain.setTargetAtTime(sound && state.armed && !state.paused && !dialogOpen ? .018 : 0, audio.currentTime, .1); oscillator.frequency.setTargetAtTime(85 + Math.hypot(state.vx, state.vy, state.vz) * 5, audio.currentTime, .1); }
    if (recording && state.armed && !state.paused && !dialogOpen && state.elapsed - lastSample >= .25) {
      lastSample = state.elapsed; samples.push({ flight: flightNumber, time: state.elapsed, x: state.x, altitude: Math.max(0, state.y - .65), z: state.z, speed: Math.hypot(state.vx, state.vz), battery: state.battery });
      if (samples.length >= 24000) { recording = false; $("record").classList.remove("recording"); $("record-text").textContent = "REC"; toast("Recording full. Export your flight log to keep your data."); }
      $("log-count").textContent = samples.length.toString();
    }
    if (now - lastUI > 100) { refresh(); lastUI = now; }
    frames++;
    if (now - lastFPS > 1000) { $("fps").textContent = Math.round(frames * 1000 / (now - lastFPS)).toString(); frames = 0; lastFPS = now; }
  });
} catch (error) {
  console.error("Unable to initialize flight world", error); $("world-error").hidden = false;
  ["launch", "land", "return", "record", "screenshot"].forEach(id => $<HTMLButtonElement>(id).disabled = true);
}
if (import.meta.hot) import.meta.hot.dispose(() => { world?.dispose(); void audio?.close(); });


$("map-retry").onclick = () => window.location.reload();
$("location").onchange = () => { const location = locations[+$<HTMLSelectElement>("location").value]; reset(); world?.setLocation(location); $("location-name").textContent = location.name; camera("Orbit"); };
