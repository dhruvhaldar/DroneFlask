import bdsim
sim = bdsim.BDSim()
bd = sim.blockdiagram()
print("Help on connect:")
print(bd.connect.__doc__)

print("\nHelp on Mux:")
mux = bd.MUX(2)
print(dir(mux))
print(f"Inputs: {mux.inputs}")
# Also print help on block
print(mux.__init__.__doc__)
