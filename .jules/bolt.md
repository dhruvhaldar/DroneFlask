## 2025-05-24 - Zero-Allocation State Updates
**Learning:** Frequent memory allocation for shared state in high-frequency loops (or event handlers) creates GC pressure. Updating numpy arrays in-place (`arr[:] = new_values`) is significantly faster and more memory efficient than re-allocating (`arr = np.array(new_values)`).
**Action:** Use in-place assignment `[:]` when updating persistent state vectors from external inputs.

## 2025-05-24 - Function Block Return Types
**Learning:** `bdsim` Function blocks can return values directly. Wrapping single outputs in a list (e.g., `return [out]`) adds unnecessary allocation overhead in the simulation loop.
**Action:** Return numpy arrays directly from Function blocks when `nout=1` to avoid list overhead.
