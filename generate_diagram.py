def generate_diagram():
    dot_content = """
    digraph G {
        rankdir=LR;
        splines=ortho;
        node [shape=box, style=filled, fillcolor=lightblue, fontname="Helvetica"];
        edge [fontname="Helvetica", fontsize=10];

        # Nodes
        subgraph cluster_0 {
            label = "Control System";
            style = dashed;
            Controller [label="Flight Controller\n(PID)"];
        }

        subgraph cluster_1 {
            label = "Actuation";
            style = dashed;
            Power [label="Power Bridge\n(ESC)"];
            Motors [label="BLDC Motors"];
            Blades [label="Blades\n(Aerodynamics)"];
        }

        Mixer [shape=point, width=0, height=0]; 
        # Using a summation visual or just implied. 
        # User image shows Mixer as a circle with X.
        SumJunct [shape=circle, fixedsize=true, width=0.5, label="+", style=filled, fillcolor=white];

        Dynamics [label="6DOF Quadcopter\nDynamics", height=1.5];
        
        Sensors [label="Sensors\n(IMU/GPS)", fillcolor=lightgrey];

        # Edges
        # Feedback
        Dynamics -> Sensors [label=" State\n(Pos, Att)"];
        Sensors -> Controller [label=" Measured State", color=blue];
        
        # Initial Reference (Setpoint)
        Input [shape=plaintext, label="Desired\nSetpoint", fillcolor=none];
        Input -> Controller;

        # Forward Path
        Controller -> Power [label=" Voltage/PWM"];
        Power -> Motors [label=" Current"];
        Motors -> Blades [label=" Omega"];
        Blades -> SumJunct [label=" Thrust/Torque"];
        
        # Environmental Inputs
        Gravity [shape=plaintext, label="Gravity", fillcolor=none];
        Drag [shape=plaintext, label="Drag", fillcolor=none];
        
        Gravity -> SumJunct;
        Drag -> SumJunct;
        
        SumJunct -> Dynamics [label=" Net Force/Torque", penwidth=2];

    }
    """
    
    filename = "control_system.dot"
    with open(filename, 'w') as f:
        f.write(dot_content)
    print(f"Generated logical diagram: {filename}")

if __name__ == "__main__":
    generate_diagram()
