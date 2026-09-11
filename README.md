# Droneverse

A standalone Three.js drone flight simulator. No backend, Next.js, deployment service, account, or API keys. All scenery, aircraft, and audio are generated locally; fonts are bundled.

## Run

Use Node.js 22.18+ (or Node.js 24) and pnpm.

```sh
pnpm install
pnpm dev
```

Open the local URL printed by Vite, normally http://127.0.0.1:5173. A desktop browser with WebGL 2 and a keyboard is recommended.

```sh
pnpm test       # Flight dynamics and safety behavior
pnpm typecheck  # TypeScript validation
pnpm build     # Produce a static app in dist/
pnpm preview   # Serve the production build locally
```

## Fly

Click **Arm & take off** or press **F**. The aircraft rises into a stable hover. Hold **Space** to climb, then fly through each orange gate in order.

| Key | Action |
| --- | --- |
| F | Arm / take off; request landing while flying |
| W A S D or arrow keys | Forward, left, back, right relative to heading |
| Space / Shift | Ascend / descend |
| Q / E | Yaw left / right |
| L | Land at the current position |
| H | Climb, return home, and land |
| C | Cycle Chase, FPV, and Orbit cameras |
| P | Pause / resume |
| R | Reset flight and battery |
| ? | Keyboard guide |

Chase supports scroll-to-zoom. Orbit supports dragging and scroll-to-zoom. Opening a dialog suspends physics; switching away from the app pauses active flight and clears held keys.

## Features

- Procedural 3D quadcopter with animated propellers, camera, landing gear, and navigation lights.
- Alpine airfield with mountains, instanced trees, runway, buildings, shadows, and six training gates.
- Stabilized and Sport flight modes with momentum, braking, altitude hold, and heading-relative movement.
- Building and hard-landing collisions; automatic return on low battery; bounded flight area and altitude ceiling.
- Chase, FPV, and mouse-controlled Orbit cameras; screenshot downloads and fullscreen.
- Live altitude, speed, battery, flight time, distance, compass, and local minimap.
- Toggleable flight trail, daylight / blue-hour lighting, wind strength, and synthesized motor audio.
- Telemetry recording at four samples per second with CSV export. Flight logs are held in memory and cleared on reload. Recording stops at 24,000 samples.
- Responsive interface, keyboard shortcuts, accessible dialogs, reduced-motion UI support, and WebGL failure message.

## Implementation

- `src/main.ts`: UI, input handling, telemetry recording, audio, animation orchestration.
- `src/world.ts`: Three.js renderer, procedural scene, drone, camera, and resource cleanup.
- `src/flight.ts`: Deterministic simulation state and flight dynamics, independent of rendering.
- `src/style.css`: Responsive cockpit interface.
- `tests/flight.test.ts`: Takeoff, braking, pause, landing, collisions, gate scoring, return home, limits, and battery tests.

The flight model is recreational and uses simplified velocity-based dynamics, not a calibrated aerospace model. Battery, coordinates, wind, and navigation are simulated. Buildings and the ground participate in collisions; trees, mountains, and gate frames are decorative. This project does not connect to or control physical drones.

## Browser smoke test

Start `pnpm dev` in another terminal, then run:

```sh
pnpm exec playwright install chromium
pnpm test:browser
```

Alternatively, set `BROWSER_CHANNEL=msedge` to use an installed Microsoft Edge. Set `DRONEVERSE_URL` to test another local URL or the production preview. The test checks rendering, keyboard flight, cameras, pause, environment settings, telemetry export, landing, screenshot download, and mobile overflow. Screenshots are written to the ignored `tests/artifacts/` directory.
