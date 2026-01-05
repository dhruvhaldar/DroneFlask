import bdsim
import numpy as np

sim = bdsim.BDSim()
bd = sim.blockdiagram()

src = bd.CONSTANT(1.0)
integ = bd.INTEGRATOR(x0=0)
bd.connect(src, integ)
bd.compile()

print("Running with watch...")
res = sim.run(bd, T=1.0, dt=0.1, watch=[integ])
print(f"Result type: {type(res)}")
print(f"Result dir: {dir(res)}")
print(f"Data: {res.data if hasattr(res, 'data') else 'No data attr'}")
print(f"y: {res.y if hasattr(res, 'y') else 'No y attr'}")
