import bdsim
sim = bdsim.BDSim()
bd = sim.blockdiagram()
print(f"Has dotfile: {hasattr(bd, 'dotfile')}")
print(f"Has show: {hasattr(bd, 'show')}")
print(dir(bd))
