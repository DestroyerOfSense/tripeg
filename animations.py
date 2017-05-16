"""Contains animations to be used by graphics."""

__all__ = ["draw_arrow"]

def draw_arrow(artist, destination):
    """Draws arrow from artist's position to destination."""
    artist.setheading(artist.towards(destination))
    artist.pendown()
    artist.dot(10, "green")
    artist.goto(destination)

# Add more in next version.
               
