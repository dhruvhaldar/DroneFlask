import time
import numpy as np
import quadcopter_bdsim
from quadcopter_bdsim import flight_controller

def benchmark():
    # Setup
    state = np.zeros(12)
    # Give it some state so it's not all zeros (though zeros are fine for performance test)
    state[2] = 4.0 # z
    state[5] = -0.5 # vz

    iterations = 100_000

    start = time.perf_counter()
    for _ in range(iterations):
        # Time input varies to trigger different maneuvers
        flight_controller(state, 3.0)
    end = time.perf_counter()

    avg_time = (end - start) / iterations * 1e6 # microseconds
    print(f"Average time per call: {avg_time:.4f} us")
    print(f"Total time for {iterations} calls: {end - start:.4f} s")

if __name__ == "__main__":
    benchmark()
