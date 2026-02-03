
import unittest
import numpy as np
import quadcopter_bdsim

class TestBDSimIntegration(unittest.TestCase):

    def test_rigid_body_dynamics_numpy_input(self):
        """Test rigid_body_dynamics with flat numpy array (standard case)"""
        w = 100.0
        w_sq = w**2
        input_vec = np.zeros(16)
        input_vec[0:4] = w_sq

        result = quadcopter_bdsim.rigid_body_dynamics(input_vec)

        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (12,))

        w_high = 600.0
        input_vec[0:4] = w_high**2
        result = quadcopter_bdsim.rigid_body_dynamics(input_vec)
        self.assertGreater(result[5], 0.0)

    def test_rigid_body_dynamics_numpy_2d_input(self):
        """Test rigid_body_dynamics with 2D numpy array (column vector)"""
        w = 600.0
        input_vec = np.zeros((16, 1))
        input_vec[0:4, 0] = w**2

        result = quadcopter_bdsim.rigid_body_dynamics(input_vec)
        self.assertIsInstance(result, np.ndarray)
        self.assertGreater(result[5], 0.0)

    def test_rigid_body_dynamics_list_input(self):
        """Test rigid_body_dynamics with flat list (legacy case)"""
        w_high = 600.0
        input_list = [0.0] * 16
        for i in range(4):
            input_list[i] = w_high**2

        result = quadcopter_bdsim.rigid_body_dynamics(input_list)
        self.assertIsInstance(result, np.ndarray)
        self.assertGreater(result[5], 0.0)

if __name__ == '__main__':
    unittest.main()
