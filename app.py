from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import threading
import queue
import time
import numpy as np

# Patch for threading support


from quadcopter_web import setup_web_simulation

app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

# --- Shared State ---
# Controls from Client (Thread-safe dict)
control_state = {
    'cmd': [0.0, 0.0, 0.0, 0.0] # [Thrust, Roll, Pitch, Yaw]
}

# Output Queue (Sim -> Web)
state_queue = queue.Queue(maxsize=1)

# Simulation Thread
sim_thread = None

def simulation_worker():
    print("SIM: Worker started")
    sim, bd = setup_web_simulation(control_state, state_queue)
    
    # Run loop manually (step by step) or full run?
    # Full run blocks. But we have a sink that pushes to queue.
    # bdsim's run allows running for a duration.
    # To be infinite, we can run for very long T, or loop step().
    # bdsim step() API exists but `run` is standard. 
    # Let's run for T=3600 (1 hour) for now.
    
    try:
        sim.run(bd, T=3600.0, dt=0.01)
    except Exception as e:
        print(f"SIM CRASH: {e}")

def background_emitter():
    """Reads queue and pushes to SocketIO"""
    print("EMIT: Worker started")
    while True:
        try:
            # Blocking get
            state = state_queue.get(timeout=1.0)
            
            # Emit to clients
            socketio.emit('state', {'data': state})
            
            # Throttle if needed? Sim runs at 100hz (dt=0.01).
            # emitting 100hz might be heavy.
            # But we want smoothness.
            # Optimization: Throttle to ~30Hz (0.033s) to save bandwidth/CPU
            # NOTE: WebSink in quadcopter_web.py already throttles production to ~30Hz.
            # Removing redundant sleep here to prevent frame drops and reduce latency.
            socketio.sleep(0)
            
        except queue.Empty:
            pass # No data yet
        except Exception as e:
            print(f"EMIT ERROR: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('control')
def handle_control(json):
    # Optimization: Removed blocking print on every packet
    # json: {'thrust': 0.5, 'roll': 0.1 ...}
    t = float(json.get('thrust', 0))
    r = float(json.get('roll', 0))
    p = float(json.get('pitch', 0))
    y = float(json.get('yaw', 0))
    
    # Update shared state
    control_state['cmd'] = [t, r, p, y]
    # print(f"CMD: {control_state['cmd']}")

@socketio.on('reset_sim')
def handle_reset():
    print("DEBUG: Reset Requested. Resetting State...")
    # Ideally we restart the sim thread.
    # For now, let's just zero the controls.
    # A true reset is hard with bdsim's blocking run.
    control_state['cmd'] = [0.0, 0.0, 0.0, 0.0]

if __name__ == '__main__':
    # Start Simulation
    t_sim = threading.Thread(target=simulation_worker, daemon=True)
    t_sim.start()
    
    # Start Emitter
    socketio.start_background_task(background_emitter)
    
    print("SERVER: Starting on http://127.0.0.1:5001")
    socketio.run(app, debug=True, use_reloader=False, port=5001)
