import bdsim
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.widgets import Button
from quadcopter_bdsim import flight_controller, power_system, rigid_body_dynamics
import visualization

def run_viz_with_controls():
    # --- 1. Simulation Phase (Sequential) ---
    print("Initializing Simulation...")
    sim = bdsim.BDSim(animation=False)
    bd = sim.blockdiagram()
    
    # Blocks
    integrator = bd.INTEGRATOR(x0=np.zeros(12), name='Integrator')
    clock = bd.TIME()
    controller = bd.FUNCTION(flight_controller, nin=2, nout=1, name='Controller')
    power = bd.FUNCTION(power_system, nin=1, nout=1, name='PowerSystem')
    dynamics = bd.FUNCTION(rigid_body_dynamics, nin=1, nout=1, name='Dynamics')
    
    def selector_z(state):
        if isinstance(state, (list, tuple)): state = np.array(state)
        return float(state[2])
    selector = bd.FUNCTION(selector_z, nin=1, nout=1, name='Selector')
    
    # Wiring
    controller[0] = integrator
    controller[1] = clock
    power[0] = controller
    dynamics[0] = power
    integrator[0] = dynamics
    selector[0] = integrator
    
    bd.compile()
    
    print("Running simulation (10s)...")
    res = sim.run(bd, T=10.0, dt=0.01)
    states = res.x
    
    if states is None:
        print("Error: No data.")
        return

    print(f"Simulation done. Frames: {len(states)}")
    
    # --- 2. Animation Phase ---
    print("Starting Animation...")
    viz = visualization.QuadcopterVisualizer(auto_show=False)
    plt.subplots_adjust(bottom=0.2)
    
    # Skip logic
    skip = 2
    anim_data = states[::skip]
    
    class Player:
        def __init__(self, viz, data):
            self.viz = viz
            self.data = data
            self.paused = False
            # Interval=50ms (20FPS)
            self.anim = FuncAnimation(viz.fig, self.update, frames=len(data), 
                                      interval=50, blit=False, repeat=True)
            
        def update(self, frame):
            state = self.data[frame]
            self.viz.update(state)
            
        def toggle_pause(self, event):
            if self.paused:
                self.anim.resume()
                self.paused = False
                btn_pause.label.set_text('Pause')
            else:
                self.anim.pause()
                self.paused = True
                btn_pause.label.set_text('Play')
                
        def replay(self, event):
            self.anim.frame_seq = self.anim.new_frame_seq() 
            
        def export(self, event):
            print("Exporting...")
            was_paused = self.paused
            if not was_paused: self.anim.pause()
            try:
                filename = "quadcopter_flight.avif"
                print(f"Saving to {filename} (Pillow)...")
                self.anim.save(filename, writer=PillowWriter(fps=30))
                print("Export AVIF Success!")
            except Exception as e:
                print(f"AVIF Failed: {e}")
                print("Fallback to GIF...")
                try:
                    self.anim.save("quadcopter_flight.gif", writer=PillowWriter(fps=30))
                    print("Export GIF Success!")
                except Exception as e2:
                    print(f"GIF Failed: {e2}")
            if not was_paused: self.anim.resume()

    player = Player(viz, anim_data)

    # Buttons
    ax_pause = plt.axes([0.4, 0.05, 0.1, 0.075])
    ax_replay = plt.axes([0.51, 0.05, 0.1, 0.075])
    ax_export = plt.axes([0.62, 0.05, 0.15, 0.075])
    
    btn_pause = Button(ax_pause, 'Pause')
    btn_pause.on_clicked(player.toggle_pause)
    
    btn_replay = Button(ax_replay, 'Replay')
    btn_replay.on_clicked(player.replay)
    
    btn_export = Button(ax_export, 'Export AVIF')
    btn_export.on_clicked(player.export)
    
    # Store ref
    viz.fig._player = player
    
    print("Animation Controls: [Pause] [Replay] [Export AVIF]")
    plt.show()
    return player

if __name__ == "__main__":
    _ = run_viz_with_controls()
