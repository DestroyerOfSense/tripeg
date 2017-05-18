"""Contains animations to be used by graphics."""

from turtle import RawPen, _CFG

class Arrow(RawPen):
    """Specialized 'RawPen' that draws arrows from one peg to another."""

    def __init__(self, graphics):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.graphics = graphics
        super().__init__(self.graphics.canvas, "arrow", _CFG["undobuffersize"],
                         True)
        self.pen(pendown=False, speed=0, pencolor="green", fillcolor="green",
                 pensize=2)
        self.goto(self.graphics.HADES)

    def draw(self, origin, destination):
        """Draws arrow from 'origin' to 'destination'."""
        self.goto(origin)
        self.setheading(self.towards(destination))
        self.pendown()
        self.dot(10, "green")
        self.goto(destination)

    def banish(self):
        """Clears drawings and sends arrow back to Hades."""
        self.clear()
        self.penup()
        self.goto(self.graphics.HADES)
               
