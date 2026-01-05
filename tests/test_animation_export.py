import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import os
import visualization

def test_export():
    print("Testing Animation Export...")
    
    # 1. Setup Viz and Dummy Data
    viz = visualization.QuadcopterVisualizer()
    frames = 10
    data = [np.zeros(12) for _ in range(frames)]
    for i in range(frames):
        data[i][2] = i * 0.1 # Move up
    
    fig = viz.fig
    
    def update(frame):
        viz.update(data[frame])
    
    anim = FuncAnimation(fig, update, frames=frames, interval=100)
    
    # 2. Try Export
    filename = "test_export.avif"
    fallback = "test_export.gif"
    
    # Cleanup old
    if os.path.exists(filename): os.remove(filename)
    if os.path.exists(fallback): os.remove(fallback)
    
    try:
        print(f"Attempting AVIF export to {filename}...")
        anim.save(filename, writer=PillowWriter(fps=10))
        if os.path.exists(filename):
            print(f"SUCCESS: Created {filename} ({os.path.getsize(filename)} bytes)")
        else:
            print("FAILURE: File not created (AVIF).")
            
    except Exception as e:
        print(f"AVIF Failed: {e}")
        print(f"Attempting GIF fallback to {fallback}...")
        try:
            anim.save(fallback, writer=PillowWriter(fps=10))
            if os.path.exists(fallback):
                print(f"SUCCESS: Created {fallback} ({os.path.getsize(fallback)} bytes)")
            else:
                print("FAILURE: File not created (GIF).")
        except Exception as e2:
            print(f"GIF Failed: {e2}")

    plt.close(fig)

if __name__ == "__main__":
    test_export()
