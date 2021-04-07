"""
This goboard implementation clean some unnessary features from goboardv2.
For example, we don't need to code empty with zobrist hash. Remove MoveAge.
change line 97 of gobardv2 copy.deepcopy(self.liberties)
simplify line 167 of goboardv2 self._replace_string(other_color_string.without_liberty(point))
delete method will capture in Board class
delete method hash in Move class
If success, we can ignore goboardv2
"""
import copy
from dokigo.base import Player, Point
from dokigo.scoring import compute_game_result
from dokigo import zobrist

__all__ = [
    'Board',
    'GameState',
    'Move',
]

neighbor_tables = {}  # <1>
corner_tables = {}  # <2>


# <1> save neighbors in a dictionary neighbor_tables[9] is a neighbor table for a 9x9 Go game for each point
# <2> save corners in a dictionary corner_tables[1] is a corner table for a 9x9 Go game for each point


def init_neighbor_table(dim):
    rows, cols = dim
    new_table = {}
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            p = Point(row=r, col=c)
            full_neighbors = p.neighbors()
            true_neighbors = [
                n for n in full_neighbors
                if 1 <= n.row <= rows and 1 <= n.col <= cols]
            new_table[p] = true_neighbors
    neighbor_tables[dim] = new_table


def init_corner_table(dim):
    rows, cols = dim
    new_table = {}
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            p = Point(row=r, col=c)
            full_corners = [
                Point(row=p.row - 1, col=p.col - 1),
                Point(row=p.row - 1, col=p.col + 1),
                Point(row=p.row + 1, col=p.col - 1),
                Point(row=p.row + 1, col=p.col + 1),
            ]
            true_corners = [
                n for n in full_corners
                if 1 <= n.row <= rows and 1 <= n.col <= cols]
            new_table[p] = true_corners
    corner_tables[dim] = new_table


class IllegalMoveError(Exception):
    pass


class GoString:
    """Stones that are linked by a chain of connected stones of the
    same color.
    """

    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    def remove_liberty(self, point):
        self.liberties.remove(point)

    def add_liberty(self, point):
        self.liberties.add(point)

    def merged_with(self, string):
        """Return a new string containing all stones in both strings."""
        assert string.color == self.color
        combined_stones = self.stones | string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | string.liberties) - combined_stones)

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
               self.color == other.color and \
               self.stones == other.stones and \
               self.liberties == other.liberties

    def __deepcopy__(self, memodict={}):
        return GoString(self.color, self.stones, self.liberties)
        # immutable. Because the constructor use a set function. A set x itself is mutable, but set(x) generate a new
        # object.


class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        self._hash = zobrist.EMPTY_BOARD

        global neighbor_tables
        dim = (num_rows, num_cols)
        if dim not in neighbor_tables:
            init_neighbor_table(dim)
        if dim not in corner_tables:
            init_corner_table(dim)
        self.neighbor_table = neighbor_tables[dim]
        self.corner_table = corner_tables[dim]

    def neighbors(self, point):
        return self.neighbor_table[point]

    def corners(self, point):
        return self.corner_table[point]

    def place_stone(self, player, point):
        assert self.is_on_grid(point)  # make sure it is on grid
        assert self._grid.get(point) is None  # no existing stone on point
        # 0. Examine the adjacent points.
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        for neighbor in self.neighbor_table[point]:
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)
        new_string = GoString(player, [point], liberties)
        # 1. Merge any adjacent strings of the same color.
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string
        # Add filled point hash code.
        self._hash ^= zobrist.HASH_CODE[point, player]

        # 2. Reduce liberties of any adjacent strings of the opposite
        #    color.
        # 3. If any opposite color strings now have zero liberties,
        #    remove them.
        for other_color_string in adjacent_opposite_color:
            other_color_string.remove_liberty(point)
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)

    def _remove_string(self, string):
        for point in string.stones:
            # Removing a string can create liberties for other strings.
            for neighbor in self.neighbor_table[point]:
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    neighbor_string.add_liberty(point)
            self._grid[point] = None
            # Remove filled point hash code.
            self._hash ^= zobrist.HASH_CODE[point, string.color]

    def is_self_capture(self, player, point):
        friendly_strings = []
        for neighbor in self.neighbor_table[point]:
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                # This point has a liberty. Can't be self capture.
                return False
            elif neighbor_string.color == player:
                # Gather for later analysis.
                friendly_strings.append(neighbor_string)
            else:
                if neighbor_string.num_liberties == 1:
                    # This move is real capture, not a self capture.
                    return False
        if all(neighbor.num_liberties == 1 for neighbor in friendly_strings):
            return True
        return False

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
               1 <= point.col <= self.num_cols

    def get(self, point):
        """Return the content of a point on the board.

        Returns None if the point is empty, or a Player if there is a
        stone on that point.
        """
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point):
        """Return the entire string of stones at a point.

        Returns None if the point is empty, or a GoString if there is
        a stone on that point.
        """
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def __eq__(self, other):
        return isinstance(other, Board) and \
               self.num_rows == other.num_rows and \
               self.num_cols == other.num_cols and \
               self._hash() == other._hash()

    def __deepcopy__(self, memodict={}):
        copied = Board(self.num_rows, self.num_cols)
        copied._grid = copy.deepcopy(self._grid)  # deepcopy is needed since string has liberties and stones which are
        # sets and sets are mutable
        copied._hash = self._hash
        return copied

    def zobrist_hash(self):
        return self._hash


class Move:
    """Any action a player can play on a turn.

    Exactly one of is_play, is_pass, is_resign will be set.
    """

    def __init__(self, point=None, is_pass=False, is_resign=False):
        self.is_play = (point is not None)
        assert (self.is_play) ^ is_pass ^ is_resign  # minor known issue: will also return true if 3 of them are
        # true.
        self.point = point
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        """A move that places a stone on the board."""
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        return Move(is_resign=True)

    def __str__(self):
        if self.is_pass:
            return 'pass'
        if self.is_resign:
            return 'resign'
        return '(r %d, c %d)' % (self.point.row, self.point.col)

    def __eq__(self, other):
        return (
                   self.is_play,
                   self.is_pass,
                   self.is_resign,
                   self.point) == (
                   other.is_play,
                   other.is_pass,
                   other.is_resign,
                   other.point)


class GameState:
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player  # <1>
        self.previous_state = previous
        if previous is None:  # todo think if we can reduce this
            self.previous_states = set()
        else:
            self.previous_states = set(
                previous.previous_states |
                {(previous.next_player, previous.board.zobrist_hash())})  # <2>
        self.last_move = move  # <3>

    # <1>: next_player means the current player for current state
    # <2>: save the current player and the board before current player place the stone.
    # <3>: this move is the last move in the previous state.

    def apply_move(self, move):  # <1>
        """Return the new GameState after applying the move."""
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)

    # <1>: code didn't check if this is a valid move before apply move.

    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        return self.board.is_self_capture(player, move.point)

    @property
    def situation(self):
        return (self.next_player, self.board)  # <1>

    # return the current board position and current play (the one that is going to place a stone on current board)

    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())  # <1>
        return next_situation in self.previous_states

    # <1> check if the next player faces the situation where he saw before.

    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return (
                self.board.get(move.point) is None and
                not self.is_move_self_capture(self.next_player, move) and
                not self.does_move_violate_ko(self.next_player, move))

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def legal_moves(self):  # <1>
        if self.is_over():
            return []
        moves = []
        for row in range(1, self.board.num_rows + 1):
            for col in range(1, self.board.num_cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        # These two moves are always legal.
        moves.append(Move.pass_turn())
        moves.append(Move.resign())

        return moves

    # <1> this function will loop all the point, and it is expensive to call it frequently.

    def winner(self):
        if not self.is_over():
            return None
        if self.last_move.is_resign:
            return self.next_player
        game_result = compute_game_result(self)
        return game_result.winner
