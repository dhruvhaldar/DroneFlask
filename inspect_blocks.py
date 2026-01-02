import bdsim
sim = bdsim.BDSim()
bd = sim.blockdiagram()
print("Available blocks/methods on bd:")
print([m for m in dir(bd) if m.isupper()])
