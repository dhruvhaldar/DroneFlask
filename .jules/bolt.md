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

## 2025-05-23 - Array Construction
**Learning:** `np.concatenate` involves multiple allocations and is ~2x slower than `np.empty` + assignment for small arrays in high-frequency loops.
**Action:** Use pre-allocation (`np.empty`) and indexed assignment for constructing state vectors in simulation steps.

## 2025-05-23 - Trig Reuse
**Learning:** In 6DOF physics loops, trig functions (`sin`, `cos`, `tan`) of the same angles are often called multiple times. Calculating `tan(theta)` as `stheta/ctheta` (if `cos` and `sin` are already computed) is ~14% faster and numerically sufficient for control loops.
**Action:** Reuse pre-calculated sine/cosine values for derived trig functions in inner physics loops.

## 2025-05-23 - Vector Unpacking
**Learning:** Unpacking small numpy arrays (e.g. 12 elements) into scalar variables is ~4x slower than converting to a list first (`.tolist()`) and then unpacking.
**Action:** Always use `.tolist()` before unpacking or accessing multiple elements from small numpy arrays in high-frequency loops.

## 2025-05-24 - Block Diagram Overhead
**Learning:** In pure Python block diagram simulations (like `bdsim`), each block adds scheduling and function call overhead. Redundant pass-through blocks (e.g. for signal shaping) can noticeably impact performance in high-frequency loops.
**Action:** Remove redundant blocks and wire functions directly where possible; implement signal shaping within the source/dest blocks if cheap.
