#!/usr/bin/env python3

"""Main script."""

from tripeg.game import MainGame
from tripeg.graphics import TurtleGraphics

def main():
    """Main function."""
    game = MainGame()
    game(TurtleGraphics())

if __name__ == "__main__":
    main()
