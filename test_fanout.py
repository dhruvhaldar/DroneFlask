import bdsim
sim = bdsim.BDSim()
bd = sim.blockdiagram()

# Source: 1 Output
src = bd.FUNCTION(lambda t: 1.0, nin=1, nout=1, name='src')
time = bd.TIME()
bd.connect(time, src)

# Destination: 2 Inputs (Sum)
def sum_func(u1, u2):
    return u1 + u2
dest = bd.FUNCTION(sum_func, nin=2, nout=1, name='dest')

# Wiring: Connect src to BOTH inputs of dest
# Using index 0 and 1
print("Connecting Src -> Dest[0]")
bd.connect(src, dest, 0)

print("Connecting Src -> Dest[1]")
bd.connect(src, dest, 1)

# Scope
scope = bd.SCOPE(name='scope')
bd.connect(dest, scope)

print("Compiling...")
try:
    bd.compile()
    print("Compile SUCCESS")
except Exception as e:
    print(f"Compile FAILED: {e}")

print("Running...")
try:
    sim.run(bd, T=1.0)
    print("Run SUCCESS")
except Exception as e:
    print(f"Run FAILED: {e}")
