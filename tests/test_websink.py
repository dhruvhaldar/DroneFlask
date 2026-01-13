
import unittest
import numpy as np
import queue
from quadcopter_web import WebSink

class TestWebSinkOptimization(unittest.TestCase):
    def test_step_with_numpy(self):
        q = queue.Queue(maxsize=1)
        sink = WebSink(q)

        # Test with numpy array
        state_np = np.zeros(12)

        # Need to call step 3 times to trigger queue put
        sink.step(0, [state_np])
        sink.step(0, [state_np])
        sink.step(0, [state_np])

        self.assertFalse(q.empty())
        data = q.get()
        self.assertIsInstance(data, list)
        # Optimized: Expect 6 elements (Pos + Angles)
        self.assertEqual(len(data), 6)
        self.assertEqual(data[0], 0.0)

    def test_step_with_list(self):
        q = queue.Queue(maxsize=1)
        sink = WebSink(q)

        # Test with list
        state_list = [1.0] * 12

        sink.step(0, [state_list])
        sink.step(0, [state_list])
        sink.step(0, [state_list])

        self.assertFalse(q.empty())
        data = q.get()
        self.assertIsInstance(data, list)
        # Optimized: Expect 6 elements (Pos + Angles)
        self.assertEqual(len(data), 6)
        self.assertEqual(data[0], 1.0)

    def test_step_queue_full(self):
        q = queue.Queue(maxsize=1)
        sink = WebSink(q)
        state_np = np.zeros(12)

        # Fill manually
        q.put([9.9]*12)

        # Step should replace it
        sink.step(0, [state_np])
        sink.step(0, [state_np])
        sink.step(0, [state_np])

        self.assertFalse(q.empty())
        data = q.get()
        self.assertEqual(data[0], 0.0) # Should be new data

if __name__ == '__main__':
    unittest.main()
