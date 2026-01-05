import bdsim
sim = bdsim.BDSim()
bd = sim.blockdiagram()

# Source (1 Out)
src = bd.FUNCTION(lambda t: 1, nin=1, nout=1, name='Source')
time = bd.TIME(name='Time')
# Standard connect (1-to-1)
# bd.connect(time, src) 
# Try assignment for 1-to-1 too?
src[0] = time


# Dest (2 In)
def sum_func(u1, u2): return u1+u2
dest = bd.FUNCTION(sum_func, nin=2, nout=1, name='Dest')

# Wiring with Assignment
print("Wiring Dest[0] = Src")
try:
    dest[0] = src
    print("Success Dest[0]")
except Exception as e:
    print(f"Fail Dest[0]: {e}")

print("Wiring Dest[1] = Time")
try:
    dest[1] = time
    print("Success Dest[1]")
except Exception as e:
    print(f"Fail Dest[1]: {e}")

print("Compiling...")
try:
    bd.compile()
    print("Compile OK")
except Exception as e:
    print(f"Compile Fail: {e}")
