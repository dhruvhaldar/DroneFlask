# 6DOF Quadcopter Simulation with `bdsim`

A high-fidelity 6-Degrees-of-Freedom (6DOF) quadcopter simulation built in Python using the `bdsim` block diagram library. This project models the rigid body dynamics, aerodynamics, and control systems of a quadcopter, complete with real-time 3D visualization.

## 1. System Architecture

The simulation is designed as a block diagram with three main modular components connected in a feedback loop.

### A. Flight Controller (`Controller`)

- **Inputs**: State Vector (12-DOF), Time ($t$).
- **Logic**: Implements a timed maneuver sequence to demonstrate control authority.
  - **0-2s**: **Takeoff & Hover** (Altitude Control).
  - **2-4s**: **Roll Maneuver** (+5.7° Roll).
  - **4-6s**: **Pitch Maneuver** (+5.7° Pitch).
  - **6-8s**: **Yaw Maneuver** (Spin at 0.5 rad/s).
  - **8-10s**: **Stabilize** (Return to Hover).
- **Algorithm**: Cascaded PID/PD controllers for Altitude ($z$) and Attitude ($\phi, \theta, \psi$).
- **Output**: 4 Motor Speed Commands ($\omega_{1-4}$).

### B. Power System (`PowerSystem`)

- **Function**: Models the Electronic Speed Controllers (ESCs) and Motor response.
- **Config**: X-Configuration Quadcopter.
- **Mixing**: Converts body torques and thrust commands into individual motor squared-speeds.

### C. Rigid Body Dynamics (`Dynamics`)

- **Physics**: Solves the Newton-Euler equations of motion for a rigid body.
- **Aerodynamics**:
  - **Thrust**: $F = k_F \omega^2$
  - **Torque**: $\tau = k_M \omega^2$
  - Coefficients derived from thesis data ($k_F = 8.875\mu$, $k_M = 0.12\mu$).
- **State**: Tracks 12 variables: Position ($x,y,z$), Velocity ($v_x,v_y,v_z$), Attitude ($\phi,\theta,\psi$), and Angular Rates ($p,q,r$).

## 2. Visualization & Animation

The project includes a custom 3D visualizer using `matplotlib` and `mpl_toolkits.mplot3d`.

### Features

- **Real-time Playback**: smooth animation of the flight trajectory.
- **Dynamic Camera**: Automatically scales and follows the drone as it moves.
- **Interactive Controls**:
  - **Pause/Play**: Toggle playback.
  - **Replay**: Restart the simulation visualization.
  - **Export AVIF**: Save the flight as a high-quality animated image (`.avif` or `.gif`).

## 3. Installation

1. **Prerequisites**: Python 3.8+.
2. **Setup**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   _Note: Requires `numpy<2.0` for `roboticstoolbox-python` compatibility._

## 4. How to Run

### A. Full 3D Animation (Recommended)

Run the simulation and launch the commercial-style visualization window:

```bash
python run_animation.py
```

### B. Headless Simulation

Generate the block diagram and run the mathematical simulation without 3D graphics (useful for debugging logic or batch processing):

```bash
python quadcopter_bdsim.py
```

### C. View Block Diagram

The simulation generates `quadcopter_diagram.dot`.

- **Visualize**: Use "Graphviz Preview" in VS Code or [Graphviz Online](https://dreampuf.github.io/GraphvizOnline/).
- **Logical Architecture**: See `control_system.dot` for the high-level engineering schematic.

## 5. File Structure

- **`run_animation.py`**: **Main Entry Point**. Runs simulation + 3D Playback UI.
- **`quadcopter_bdsim.py`**: Core simulation definition, physics, and controller logic.
- **`visualization.py`**: 3D plotting library.
- **`viz_block.py`**: Custom `bdsim` Sink block for integration.
- **`control_system.dot`**: Logical control architecture diagram.
- **`quadcopter_diagram.dot`**: Generated execution graph.

## 6. References

- **Coefficients**: "MODELLING, SIMULATION AND CONTROL OF 6-DOF QUADCOPTER" (Thesis).
- **Library**: [bdsim](https://github.com/petercorke/bdsim) by Peter Corke.
