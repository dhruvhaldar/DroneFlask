import socketio
import time

sio = socketio.Client()
yaw_changes = []

@sio.event
def connect():
    print("Connected.")
    # Low thrust, Max Yaw
    sio.emit('control', {'thrust': 0.1, 'roll': 0, 'pitch': 0, 'yaw': 1.0})

@sio.on('state')
def on_state(data):
    # data: [x,y,z, vx,vy,vz, phi,theta,psi, p,q,r]
    # psi is index 8
    psi = data['data'][8]
    yaw_changes.append(psi)
    if len(yaw_changes) % 20 == 0:
        print(f"Current Yaw: {psi}")

if __name__ == '__main__':
    try:
        sio.connect('http://localhost:5001')
        time.sleep(3)
        sio.disconnect()

        # Analyze
        if len(yaw_changes) > 1:
            diff = yaw_changes[-1] - yaw_changes[0]
            print(f"Total Yaw Change: {diff}")
            if abs(diff) > 0.01:
                print("SUCCESS: Drone rotates on ground.")
            else:
                print("FAILURE: Drone stationary.")
        else:
            print("FAILURE: No data received.")

    except Exception as e:
        print(f"Error: {e}")
