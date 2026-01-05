import bdsim
sim = bdsim.BDSim()
bd = sim.blockdiagram()

blk = bd.FUNCTION(lambda x: x, nin=2, nout=1)
try:
    p0 = blk[0]
    print(f"Blk[0] Type: {type(p0)}")
    print(f"Blk[0] Dir: {dir(p0)}")
except Exception as e:
    print(f"Blk[0] Error: {e}")
