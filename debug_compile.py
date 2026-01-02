from quadcopter_web import setup_web_simulation
import queue

print("Attempting to compile simulation...")
q = queue.Queue()
state = {'cmd': [0,0,0,0]}
try:
    setup_web_simulation(state, q)
    print("Success!")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
