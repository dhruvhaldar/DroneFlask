from quadcopter_web import setup_web_simulation
import queue
import time
import numpy as np

print("Running simulation debug...")
q = queue.Queue()
state = {'cmd': [0.5, 0, 0, 0]} # Test input (Hover thrust?)

try:
    sim, bd = setup_web_simulation(state, q)
    print("Compiled. Starting run...")
    # Run for short time
    sim.run(bd, T=0.11, dt=0.01)
    print("Run Complete.")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
