# Bolt's Journal

## 2024-05-22 - Initial Setup
**Learning:** Performance optimization requires measuring both IO and Network bottlenecks.
**Action:** Always check for high-frequency loops (like physics steps) containing blocking IO (print) or network calls.

## 2024-05-22 - Adaptive Pacing
**Learning:** Fixed `time.sleep(dt)` in a simulation loop guarantees drift (slower than real-time) because it adds sleep *on top* of execution time.
**Action:** Use adaptive pacing: calculate `target_time = start + elapsed_sim_time` and sleep `target_time - now`. Use `time.sleep(0)` if lagging to yield without delay.

## 2025-05-23 - Interface Optimization
**Learning:** Passing pre-computed values (like squared speed) between physics blocks avoids redundant inverse operations (sqrt/sq) in high-frequency loops.
**Action:** When connecting Physics/Controller blocks, verify if the signal definition can be simplified (e.g. Force proportional to w^2) to save ops.

## 2025-05-24 - Precomputed Physics Constants
**Learning:** Physics functions in `bdsim` run in a tight Python loop. Repeated divisions and constant arithmetic (e.g. `(Ixx - Iyy)/Izz`) add up.
**Action:** Precompute inverse mass/inertia and coefficient terms at module level. Replace division with multiplication where possible.
