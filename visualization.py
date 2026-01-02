import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3

class QuadcopterVisualizer:
    def __init__(self, arm_length=0.25, auto_show=True):
        self.L = arm_length
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Initial Plot
        self.ax.set_xlim3d([-2, 2])
        self.ax.set_ylim3d([-2, 2])
        self.ax.set_zlim3d([0, 5])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('6DOF Quadcopter Simulation')
        
        # Quadcopter Body (X configuration)
        # Arms: [FrontRight, RearLeft], [FrontLeft, RearRight]
        self.arm1, = self.ax.plot([], [], [], 'r-', linewidth=2, label='Front') 
        self.arm2, = self.ax.plot([], [], [], 'b-', linewidth=2) 
        self.payload, = self.ax.plot([], [], [], 'ko', markersize=4)
        
        # Trail
        self.trail_x = []
        self.trail_y = []
        self.trail_z = []
        self.trail, = self.ax.plot([], [], [], 'g:', linewidth=1, alpha=0.5)
        
        if auto_show:
            plt.ion() # Interactive mode
            plt.show(block=False)

    def update(self, state):
        # state: [x, y, z, vx, vy, vz, phi, theta, psi, ...]
        if isinstance(state, (list, tuple)): state = np.array(state).flatten()
        
        x, y, z = state[0], state[1], state[2]
        phi, theta, psi = state[6], state[7], state[8]
        
        # Rotation Matrix (Body -> Inertial)
        R = self._get_rotation_matrix(phi, theta, psi)
        
        # Arm vectors in Body Frame
        # Arm 1: X-axis (forward) ? Or diagonal. 
        # Sim assumes X config usually diagonal.
        d = self.L / np.sqrt(2)
        
        # Define 4 motor positions in Body Frame
        # 1: Front-Right (+d, -d, 0)
        # 2: Rear-Left (-d, +d, 0)
        # 3: Front-Left (+d, +d, 0)
        # 4: Rear-Right (-d, -d, 0)
        
        p1_b = np.array([ d, -d, 0])
        p2_b = np.array([-d,  d, 0])
        p3_b = np.array([ d,  d, 0])
        p4_b = np.array([-d, -d, 0])
        
        # Rotate to Inertial
        p1 = np.dot(R, p1_b) + [x, y, z]
        p2 = np.dot(R, p2_b) + [x, y, z]
        p3 = np.dot(R, p3_b) + [x, y, z]
        p4 = np.dot(R, p4_b) + [x, y, z]
        center = np.array([x, y, z])
        
        # Draw Arms (Cross)
        # Line 1: p2 -> center -> p1 (RearLeft to FrontRight)
        # Line 2: p4 -> center -> p3 (RearRight to FrontLeft)
        
        self.arm1.set_data([p2[0], p1[0]], [p2[1], p1[1]])
        self.arm1.set_3d_properties([p2[2], p1[2]])
        
        self.arm2.set_data([p4[0], p3[0]], [p4[1], p3[1]])
        self.arm2.set_3d_properties([p4[2], p3[2]])
        
        self.payload.set_data([x], [y])
        self.payload.set_3d_properties([z])
        
        # Trail
        self.trail_x.append(x)
        self.trail_y.append(y)
        self.trail_z.append(z)
        
        # Limit trail length
        # Limit trail length (Increased for longer history)
        if len(self.trail_x) > 2000:
            self.trail_x.pop(0)
            self.trail_y.pop(0)
            self.trail_z.pop(0)
            
        self.trail.set_data(self.trail_x, self.trail_y)
        self.trail.set_3d_properties(self.trail_z)
        
        # Dynamic Axis Scaling
        self._adjust_axes(x, y, z)
        
        # NOTE: Removed self.fig.canvas.flush_events() 
        # FuncAnimation handles drawing. Manual flushing causes double-draw lag.

    def _adjust_axes(self, x, y, z):
        # Optimization: Lazy update
        # Only call set_*lim if we are close to the edge or outside
        # This prevents re-calculating the scene box every frame
        
        xlim = self.ax.get_xlim3d()
        ylim = self.ax.get_ylim3d()
        zlim = self.ax.get_zlim3d()
        
        updated = False
        margin = 1.0
        buffer = 0.5 # Trigger buffer
        
        # Check X
        new_xlim = list(xlim)
        if x < xlim[0] + buffer:
            new_xlim[0] = x - margin
            updated = True
        if x > xlim[1] - buffer:
            new_xlim[1] = x + margin
            updated = True
        
        # Check Y
        new_ylim = list(ylim)
        if y < ylim[0] + buffer:
            new_ylim[0] = y - margin
            updated = True
        if y > ylim[1] - buffer:
            new_ylim[1] = y + margin
            updated = True
            
        # Check Z
        new_zlim = list(zlim)
        if z > zlim[1] - buffer:
            new_zlim[1] = z + margin
            updated = True
        
        if updated:
            # Debug: Prove lazy scaling is working
            # print(f"Resizing Axes... X:{new_xlim}")
            self.ax.set_xlim3d(new_xlim)
            self.ax.set_ylim3d(new_ylim)
            self.ax.set_zlim3d([0, max(5, new_zlim[1])])
        
    def _get_rotation_matrix(self, phi, theta, psi):
        cpsi, spsi = np.cos(psi), np.sin(psi)
        ctheta, stheta = np.cos(theta), np.sin(theta)
        cphi, sphi = np.cos(phi), np.sin(phi)
        
        R = np.array([
            [cpsi*ctheta, cpsi*stheta*sphi - spsi*cphi, cpsi*stheta*cphi + spsi*sphi],
            [spsi*ctheta, spsi*stheta*sphi + cpsi*cphi, spsi*stheta*cphi - cpsi*sphi],
            [-stheta,     ctheta*sphi,                  ctheta*cphi]
        ])
        return R
    
    def close(self):
        plt.ioff()
        plt.close(self.fig)

if __name__ == "__main__":
    # Test
    import time
    v = QuadcopterVisualizer()
    for i in range(50):
        v.update([0, 0, i*0.1, 0,0,0, i*0.1, 0, i*0.1])
        time.sleep(0.1)
