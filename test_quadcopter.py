import unittest
import numpy as np
import quadcopter_bdsim
from profiling_test import calculate_thrust, calculate_torque

class TestQuadcopter(unittest.TestCase):
    
    def test_thrust_calculation(self):
        """Test if thrust calculation follows the square law"""
        w = 100.0
        expected = 8.875e-6 * (100.0**2)
        self.assertAlmostEqual(calculate_thrust(w), expected)
        
    def test_torque_calculation(self):
        """Test if torque calculation follows the square law"""
        w = 100.0
        expected = 1.203e-7 * (100.0**2)
        self.assertAlmostEqual(calculate_torque(w), expected)
        
    def test_dynamics_hover(self):
        """Test if dynamics return approx zero acceleration at hover speed"""
        # Calculate hover speed for 1kg mass
        # F = mg = 9.81
        # 4 * kF * w^2 = 9.81
        # w^2 = 9.81 / (4 * 8.875e-6)
        w_sq = 9.81 / (4 * 8.875e-6)
        w = np.sqrt(w_sq)
        
        state = np.zeros(12)
        u = [w, w, w, w]
        
        d_state = quadcopter_bdsim.quadcopter_dynamics(0, state, u)
        
        # Check z-acceleration (index 5)
        z_acc = d_state[5]
        
        # Should be very close to 0 (gravity cancelled by thrust)
        self.assertAlmostEqual(z_acc, 0.0, places=2)
        
    def test_dynamics_climb(self):
        """Test positive vertical acceleration when thrust > gravity"""
        w = 600.0 # High speed
        state = np.zeros(12)
        u = [w, w, w, w]
        d_state = quadcopter_bdsim.quadcopter_dynamics(0, state, u)
        
        # Expect positive z acceleration
        self.assertGreater(d_state[5], 0.0)
        
    def test_yaw_dynamics(self):
        """Test yaw moment generation"""
        # Increase CW motors (2, 4) -> Should create Positive or Negative Yaw depending on convention
        # In script: tau_psi = (tau_2 + tau_4) - (tau_1 + tau_3)
        # So increasing 2,4 should give positive tau_psi -> positive r_dot
        
        state = np.zeros(12)
        w_base = 300.0
        u = [w_base, w_base+50, w_base, w_base+50] # Imbalance
        
        d_state = quadcopter_bdsim.quadcopter_dynamics(0, state, u)
        r_dot = d_state[11] # Last element
        
        self.assertGreater(r_dot, 0.0)

if __name__ == '__main__':
    unittest.main()
