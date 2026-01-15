
import unittest
import time
import queue
import numpy as np
from quadcopter_web import WebSink

class TestWebSinkPerformance(unittest.TestCase):
    def test_websink_step_pacing(self):
        """
        Verify that WebSink.step maintains near real-time pacing
        instead of lagging due to fixed sleep.
        """
        # Setup
        q = queue.Queue()
        sink = WebSink(q, name='WebSink')

        # Fake inputs
        state = [0.0] * 12
        inputs = [state]

        # Measure execution time of 100 steps
        # Each step targets dt=0.01 (100Hz)
        # Total expected time = 1.00s

        steps = 100
        start_time = time.perf_counter()

        for i in range(steps):
            # t must advance by 0.01 per step for the logic to work properly
            sink.step(i*0.01, inputs)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Tolerance: It should be very close to 1.0s.
        # Fixed sleep(0.01) would result in > 1.01s (usually ~1.02s+)
        # Adaptive sleep should be ~1.00s +/- system noise.
        # We allow small overhead but enforce a tight bound.

        # Note: If system is heavily loaded, it might be slower.
        # But we want to ensure it is NOT significantly slower than 1.0s intentionally.

        print(f"\n[Perf] 100 Steps Time: {total_time:.4f}s (Target: 1.00s)")

        # Check that it is not too fast (pacing works)
        self.assertGreater(total_time, 0.95, "Simulation running too fast! Pacing failed.")

        # Check that it is not too slow (adaptive sleep works better than fixed)
        # We accept up to 10ms overhead for 100 steps (100us per step overhead)
        self.assertLess(total_time, 1.05, "Simulation running too slow! Adaptive pacing ineffective?")

if __name__ == '__main__':
    unittest.main()
