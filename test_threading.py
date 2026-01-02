import bdsim
import threading
import time

def thread_target():
    print("Thread Start")
    sim = bdsim.BDSim(animation=False)
    bd = sim.blockdiagram()
    src = bd.CONSTANT(1)
    # Generic sink
    snk = bd.LREC(nin=1)
    bd.connect(src, snk)
    bd.compile()
    print("Thread Run")
    sim.run(bd, T=1.0)
    print("Thread Done")

t = threading.Thread(target=thread_target)
t.start()
t.join()
print("Main Done")
