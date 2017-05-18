"""Defines main game classes."""

from operator import add

class BaseGame:
    """Base class for all game classes."""

    _ORIGINAL_BOARD = {(0,0): 1, (2,0): 1, (4,0): 1, (6,0): 1, (8,0): 1,
                       (1,2): 1, (3,2): 1, (5,2): 1, (7,2): 1, (2,4): 1,
		       (4,4): 1, (6,4): 1, (3,6): 1, (5,6): 1, (4,8): 0}
    _POSSIBLE_MOVES = {(0,0): ((4,0),(2,4)),
                       (2,0): ((4,0),(2,4)),
                       (4,0): ((-4,0),(4,0),(2,4),(-2,4)),
                       (6,0): ((-4,0),(-2,4)),
                       (8,0): ((-4,0),(-2,4)),
                       (1,2): ((4,0),(2,4)),
                       (3,2): ((4,0),(2,4)),
                       (5,2): ((-4,0),(-2,4)),
                       (7,2): ((-4,0),(-2,4)),
                       (2,4): ((4,0),(2,4),(-2,-4),(2,-4)),
                       (4,4): ((-2,-4,),(2,-4)),
                       (6,4): ((-4,0),(-2,4),(-2,-4),(2,-4)),
                       (3,6): ((-2,-4),(2,-4)),
                       (5,6): ((-2,-4),(2,-4)),
                       (4,8): ((-2,-4),(2,-4))}
    started = False

    def __call__(self):
        """Call self as function."""
        self.started = True
        self.board = self._ORIGINAL_BOARD.copy()
        self.peg_count = 14
        self.moves = []

    @staticmethod
    def _endpoint(peg, move):
        """Finds the endpoint of a move vector."""
        endpoint = tuple(map(add, peg, move))
        return endpoint

    @staticmethod
    def _midpoint(peg, move):
        """Finds the midpoint of a move vector."""
        move = tuple(i//2 for i in move)
        midpoint = tuple(map(add, peg, move))
        return midpoint

    def _is_legal(self, peg, move):
        """Determines if a move is legal or not."""
        endpoint = self._endpoint(peg, move)
        midpoint = self._midpoint(peg, move)
        try:
            if not self.board[midpoint] or self.board[endpoint]:
                return False
            else:
                return True
        except KeyError:
            return False

    def find_legal_moves(self):
        """Finds all moves that are currently legal.

        Returns a dictionary whose keys are the locations of holes with
        pegs in them and whose values are movement vectors that the pegs
        can legally move along.
        """
        pegs = [peg for peg in self.board if self.board[peg]]
        legal_moves = {}
        for peg in pegs:
            peg_moves = []
            for move in self._POSSIBLE_MOVES[peg]:
                if self._is_legal(peg, move):
                    peg_moves.append(move)
            if len(peg_moves):
                legal_moves[peg] = peg_moves
        return legal_moves

    def move(self, peg, move):
        """Makes a move."""
        self.board[peg] = 0
        self.board[self._midpoint(peg, move)] = 0
        self.board[self._endpoint(peg, move)] = 1
        self.peg_count -= 1
        self.moves.append((peg, move))

    def undo(self):
        """Undoes a move."""
        peg, move = self.moves.pop()
        self.board[peg] = 1
        self.board[self._midpoint(peg, move)] = 1
        self.board[self._endpoint(peg, move)] = 0
        self.peg_count += 1

    def restart(self):
        """Restarts the game."""
        self.board = self._ORIGINAL_BOARD.copy()
        self.peg_count = 14
        self.moves.clear()

class MainGame(BaseGame):
    """Main game class."""

    def __call__(self, graphics):
        """Call self as function."""
        super().__call__()
        self.graphics = graphics
        self.graphics.game = self
        self.graphics.construct()
        self.graphics.update_peg_moves()
        self.graphics.window.mainloop()

    def move(self, peg, move):
        """Makes a move."""
        super().move(peg, move)
        self.graphics.update_(peg, move)
        self.graphics.update_peg_moves()
        self.graphics.update_gui()

    def undo(self):
        """Undoes a move."""
        self.graphics.erase()
        super().undo()
        self.graphics.update_peg_moves()
        self.graphics.update_gui()

    def restart(self):
        """Restarts the game."""
        super().restart()
        self.graphics.reset_()
        self.graphics.update_peg_moves()
        self.graphics.update_gui()
    
