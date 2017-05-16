"""Provides various classes used for finding, storing, and manipulating move
path data."""

from functools import lru_cache
from random import choice
from time import perf_counter

from tripeg.game import BaseGame

class DummyGame(BaseGame):
    """Used to convert 'MainGame' objects into a more streamlined
    version in order to iterate over move paths at maximum speed."""

    def __init__(self, game=None):
        """Initialize self. See help(type(self)) for accurate signature."""
        if game and game.started:
            self.started = True
            self.board = game.board.copy()
            self.peg_count = game.peg_count
            self.moves = game.moves.copy()
        else:
            super().__call__()
        
class Node:
    """Wrapper for data allowing it to function as a node."""

    def __init__(self, data=None):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.data = data

class PathFinder:
    """Provides methods to find move paths that meet various criteria.

    Should be called after the player makes a move.
    """

    _game = None
    best_path = None
    best_score = None

    def __call__(self, game):
        """Call self as function."""
        if not game:
            self._game = DummyGame()
        elif not isinstance(game, DummyGame):
            self._game = DummyGame(game)
        else:
            self._game = game
        moves = self._game.moves
        self.possible_paths = dict.fromkeys(range(1,9))
        root = Node(moves[-1])
        self._find_paths(root)
        self._find_paths.cache_clear()
        found_scores = [score for score in self.possible_paths.keys() if
                        self.possible_paths[score]]
        self.best_score = min(found_scores)
        self.best_path = self.possible_paths[self.best_score]

    @lru_cache(None)
    def _find_paths(self, node):
        """Finds possible paths and records them in 'possible_paths'."""
        legal_moves = self._game.find_legal_moves()
        if not legal_moves:
            score = self._game.peg_count
            if not self.possible_paths[score]:
                self.possible_paths[score] = self._game.moves.copy()
        else:
            children = []
            for peg in legal_moves:
                for move in legal_moves[peg]:
                    children.append(Node((peg, move)))
            for child in children:
                self._game.move(*child.data)
                self._find_paths(child)
        try:
            self._game.undo()
        except IndexError:
            pass
