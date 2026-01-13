import bdsim
import numpy as np
import math
import queue
from bdsim.components import SourceBlock, SinkBlock, FunctionBlock
from quadcopter_bdsim import power_system, rigid_body_dynamics
import time

# --- Interactive Control Blocks ---

class WebSource(SourceBlock):
    """
    Reads control commands [Thrust, Roll, Pitch, Yaw] from a shared object.
    """
    def __init__(self, shared_state, *inputs, **kwargs):
        super().__init__(nin=0, nout=1, **kwargs)
        self.type = 'web_source'
        self.shared_state = shared_state # Dict or Object with .cmd
        
    def output(self, t=None, *args):
        # Read conversion
        # Cmd: [Thrust(0-1), Roll(rad), Pitch(rad), YawRate(rad/s)]
        cmd = self.shared_state.get('cmd', [0,0,0,0])
        return [np.array(cmd)]

class WebSink(SinkBlock):
    """
    Writes state [x, y, z, ... 12] to a shared queue for the web server.
    """
    def __init__(self, output_queue, *inputs, **kwargs):
        super().__init__(nin=1, **kwargs)
        self.type = 'web_sink'
        self.q = output_queue
        self.counter = 0

    def step(self, t, inputs):
        # Inputs is a list of input values
        state = inputs[0]
        
        try:
            # Optimization: Throttle queue updates to ~30Hz (sim runs at 100Hz)
            # This reduces unnecessary list conversions and queue locking
            self.counter += 1
            if self.counter % 3 == 0:
                if state is not None:
                    # Optimization: Only send used telemetry (Pos, Angles) to reduce payload by 50%
                    # and avoid processing unused velocity/rate states.
                    # State indices: 0,1,2 (Pos), 3,4,5 (Vel), 6,7,8 (Ang), 9,10,11 (Rates)
                    # New payload: [x, y, z, phi, theta, psi]
                    indices = [0, 1, 2, 6, 7, 8]
                    if hasattr(state, 'tolist'):
                        # Manual selection is faster/cleaner than fancy indexing for small fixed list
                        # and avoids allocating full array for rounding
                        data = [round(float(state[i]), 4) for i in indices]
                    else:
                        data = [round(float(state[i]), 4) for i in indices]

                    # Push state to queue (non-blocking, drop old if full)
                    try:
                        self.q.put_nowait(data)
                    except queue.Full:
                        try:
                            self.q.get_nowait() # Remove old
                            self.q.put_nowait(data) # Try again
                        except (queue.Empty, queue.Full):
                            pass
                self.counter = 0
            
            # Throttle to Real-Time (approx)
            # dt is 0.01 in app.py. Sleep to prevent running at 1000x speed
            time.sleep(0.01)
        except Exception:
            pass

def flight_controller_interactive(cmd, state):
    """
    Stabilize Attitude based on Pilot Commands.
    cmd: [Thrust_Ref, Roll_Ref, Pitch_Ref, Yaw_Ref] (From WebSource)
    state: [x,y,z, vx,vy,vz, phi,theta,psi, p,q,r] (From Integrator)
    
    Output: [F_total, tau_x, tau_y, tau_z]
    """
    # Unpack Commmands
    # Thrust is normalized 0-1? Or Force?
    # Let's assume Pilot gives normalized Thrust 0-1
    # Max Thrust approx 4 * kF * w_max^2. 
    # w_max ~ 900 rad/s (from thesis?) 
    # kF = 8.875e-6
    # F_max = 4 * 8.875e-6 * 900^2 ~ 28 N. Mass ~ 1kg => 2.8g.
    
    F_max = 30.0 
    T_ref = cmd[0] * F_max
    phi_ref = cmd[1]
    theta_ref = cmd[2]
    r_ref = cmd[3] # Yaw Rate command usually
    
    # State
    z = state[2]
    vz = state[5]
    phi = state[6]
    theta = state[7]
    psi = state[8]
    p = state[9]
    q = state[10]
    r = state[11]
    
    # Gains (Tuned for ~1kg quad)
    # Altitude (Manual Thrust, so P-gain on Vel? Or just pass through?)
    # Usually manual mode passes Thrust directly.
    F_total = T_ref
    if F_total < 0: F_total = 0
    
    # Roll Control (Attitude)
    kp_phi = 2.0
    kd_phi = 0.5
    tau_phi = kp_phi * (phi_ref - phi) + kd_phi * (0 - p)
    
    # Pitch Control (Attitude)
    kp_theta = 2.0
    kd_theta = 0.5
    tau_theta = kp_theta * (theta_ref - theta) + kd_theta * (0 - q)
    
    # Yaw Control (Rate)
    kp_psi = 1.0 # acts on rate error
    tau_psi = kp_psi * (r_ref - r)
    
    # Pre-Mixer Format: [F, tau_phi, tau_theta, tau_psi]
    # u = np.array([F_total, tau_phi, tau_theta, tau_psi])
    
    # --- Mixer (Force/Torque -> Motor Speeds) ---
    kF = 8.875e-6
    kM = 1.203e-7
    L = 0.25
    
    term_F = F_total / (4*kF)
    term_phi = tau_phi / (2*L*kF)
    term_theta = tau_theta / (2*L*kF)
    term_psi = tau_psi / (4*kM)
    
    w1_sq = term_F - term_theta - term_psi
    w2_sq = term_F - term_phi   + term_psi
    w3_sq = term_F + term_theta - term_psi
    w4_sq = term_F + term_phi   + term_psi
    
    w1 = math.sqrt(max(0.0, w1_sq))
    w2 = math.sqrt(max(0.0, w2_sq))
    w3 = math.sqrt(max(0.0, w3_sq))
    w4 = math.sqrt(max(0.0, w4_sq))
    
    u = np.array([w1, w2, w3, w4])
    
    return [np.concatenate((u, state))]


def setup_web_simulation(shared_state, output_queue):
    sim = bdsim.BDSim(animation=False)
    bd = sim.blockdiagram()
    
    # Blocks
    integrator = bd.INTEGRATOR(x0=np.zeros(12), name='Integrator')
    
    # Sources
    web_input = WebSource(shared_state, name='PilotInput')
    
    # Controller (Interactive)
    # Input 0: Command (from Web), Input 1: State (from Integrator)
    controller = bd.FUNCTION(flight_controller_interactive, nin=2, nout=1, name='Controller')
    
    power = bd.FUNCTION(power_system, nin=1, nout=1, name='PowerSystem')
    dynamics = bd.FUNCTION(rigid_body_dynamics, nin=1, nout=1, name='Dynamics')
    
    # Sinks
    web_sink = WebSink(output_queue, name='WebStream')
    bd.add_block(web_sink)
    bd.add_block(web_input)
    
    # Wiring
    # Controller uses PilotInput and State
    controller[0] = web_input
    controller[1] = integrator
    
    power[0] = controller
    dynamics[0] = power
    integrator[0] = dynamics
    
    web_sink[0] = integrator
    
    bd.compile()
    print("Web Simulation Compiled.")
    return sim, bd
