"""GUI and graphics for game."""

import shelve
from tkinter import *
from tkinter import ttk
from turtle import TurtleScreen, RawPen, _CFG
from operator import add, sub
from random import choice

from tripeg.movepaths import PathFinder
from tripeg.animations import *

class BasicGUI:
    """Base class for all GUI/graphics implementations. Includes
    properly gridded widgets but no functionality."""

    def __init__(self):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.root = Tk()
        self.root.title("Triangle Peg Game")
        self.root.resizable(False, False)
        self._init_widgets()

    def _init_widgets(self):
        """Creates and grids widgets."""
        # Creates widgets:
        self.mainframe = ttk.Frame(self.root, padding="5 5 5 5")
        self.canvas = Canvas(self.mainframe, width=500, height=500,
                             relief="sunken", borderwidth=3)
        right_column = ttk.Frame(self.mainframe)
        game_buttons = ttk.Labelframe(right_column, text="Controls")
        help_buttons = ttk.Labelframe(right_column, text="Help")
        self.undo_btn = ttk.Button(game_buttons, text="Undo", state="disabled")
        self.restart_btn = ttk.Button(game_buttons, text="Restart",
                                      state="disabled")
        self.show_moves_btn = ttk.Button(help_buttons, text="Show Moves")
        self.best_move_btn = ttk.Button(help_buttons, text="Best Move",
                                        state="disabled")
        # Grids widgets:
        self.mainframe.grid(row=0, column=0, sticky=(N,S,E,W))
        self.canvas.grid(row=1, column=1, sticky=(N,S,E,W))
        right_column.grid(row=1, column=2, sticky=(N,S,E,W))
        game_buttons.grid(row=1, column=1)
        help_buttons.grid(row=2, column=1)
        self.undo_btn.grid(row=1, column=1)
        self.restart_btn.grid(row=2, column=1)
        self.show_moves_btn.grid(row=1, column=1)
        self.best_move_btn.grid(row=2, column=1)

class TurtleGraphics(BasicGUI):
    """GUI with graphics created using 'turtle'."""

    _world_coords = (-2,-2,10,10)
    _peg_offset = (0,0.4)
    _hades = (0,12)
    best_move = None

    @classmethod
    def _add_offset(cls, position):
        """Adds offset to peg's position coordinates."""
        peg_pos = tuple(map(add, position, cls._peg_offset))
        peg_pos = tuple(round(i, 1) for i in peg_pos)
        return peg_pos

    @classmethod
    def _subtract_offset(cls, position):
        """Subtracts offset from peg's position coordinates."""
        peg_pos = tuple(map(sub, position, cls._peg_offset))
        peg_pos = tuple(map(int, peg_pos))
        return peg_pos
        
    def _draw_board(self):
        """Draws board."""
        tri = ((-1.5,-0.5),(4,9.5),(9.5,-0.5))
        artist = RawPen(self.window)
        # Draws grooves in wood:
        artist.pen(pendown=False, pensize=2, speed=0)
        x1, y1, x2, y2 = __class__._world_coords
        for y in range(y1, y2+1, 2):
            artist.goto(x1, y)
            artist.pendown()
            artist.goto(x2, y)
            artist.penup()
        # Draws board:
        artist.pen(pencolor=(34,16,0), fillcolor=(51,25,0), pensize=6,
                        speed=0)
        artist.goto(tri[-1])
        artist.pendown()
        artist.begin_fill()
        for coord in tri:
            artist.goto(coord)
        artist.end_fill()
        # Draws peg holes:
        artist.pen(pencolor="gray", fillcolor="black", pensize=1)
        for peg_hole in self.game.board:
            artist.penup()
            artist.goto(peg_hole)
            artist.pendown()
            artist.begin_fill()
            artist.circle(0.4)
            artist.end_fill()
        artist.penup()
        artist.goto(__class__._hades)

    def _place_pegs(self):
        """Places pegs."""
        for peg_hole in self.game.board:
            if self.game.board[peg_hole]:
                start_point = __class__._add_offset(peg_hole)
                peg = Peg(start_point, self)
                self.peg_dir.append(peg)

    def _add_callbacks(self):
        """Adds callbacks to buttons."""
        self.undo_btn["command"] = self.game.undo
        self.restart_btn["command"] = self.game.restart
        self.show_moves_btn["command"] = self.show_legal_moves
        self.best_move_btn["command"] = self.show_best_move

    def _find_best_move(self):
        """Finds best move possible for current game."""
        if len(self.game.moves) <= 3:
            with shelve.open("paths") as db:
                best_paths = db[str(self.game.moves)]
                best_path = choice(best_paths)
        else:
            self.path_finder(self.game)
            best_path = self.path_finder.best_path
        best_move = best_path[len(self.game.moves)]
        best_move = (__class__._add_offset(best_move[0]), best_move[1])
        return best_move

    def _add_artist(self):
        """Adds artist to 'artist_dir'."""
        artist = RawPen(self.window)
        artist.shape("arrow")
        artist.pen(pendown=False, shown=True, pencolor="green", speed=0,
                   fillcolor="green", pensize=2)
        self.artist_dir.append(artist)

    def _disable_all(self):
        """Disables all buttons and pegs."""
        self.undo_btn["state"] = "disabled"
        self.restart_btn["state"] = "disabled"
        self.show_moves_btn["state"] = "disabled"
        self.best_move_btn["state"] = "disabled"
        for peg in self.peg_dir:
            peg.moveable = False

    def _restore_all(self):
        """Enables pegs and buttons that would normally be enabled."""
        self.update_gui()
        for peg in self.peg_dir:
            peg.moveable = True

    def _delayed_callback(self, artists):
        """Sends artist to Hades."""
        for artist in artists:
            artist.clear()
            artist.penup()
            artist.goto(__class__._hades)
        self._restore_all()
        
    def construct(self):
        """Constructs graphics."""
        self.window = TurtleScreen(self.canvas)
        self.window.setworldcoordinates(*__class__._world_coords)
        self.window.bgcolor(102,51,0)
        self.peg_dir = []
        self.artist_dir = []
        self.graveyard = []
        self.path_finder = PathFinder()
        self._draw_board()
        self._place_pegs()
        self._add_callbacks()

    def update_(self, peg, move):
        """Updates the graphics when a move is made."""
        midpoint = __class__._add_offset(self.game._midpoint(peg, move))
        lower_bound = (midpoint[0], midpoint[1]-0.01)
        upper_bound = (midpoint[0], midpoint[1]+0.01)
        dead_peg = [peg for peg in self.peg_dir if peg.pos() > lower_bound and
                    peg.pos() < upper_bound][0]
        dead_peg.goto(__class__._hades)
        self.peg_dir.remove(dead_peg)
        self.graveyard.append(dead_peg)

    def erase(self):
        """Updates the graphics when a move is undone."""
        last_peg_pos = __class__._add_offset(tuple(map(
            add, *self.game.moves[-1])))
        last_peg = [peg for peg in self.peg_dir if abs(peg.pos()-last_peg_pos)
                    < 0.1][0]
        last_peg.goto(__class__._add_offset(self.game.moves[-1][0]))
        last_peg.start_point = last_peg.pos()
        revived_peg = self.graveyard.pop()
        revived_peg.goto(revived_peg.start_point)
        self.peg_dir.append(revived_peg)
        
    def reset_(self):
        """Updates the graphics when the game is restarted."""
        for obj in [self.window, self.peg_dir, self.artist_dir, self.graveyard]:
            del obj
        self.canvas.destroy()
        self.canvas = Canvas(self.mainframe, width=500, height=500,
                             relief="sunken", borderwidth=3)
        self.canvas.grid(row=1, column=1, sticky=(N,S,E,W))
        self.construct()
         
    def show_legal_moves(self):
        """Shows the player all legal moves."""
        self._disable_all()
        move_count = 0
        legal_moves = self.game.find_legal_moves()
        for val in legal_moves.values():
            for move in val:
                move_count += 1
        artists_needed = move_count - len(self.artist_dir)
        for task in range(artists_needed):
            self._add_artist()
        used_artists = []
        artist_count = 0
        for start_peg in legal_moves:
            for move in legal_moves[start_peg]:
                artist = self.artist_dir[artist_count]
                artist.goto(__class__._add_offset(start_peg))
                destination = tuple(map(add, artist.pos(), move))
                draw_arrow(artist, destination)
                used_artists.append(artist)
                artist_count += 1
        self.root.after(3000, self._delayed_callback, used_artists)
        
    def show_best_move(self):
        """Shows the player the best move to make next."""
        self._disable_all()
        if not self.artist_dir:
            self._add_artist()
        artist = self.artist_dir[0]
        artist.goto(self.best_move[0])
        destination = tuple(map(add, artist.pos(), self.best_move[1]))
        draw_arrow(artist, destination)
        self.root.after(3000, self._delayed_callback, [artist])

    def update_peg_moves(self):
        """Updates move list for all pegs."""
        legal_moves = self.game.find_legal_moves()
        for peg in self.peg_dir:
            board_pos = __class__._subtract_offset(peg.pos())
            peg.possible_moves = legal_moves.get(board_pos, [])
        if legal_moves and len(self.game.moves) >= 1:
            self.best_move = self._find_best_move()

    def update_gui(self):
        """Updates GUI to reflect current game conditions."""
        legal_moves = self.game.find_legal_moves()
        if self.game.moves:
            self.undo_btn["state"] = "!disabled"
            self.restart_btn["state"] = "!disabled"
            self.best_move_btn["state"] = "!disabled"
        else:
            self.undo_btn["state"] = "disabled"
            self.restart_btn["state"] = "disabled"
        if legal_moves:
            self.show_moves_btn["state"] = "!disabled"
        else:
            self.show_moves_btn["state"] = "disabled"
        if legal_moves and self.game.moves:
            self.best_move_btn["state"] = "!disabled"
        else:
            self.best_move_btn["state"] = "disabled"

class Peg(RawPen):
    """A specialized 'RawPen' that represents a peg."""

    moveable = True

    def __init__(self, start_point, graphics):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.graphics = graphics
        self.possible_moves = []
        super().__init__(self.graphics.canvas, "circle", _CFG["undobuffersize"],
                         True)
        self.pen(pendown=False, speed=0, outline=2, fillcolor="red",
                 pencolor="black", stretchfactor=(1.25,1.25))
        self.start_point = start_point
        self.goto(start_point)
        self.ondrag(self._remove)
        self.onrelease(self._place)

    def _remove(self, x, y):
        """Removes peg from hole if it has moves."""
        if self.possible_moves and self.moveable:
            self.goto(x,y)

    def _place(self, x, y):
        """Places peg in peg hole if legal."""
        if self.possible_moves:
            target_holes = [tuple(map(add, self.start_point, move)) for move in
                            self.possible_moves]
            distances = [self.distance(hole) for hole in target_holes]
            hole_distances = dict(zip(distances, target_holes))
            nearest_hole = hole_distances[min(hole_distances)]
            if self.distance(nearest_hole) <= 0.45:
                self.goto(nearest_hole)
                peg = self.graphics._subtract_offset(self.start_point)
                move = tuple(map(sub, self.pos(), self.start_point))
                move = tuple(map(int, move))
                self.graphics.game.move(peg, move)
                self.start_point = self.pos()
            else:
                self.goto(self.start_point)
                
