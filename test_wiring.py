import bdsim
sim = bdsim.BDSim()
bd = sim.blockdiagram()

# Source (1 Out)
src = bd.FUNCTION(lambda t: 1, nin=1, nout=1)
time = bd.TIME()
bd.connect(time, src)

# Dest (2 In)
dest = bd.FUNCTION(lambda u1, u2: u1+u2, nin=2, nout=1)

# Try connecting to port 0
print("Connecting Src -> Dest[0]")
# Assuming the signature is connect(start, end, start_port=None, end_port=None)?
# Or connect(start, end, port)
# co_varnames was ('self', 'start', 'end', 'i', 'wire')
# so 'i' is likely the input port index on 'end'.
try:
    bd.connect(src, dest, 0)
    print("Success 0")
except Exception as e:
    print(f"Fail 0: {e}")

# Try connecting to port 1
print("Connecting Src -> Dest[1]")
try:
    bd.connect(src, dest, 1)
    print("Success 1")
except Exception as e:
    print(f"Fail 1: {e}")

print("Compile check")
try:
    bd.compile()
    print("Compile OK")
except Exception as e:
    print(f"Compile Fail: {e}")
