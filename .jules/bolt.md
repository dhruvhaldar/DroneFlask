## 2025-05-24 - Zero-Allocation State Updates
**Learning:** Frequent memory allocation for shared state in high-frequency loops (or event handlers) creates GC pressure. Updating numpy arrays in-place (`arr[:] = new_values`) is significantly faster and more memory efficient than re-allocating (`arr = np.array(new_values)`).
**Action:** Use in-place assignment `[:]` when updating persistent state vectors from external inputs.

## 2025-05-24 - Function Block Return Types
**Learning:** `bdsim` Function blocks can return values directly. Wrapping single outputs in a list (e.g., `return [out]`) adds unnecessary allocation overhead in the simulation loop.
**Action:** Return numpy arrays directly from Function blocks when `nout=1` to avoid list overhead.

## 2025-05-24 - Individual Assignment vs List Slice
**Learning:** When updating a small fixed-size numpy array (e.g., control vector), individual element assignment (`arr[0]=x; arr[1]=y...`) is ~2.4x faster than list slice assignment (`arr[:] = [x, y...]`) because it avoids creating a temporary list object.
**Action:** Prefer individual index assignment for small, high-frequency array updates.
