## 2025-02-18 - 3D Interaction Hints
**Learning:** Users often miss that they can interact with 3D scenes (drag/scroll) when controls are not explicitly visible.
**Action:** Added a "fade-out" interaction hint that appears on load and vanishes upon first interaction. This improves discoverability without cluttering the UI permanently. Using `window` capture phase is essential to catch interactions that might be consumed by libraries like Three.js OrbitControls.
