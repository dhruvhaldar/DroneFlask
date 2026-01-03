import bdsim
import numpy as np
import math

# Coefficients
kF = 8.875e-6
kM = 1.203e-7
MASS = 1.0
GRAVITY = 9.81
L = 0.25 
Ixx = 0.01
Iyy = 0.01
Izz = 0.02
J = np.array([[Ixx, 0, 0], [0, Iyy, 0], [0, 0, Izz]])
J_inv = np.linalg.inv(J)

def quadcopter_dynamics(t, state, u):
    x, y, z, vx, vy, vz, phi, theta, psi, p, q, r = state
    w1, w2, w3, w4 = u
    
    # Square only once
    w1_sq, w2_sq, w3_sq, w4_sq = w1*w1, w2*w2, w3*w3, w4*w4

    # Thrusts
    T1 = kF * w1_sq
    T2 = kF * w2_sq
    T3 = kF * w3_sq
    T4 = kF * w4_sq

    F_total = T1 + T2 + T3 + T4

    # Torques
    tau_1 = kM * w1_sq
    tau_2 = kM * w2_sq
    tau_3 = kM * w3_sq
    tau_4 = kM * w4_sq

    tau_phi = L * (T4 - T2)
    tau_theta = L * (T3 - T1)
    tau_psi = (tau_2 + tau_4) - (tau_1 + tau_3)
    
    # Trigonometry
    cpsi, spsi = np.cos(psi), np.sin(psi)
    ctheta, stheta = np.cos(theta), np.sin(theta)
    cphi, sphi = np.cos(phi), np.sin(phi)
    
    # Acceleration
    # We only need the third column of R multiplied by F_total
    R31 = cpsi*stheta*cphi + spsi*sphi
    R32 = spsi*stheta*cphi - cpsi*sphi
    R33 = ctheta*cphi
    
    accel_x = (F_total * R31) / MASS
    accel_y = (F_total * R32) / MASS
    accel_z = (F_total * R33 - MASS * GRAVITY) / MASS
    
    if z <= 0.0 and F_total < MASS*GRAVITY and vz < 0:
        accel_x = 0.0
        accel_y = 0.0
        accel_z = 0.0
        vz = 0.0
        z = 0.0
    
    # Omega dot (angular acceleration)
    # Using J_inv diagonal components directly for efficiency
    p_dot = (tau_phi - q*r*(Izz - Iyy)) * J_inv[0,0]
    q_dot = (tau_theta - p*r*(Ixx - Izz)) * J_inv[1,1]
    r_dot = (tau_psi - p*q*(Iyy - Ixx)) * J_inv[2,2]
    
    # Euler rates
    ttheta = np.tan(theta)
    ctheta_val = np.cos(theta)

    q_sphi_plus_r_cphi = q*sphi + r*cphi

    phi_dot = p + q_sphi_plus_r_cphi * ttheta
    theta_dot = q*cphi - r*sphi
    
    if abs(ctheta_val) > 1e-3:
        ctheta_inv = 1.0 / ctheta_val
    else:
        ctheta_inv = 0.0

    psi_dot = q_sphi_plus_r_cphi * ctheta_inv

    return np.array([vx, vy, vz, accel_x, accel_y, accel_z, phi_dot, theta_dot, psi_dot, p_dot, q_dot, r_dot])


# --- Complex Block Definitions ---

def flight_controller(state_input, time_input=0):
    """
    Block 1: Flight Controller
    Input 1: State Vector (12)
    Input 2: Time (Scalar)
    Output: Motor Voltages (4) + State (12) = (16)
    """
    if isinstance(state_input, (list, tuple)): state = np.array(state_input).flatten()
    else: state = state_input
    
    # Maneuver Logic based on Time
    t = float(time_input)
    
    # Desired States (Regulation)
    z_des = 5.0
    phi_des = 0.0
    theta_des = 0.0
    psi_rate_des = 0.0
    
    # Sequence
    if t < 2.0:
        # Hover / Climb
        pass
    elif t < 4.0:
        # Roll Maneuver
        phi_des = 0.1 # ~5.7 deg
    elif t < 6.0:
        # Pitch Maneuver
        theta_des = 0.1 
    elif t < 8.0:
        # Yaw Maneuver
        psi_rate_des = 0.5 # rad/s
    else:
        # Back to Hover
        pass
        
    # Extract Current State
    z = state[2]
    vz = state[5]
    phi = state[6]
    theta = state[7]
    p = state[9]
    q = state[10]
    r = state[11]
    
    # --- Controller Gains ---
    # Altitude (Z)
    kp_z = 20.0
    kd_z = 10.0
    
    # Roll (Phi)
    kp_phi = 5.0
    kd_phi = 1.0 # Damping
    
    # Pitch (Theta)
    kp_theta = 5.0
    kd_theta = 1.0
    
    # Yaw (Psi Rate)
    kp_r = 2.0
    
    # --- Control Laws ---
    # Hover Thrust (Gravity Compensation)
    hover_thrust = MASS * GRAVITY
    
    # Altitude PID
    u_z = kp_z * (z_des - z) - kd_z * vz
    F_total = hover_thrust + u_z
    
    # Attitude PD
    tau_phi = kp_phi * (phi_des - phi) - kd_phi * p
    tau_theta = kp_theta * (theta_des - theta) - kd_theta * q
    tau_psi = kp_r * (psi_rate_des - r) # Rate control for Yaw
    
    # --- Mixer (X-Config) ---
    # F = kF * sum(w_i^2)
    # tau_phi = L * kF * (w4^2 - w2^2)
    # tau_theta = L * kF * (w3^2 - w1^2)
    # tau_psi = kM * (w2^2 + w4^2 - w1^2 - w3^2)
    
    # Solving for squared speeds (w_sq):
    # A * w_sq = [F, t_phi, t_theta, t_psi]
    # This matrix inverse is standard.
    # w1^2 = F/4 - t_theta/(2*L*kF) - t_psi/(4*kM) ??
    # Let's derive or use standard inversion:
    # 
    # w1^2 = 1/(4kF) * F - 1/(2LkF)*tau_theta - 1/(4kM)*tau_psi
    # w2^2 = 1/(4kF) * F - 1/(2LkF)*tau_phi   + 1/(4kM)*tau_psi
    # w3^2 = 1/(4kF) * F + 1/(2LkF)*tau_theta - 1/(4kM)*tau_psi
    # w4^2 = 1/(4kF) * F + 1/(2LkF)*tau_phi   + 1/(4kM)*tau_psi
    
    term_F = F_total / (4*kF)
    term_phi = tau_phi / (2*L*kF)
    term_theta = tau_theta / (2*L*kF)
    term_psi = tau_psi / (4*kM)
    
    w1_sq = term_F - term_theta - term_psi
    w2_sq = term_F - term_phi   + term_psi
    w3_sq = term_F + term_theta - term_psi
    w4_sq = term_F + term_phi   + term_psi
    
    # Safety Clamp
    epsilon = 0.0
    w1 = math.sqrt(max(epsilon, w1_sq))
    w2 = math.sqrt(max(epsilon, w2_sq))
    w3 = math.sqrt(max(epsilon, w3_sq))
    w4 = math.sqrt(max(epsilon, w4_sq))
    
    u = np.array([w1, w2, w3, w4])
    
    # Passthrough State
    return np.concatenate((u, state))

def power_system(ctrl_vec):
    if isinstance(ctrl_vec, (list, tuple)): ctrl_vec = np.array(ctrl_vec).flatten()
    u = ctrl_vec[0:4]
    state = ctrl_vec[4:]
    return np.concatenate((u, state))

def rigid_body_dynamics(input_vec):
    if isinstance(input_vec, (list, tuple)): input_vec = np.array(input_vec).flatten()
    w = input_vec[0:4]
    state = input_vec[4:]
    return quadcopter_dynamics(0, state, w)

def run_simulation(pixel_plot=False):
    sim = bdsim.BDSim()
    bd = sim.blockdiagram()
    
    # 1. Integrator (State)
    integrator = bd.INTEGRATOR(x0=np.zeros(12), name='Integrator')
    
    # 2. Time Source
    clock = bd.TIME()
    
    # 3. Flight Controller (Multi-Input: State, Time)
    # Issue: wiring multiple inputs to FUNCTION in 1-to-1 loop.
    # MUX failed before.
    # SOLUTION: We will assume 't' is passed via 'flight_controller' signature?
    # NO, bdsim function block calling convention depends on nin.
    # If nin=2, it expects 2 input wires.
    
    controller = bd.FUNCTION(flight_controller, nin=2, nout=1, name='Controller')
    
    # 4. Power System
    power = bd.FUNCTION(power_system, nin=1, nout=1, name='PowerSystem')
    
    # 5. Dynamics
    dynamics = bd.FUNCTION(rigid_body_dynamics, nin=1, nout=1, name='Dynamics')
    
    # 6. Scope (Z)
    def selector_z(state):
        if isinstance(state, (list, tuple)): state = np.array(state)
        val = float(state[2])
        return val 
    selector = bd.FUNCTION(selector_z, nin=1, nout=1, name='Selector')
    scope = bd.SCOPE(styles=['b'], labels=['z'], name='Scope')
    
    
    # --- Wiring ---
    # Controller nin=2, Integrator nout=1
    # Connect Integrator -> Controller[0]
    # Connect Clock -> Controller[1]
    
    # Correct Syntax: Assignment
    # dest[port] = source
    
    controller[0] = integrator
    controller[1] = clock
    
    # 1-to-1 connections can use assignment too for consistency or bd.connect
    power[0] = controller
    dynamics[0] = power
    integrator[0] = dynamics
    
    selector[0] = integrator
    scope[0] = selector
    
    # Export
    print("Generating complex block diagram to 'quadcopter_diagram.dot'...")
    bd.dotfile('quadcopter_diagram.dot')
    
    print("Compiling...")
    bd.compile()
    
    if pixel_plot: return bd
    
    # NO 3D VIZ in pure sim run (headless safe)
    # The viz is in run_animation.py
    print("Starting Simulation...")
    sim.run(bd, T=10.0, dt=0.01)
    print("Simulation Complete.")
    
    if __name__ == "__main__":
        sim.done(bd, block=True)

if __name__ == "__main__":
    run_simulation()
