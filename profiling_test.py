import numpy as np
import matplotlib.pyplot as plt

# Coefficients from Thesis
kF = 8.875e-6
kM = 1.203e-7

def calculate_thrust(omega):
    """Calculates thrust (N) given omega (rad/s)"""
    return kF * omega**2

def calculate_torque(omega):
    """Calculates torque (N.m) given omega (rad/s)"""
    return kM * omega**2

def plot_profiles():
    # Simulate motor speeds from 0 to 1000 rad/s (approx 9500 RPM)
    w_min = 0
    w_max = 1000
    w = np.linspace(w_min, w_max, 100)
    
    thrust = calculate_thrust(w)
    torque = calculate_torque(w)
    
    plt.figure(figsize=(12, 5))
    
    # Thrust Plot
    plt.subplot(1, 2, 1)
    plt.plot(w, thrust, 'r-', linewidth=2)
    plt.title('Thrust Profile')
    plt.xlabel('Angular Velocity (rad/s)')
    plt.ylabel('Thrust (N)')
    plt.grid(True)
    
    # Torque Plot
    plt.subplot(1, 2, 2)
    plt.plot(w, torque, 'b-', linewidth=2)
    plt.title('Torque Profile')
    plt.xlabel('Angular Velocity (rad/s)')
    plt.ylabel('Torque (N.m)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('profiling_results.png')
    print("Profiling plot saved to 'profiling_results.png'")
    # plt.show() # Uncomment to show interactive plot

if __name__ == "__main__":
    plot_profiles()
