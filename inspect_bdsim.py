import bdsim
import numpy as np

sim = bdsim.BDSim()
bd = sim.blockdiagram()

blk = bd.FUNCTION(lambda x: x, nin=2, nout=1)
print(f"Dir: {dir(blk)}")
print(f"Inputs: {getattr(blk, 'inputs', 'N/A')}")
print(f"Inports: {getattr(blk, 'inports', 'N/A')}")
print(f"In: {getattr(blk, 'in_', 'N/A')}") # 'in' is keyword
