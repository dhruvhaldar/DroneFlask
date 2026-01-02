
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class Quadcopter:
    def __init__(self):
        # Physical parameters
        self.m = 1.0  # Mass in kg
        self.g = 9.81
        
        # Moments of inertia (approximate)
        self.Ixx = 0.01
        self.Iyy = 0.01
        self.Izz = 0.02
        
        self.Ix = np.array([[self.Ixx, 0, 0],
                            [0, self.Iyy, 0],
                            [0, 0, self.Izz]])
        self.inv_Ix = np.linalg.inv(self.Ix)
        
        # Controller gains (PID) - Tuned for simple hover stability
        # Altitude (z)
        self.kp_z = 10.0
        self.kd_z = 5.0
        self.ki_z = 2.0
        
        # Roll (phi)
        self.kp_phi = 5.0
        self.kd_phi = 1.0
        
        # Pitch (theta)
        self.kp_theta = 5.0
        self.kd_theta = 1.0
        
        # Yaw (psi)
        self.kp_psi = 2.0
        self.kd_psi = 0.5

        # Integral error states
        self.int_err_z = 0.0

    def dynamics(self, t, state, u):
        """
        State vector: [x, y, z, vx, vy, vz, phi, theta, psi, p, q, r]
        Inputs u: [F_total, tau_phi, tau_theta, tau_psi]
        Coordinate frame: ENU (East-North-Up), Z is up.
        """
        x, y, z, vx, vy, vz, phi, theta, psi, p, q, r = state
        F_total, tau_phi, tau_theta, tau_psi = u
        
        # Rotation matrix from Body to Inertial frame
        # R = Rz(psi) * Ry(theta) * Rx(phi)
        cpsi, spsi = np.cos(psi), np.sin(psi)
        ctheta, stheta = np.cos(theta), np.sin(theta)
        cphi, sphi = np.cos(phi), np.sin(phi)
        
        R = np.array([
            [cpsi*ctheta, cpsi*stheta*sphi - spsi*cphi, cpsi*stheta*cphi + spsi*sphi],
            [spsi*ctheta, spsi*stheta*sphi + cpsi*cphi, spsi*stheta*cphi - cpsi*sphi],
            [-stheta,     ctheta*sphi,                  ctheta*cphi]
        ])
        
        # Transformation from body rates (p, q, r) to Euler rates (phi_dot, theta_dot, psi_dot)
        # Note: Singularity at theta = +/- 90 degrees
        W = np.array([
            [1, sphi*stheta/ctheta, cphi*stheta/ctheta],
            [0, cphi,               -sphi],
            [0, sphi/ctheta,        cphi/ctheta]
        ])
        
        # --- Translational Dynamics ---
        # F_inertial = R * F_body - [0, 0, m*g]
        # In body frame, thrust is typically aligned with Z axis (upwards relative to prop plane)
        # F_body = [0, 0, F_total]
        
        thrust_body = np.array([0, 0, F_total])
        gravity = np.array([0, 0, -self.m * self.g])
        
        accel = (np.dot(R, thrust_body) + gravity) / self.m
        
        # --- Rotational Dynamics ---
        # I * omega_dot + omega x (I * omega) = Torques
        omega = np.array([p, q, r])
        torques = np.array([tau_phi, tau_theta, tau_psi])
        
        omega_dot = np.dot(self.inv_Ix, torques - np.cross(omega, np.dot(self.Ix, omega)))
        
        # State derivatives
        pos_dot = np.array([vx, vy, vz])
        euler_dot = np.dot(W, omega)
        
        d_state = np.concatenate((pos_dot, accel, euler_dot, omega_dot))
        return d_state

    def controller(self, state, target_state, dt):
        """
        Simple PID controller for stabilization.
        Target: [x_t, y_t, z_t, yaw_t] (assuming hover at location)
        """
        x, y, z, vx, vy, vz, phi, theta, psi, p, q, r = state
        x_t, y_t, z_t, psi_t = target_state
        
        # Altitude control (PID)
        err_z = z_t - z
        d_err_z = 0 - vz # Target velocity is 0
        self.int_err_z += err_z * dt
        
        # Feedforward gravity compensation + PID
        u_thrust = self.m * self.g + (self.kp_z * err_z + self.kd_z * d_err_z + self.ki_z * self.int_err_z)
        
        # Simplified horizontal position control (P controller for desired angles)
        # Small angle approximation for acceleration: x_acc ~ g * theta, y_acc ~ -g * phi
        # Desired accelerations
        ax_des = 1.0 * (x_t - x) - 2.0 * vx
        ay_des = 1.0 * (y_t - y) - 2.0 * vy
        
        # Desired roll/pitch to achieve accel (inverted for drag/thrust model approx)
        # For small angles: ax = g*(theta*cos(psi) + phi*sin(psi))
        #                   ay = g*(theta*sin(psi) - phi*cos(psi))
        # Simplified mapping (assuming psi~0 for now):
        phi_des = -ay_des / self.g
        theta_des = ax_des / self.g
        
        # Clamp desired angles for stability
        max_angle = np.radians(20)
        phi_des = np.clip(phi_des, -max_angle, max_angle)
        theta_des = np.clip(theta_des, -max_angle, max_angle)
        
        # Attitude control (PD)
        u_phi = self.kp_phi * (phi_des - phi) + self.kd_phi * (0 - p)
        u_theta = self.kp_theta * (theta_des - theta) + self.kd_theta * (0 - q)
        u_psi = self.kp_psi * (psi_t - psi) + self.kd_psi * (0 - r)
        
        return [u_thrust, u_phi, u_theta, u_psi]

def run_simulation():
    quad = Quadcopter()
    
    # Initial State
    # [x, y, z, vx, vy, vz, phi, theta, psi, p, q, r]
    state = np.zeros(12)
    state[0] = 0.0 # x
    state[1] = 0.0 # y
    state[2] = 0.0 # z (ground)
    
    # Target State (Hover at 5m, at x=2, y=2)
    target = [2.0, 2.0, 5.0, 0.0] 
    
    # Simulation Parameters
    dt = 0.01
    t_end = 10.0
    steps = int(t_end / dt)
    time = np.linspace(0, t_end, steps)
    
    # History for plotting
    history = np.zeros((steps, 12))
    controls = np.zeros((steps, 4))
    
    for i in range(steps):
        t = time[i]
        
        # Get control inputs
        u = quad.controller(state, target, dt)
        controls[i] = u
        
        # Update dynamics (Euler integration for simplicity here, solve_ivp better for precision)
        # k1 = quad.dynamics(t, state, u)
        # state = state + k1 * dt
        
        # Using RK4 for better stability
        k1 = quad.dynamics(t, state, u)
        k2 = quad.dynamics(t + dt/2, state + k1 * dt/2, u)
        k3 = quad.dynamics(t + dt/2, state + k2 * dt/2, u)
        k4 = quad.dynamics(t + dt, state + k3 * dt, u)
        
        state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Simple ground constraint
        if state[2] < 0:
            state[2] = 0
            state[5] = 0 # zero z velocity
            
        history[i] = state
        
    # Plotting
    plt.figure(figsize=(12, 10))
    
    plt.subplot(3, 1, 1)
    plt.plot(time, history[:, 0], label='x')
    plt.plot(time, history[:, 1], label='y')
    plt.plot(time, history[:, 2], label='z')
    plt.axhline(target[0], color='r', linestyle='--', alpha=0.3)
    plt.axhline(target[1], color='g', linestyle='--', alpha=0.3)
    plt.axhline(target[2], color='b', linestyle='--', alpha=0.3)
    plt.legend()
    plt.title('Position')
    plt.grid()
    
    plt.subplot(3, 1, 2)
    plt.plot(time, np.degrees(history[:, 6]), label='phi (roll)')
    plt.plot(time, np.degrees(history[:, 7]), label='theta (pitch)')
    plt.plot(time, np.degrees(history[:, 8]), label='psi (yaw)')
    plt.legend()
    plt.title('Attitude (Degrees)')
    plt.grid()
    
    plt.subplot(3, 1, 3)
    plt.plot(time, controls[:, 0], label='Thrust')
    plt.legend()
    plt.title('Control Thrust')
    plt.xlabel('Time (s)')
    plt.grid()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_simulation()
