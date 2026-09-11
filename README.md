# Droneverse

A standalone Three.js drone simulator with **textured real-world 3D capture**. The default scene streams photogrammetry of the AGI headquarters campus in Exton, Pennsylvania: buildings, roads, parking lots, and vegetation have real 3D geometry and photographic textures. MapLibre supplies the geographic view and live minimap.

## Run

Use Node.js 22.18+ or Node.js 24, and pnpm:

```sh
pnpm install
pnpm dev
```

Open the URL printed by Vite (normally http://127.0.0.1:5173). Use a desktop browser with WebGL 2, hardware acceleration, and a keyboard. An internet connection is required for maps and 3D tiles. No API key or backend is required for the included sources.

## Scenery

- **Exton campus · 3D capture** is the default. This is a public, limited-area photogrammetry sample used by MapLibre's official 3D Tiles example. It is not worldwide Street View or Google's Photorealistic 3D Tiles. Geometry and texture detail refine as tiles stream; initial loading can take tens of seconds.
- **Swiss Alps, Yosemite, and Manali** are alternate topographic views: OpenStreetMap-derived OpenFreeMap vector maps over real Mapzen/AWS elevation tiles. These do not have the campus's photographic building textures.
- Choose a location under **Environment**. Changing locations resets the flight. Map and capture attribution remain visible in the viewport; see [THIRD_PARTY.md](THIRD_PARTY.md).
- **Orbit** begins with an overview. Drag to rotate/pitch and scroll to zoom. Takeoff automatically selects **Chase**; **FPV** provides the drone's forward view.

## Fly

Click **Arm & take off** or press **F**. Hold **Space** to climb, then use the keyboard to fly through the virtual training gates.

| Key | Action |
| --- | --- |
| F | Arm / take off; request landing while flying |
| W A S D or arrow keys | Forward, left, back, right relative to heading |
| Space / Shift | Ascend / descend |
| Q / E | Rotate left / right |
| L | Land |
| H | Return home and land |
| C | Cycle Chase, FPV, and Orbit |
| P | Pause / resume |
| R | Reset flight and battery |
| ? | Keyboard guide |

Stabilized and Sport modes provide different speed, momentum, and braking. Telemetry shows altitude, speed, battery, elapsed time, and distance. Other controls include lighting, wind, synthesized motor audio, flight trails, fullscreen, screenshots, and telemetry recording with CSV export. Logs stay in memory until reload and hold at most 24,000 samples.

## Simulation limits

This is a recreational **surface-following** flight model. Altitude is relative to the sampled 3D surface, including roofs in the capture, or local terrain in topographic mode. It is not a calibrated aircraft or obstacle-avoidance model. Capture boundaries and unloaded surface areas stop horizontal motion; hard landings stop the aircraft. Sideways building collisions are not modeled. Training gates are simulated overlays, not geographic features. No physical drone is connected.

The 3D capture is finite and reflects the date and quality of its source photographs. The imagery is streamed from third-party services, whose availability is outside this app. For arbitrary cities with consistently photorealistic coverage, a licensed imagery/3D Tiles provider and its credentials would be needed.

## Verify

```sh
pnpm test
pnpm typecheck
pnpm build
pnpm preview
```

For browser checks, start the development server separately, then:

```sh
pnpm exec playwright install chromium
pnpm test:browser
```

Set `BROWSER_CHANNEL=msedge` to use installed Microsoft Edge. Set `DRONEVERSE_URL` to test the production preview or another URL. The browser test waits for the capture, checks flight controls, cameras, recording, exports, landing, screenshots, and mobile overflow. Test screenshots go to ignored `tests/artifacts/`.

## Code

- `src/main.ts`: cockpit UI, input, telemetry, audio, and animation loop.
- `src/world.ts`: MapLibre map, georeferenced Three.js drone/gates, cameras, surface following, and cleanup.
- `src/reality.ts`: streamed 3D capture, ECEF-to-local transforms, mesh surface sampling, and bounded tile cache.
- `src/geography.ts`: geographic locations, map/elevation sources, and local coordinate conversion.
- `src/flight.ts`: deterministic flight dynamics.
- `public/draco/`: locally served geometry decoder.
- `tests/*.test.ts`: flight dynamics and geographic transform tests.
