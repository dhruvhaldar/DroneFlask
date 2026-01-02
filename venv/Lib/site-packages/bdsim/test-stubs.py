import bdsim

sim = bdsim.BDSim(animation=True)  # create simulator
bd = sim.blockdiagram()

g = bd.GAIN()
p = bd.PROD()

s = bd.SUM()

bd.report()

from bdsim.blocks import *

a = bd.GAIN()