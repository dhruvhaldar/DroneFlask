import bdsim
sim = bdsim.BDSim()
bd = sim.blockdiagram()
print("--- CONNECT DOCS ---")
print(bd.connect.__doc__)
print("--------------------")
print(f"Connect method args: {bd.connect.__code__.co_varnames}")
