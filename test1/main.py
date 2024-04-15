import carrotlib as cl
from linalg import vec2
import sys
import raylib as rl
from common import *

class MyGame(cl.Game):
    def on_ready(self):
        super().on_ready()

        label = cl.controls.Label()
        label.text = "Hello, world"
        label.font_size = 0.05*vh
        label.color = cl.Colors.Black
        label.position = vec2(1*vh, 0.5*vw)

    @property
    def design_size(self):
        if sys.platform in ('ios','android'):
            return (VIEWPORT_WIDTH_INIT, 0)
        
        return WINDOW_SIZE_ON_WIN32_INIT

grid = GridLines(
    x_screen_coordinates={
        "left": (0.0, lambda x: print("left", x)),
        "center": (0.5, lambda x: print("center", x)),
        "right": (1.0, lambda x: print("right", x)),
    },
    title="Exam1Page",
    debug=True,
    tablefmt="fancy_grid"
)

print(grid)