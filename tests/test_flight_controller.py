
import unittest
import numpy as np
from quadcopter_web import flight_controller_interactive

class TestFlightController(unittest.TestCase):
    def test_flight_controller_output(self):
        # cmd: [Thrust, Roll, Pitch, Yaw]
        cmd = np.array([0.5, 0.0, 0.0, 0.0])
        # state: 12 zeros
        state = np.zeros(12)

        # Run function
        output = flight_controller_interactive(cmd, state)

        # Verify output structure
        self.assertIsInstance(output, np.ndarray)
        self.assertEqual(len(output), 16)

        # Check first 4 elements are motor speeds (or squares)
        # 0.5 thrust should give some positive motor outputs
        self.assertTrue(np.all(output[0:4] >= 0))

        # Check remaining 12 elements are state (zeros)
        self.assertTrue(np.array_equal(output[4:], state))

    def test_flight_controller_maneuver(self):
        # Test a roll command
        cmd = np.array([0.5, 0.1, 0.0, 0.0])
        state = np.zeros(12)

        output = flight_controller_interactive(cmd, state)

        w_sq = output[0:4]
        # Roll right (positive phi ref) -> higher speed on one side?
        # Logic: tau_phi = kp * (ref - phi)
        # tau_phi > 0.
        # w4_sq - w2_sq > 0 => w4 > w2
        # w1, w2, w3, w4

        w2_sq = w_sq[1]
        w4_sq = w_sq[3]

        self.assertGreater(w4_sq, w2_sq)

if __name__ == '__main__':
    unittest.main()
