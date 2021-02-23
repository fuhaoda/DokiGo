import enum
import copy
import random
from collections import namedtuple


class Player(enum.Enum):
    x = 1
    o = 2

    @property
    def other(self):
        return Player.x if self == Player.o else Player.o


class Point(namedtuple('Point', ['row', 'col'])):
    def __deepcopy__(self, memodict={}):
        # these are immutable so we just return self.
        return self


BOARD_SIZE = 3
ROWS = tuple(range(1, BOARD_SIZE + 1))
COLS = tuple(range(1, BOARD_SIZE + 1))
DIAG_1 = (Point(1, 1), Point(2, 2), Point(3, 3))
DIAG_2 = (Point(1, 3), Point(2, 2), Point(3, 1))
COL_NAMES = 'ABC'


class Board:
    def __init__(self):
        self._grid = {}

    def place(self, player, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None
        self._grid[point] = player

    @staticmethod
    def is_on_grid(point):
        return 1 <= point.row <= BOARD_SIZE and 1 <= point.col <= BOARD_SIZE

    def get(self, point):
        # Return the content on the board, and return None if the point is empty
        return self._grid.get(point)


class Move:
    def __init__(self, point):
        self.point = point


class GameState:
    def __init__(self, board, next_player, move):
        self.board = board
        self.next_player = next_player
        self.last_move = move

    def apply_move(self, move):
        next_board = copy.deepcopy(self.board)
        next_board.place(self.next_player, move.point)
        return GameState(next_board, self.next_player.other, move)

    @classmethod
    def new_game(cls):
        board = Board()
        return GameState(board, Player.x, None)

    def is_valid_move(self, move):
        return Board.is_on_grid(move.point) and self.board.get(move.point) is None and not self.is_over()

    def legal_moves(self):
        moves = []
        for row in ROWS:
            for col in COLS:
                move = Move(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        return moves

    def is_over(self):
        if self._has_3_in_a_row(Player.x):
            return True
        if self._has_3_in_a_row(Player.o):
            return True
        if all(self.board.get(Point(row, col)) is not None for row in ROWS for col in COLS):
            return True
        return False

    def _has_3_in_a_row(self, player):
        for col in COLS:
            if all(self.board.get(Point(row, col)) == player for row in ROWS):
                return True
        for row in ROWS:
            if all(self.board.get(Point(row, col)) == player for col in COLS):
                return True
        if all(self.board.get(point) == player for point in DIAG_1) or all(
                self.board.get(point) == player for point in DIAG_2):
            return True
        return False

    def winner(self):
        if self._has_3_in_a_row(Player.x):
            return Player.x
        if self._has_3_in_a_row(Player.o):
            return Player.o
        return None


class GameResult(enum.Enum):
    loss = 1
    draw = 2
    win = 3


def reverse_game_result(game_result):
    if game_result == GameResult.loss:
        return game_result.win
    elif game_result == GameResult.win:
        return game_result.loss
    else:
        return GameResult.draw


def best_result(game_state):
    if game_state.is_over():
        if game_state.winner() == game_state.next_player:
            return GameResult.win
        elif game_state.winner() is None:
            return GameResult.draw
        else:
            return GameResult.loss
    best_result_so_far = GameResult.loss
    for candidate_move in game_state.legal_moves():
        next_state = game_state.apply_move(candidate_move)
        opponent_best_result = best_result(next_state)
        our_result = reverse_game_result(opponent_best_result)
        if our_result.value > best_result_so_far.value:
            best_result_so_far = our_result
    return best_result_so_far


class MinimaxAgent:
    def select_move(self, game_state):
        winning_moves = []
        draw_moves = []
        losing_moves = []

        for possible_move in game_state.legal_moves():
            next_state = game_state.apply_move(possible_move)
            opponent_best_outcome = best_result(next_state)
            our_best_outcome = reverse_game_result(opponent_best_outcome)
            if our_best_outcome == GameResult.win:
                winning_moves.append(possible_move)
            elif our_best_outcome == GameResult.draw:
                draw_moves.append(possible_move)
            else:
                losing_moves.append(possible_move)
        if winning_moves:
            return random.choice(winning_moves)
        if draw_moves:
            return random.choice(draw_moves)
        return random.choice(losing_moves)


def print_board(board):
    print('   A   B   C')
    for row in (1, 2, 3):
        pieces = []
        for col in (1, 2, 3):
            piece = board.get(Point(row, col))
            if piece == Player.x:
                pieces.append('X')
            elif piece == Player.o:
                pieces.append('O')
            else:
                pieces.append(' ')
        print('%d  %s' % (row, ' | '.join(pieces)))


def point_from_coords(text):
    col_name = text[0]
    row = int(text[1])
    return Point(row, COL_NAMES.index(col_name) + 1)


def main():
    game = GameState.new_game()

    human_player = random.choice(list(Player))
    print("Game Start! You will play: %s and AI will play %s" % (human_player.name, human_player.other.name))
    bot = MinimaxAgent()

    while not game.is_over():
        print_board(game.board)
        if game.next_player == human_player:
            while True:
                human_move = input('-- ')
                point = point_from_coords(human_move.strip())
                move = Move(point)
                if game.is_valid_move(move):
                    break
                print("It is not a valid move")
        else:
            print("Computer is thinking ...")
            move = bot.select_move(game)
        game = game.apply_move(move)

    print_board(game.board)
    winner = game.winner()
    if winner is None:
        print("It is a draw")
    elif winner == human_player:
        print("Winner is: " + 'YOU!!!')
    else:
        print("Winner is AI!")


if __name__ == '__main__':
    main()
