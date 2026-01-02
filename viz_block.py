import bdsim
from bdsim.components import SinkBlock

class QuadVizBlock(SinkBlock):
    def __init__(self, visualizer, *inputs, **kwargs):
        super().__init__(nin=1, **kwargs)
        self.type = 'quad_viz'
        self.viz = visualizer
        
    def step(self, state=None):
        # state is the input
        if state is not None:
            self.viz.update(state)
