from dokigo.base import Point, Player
from dokigo.encoders.base import get_encoder_by_name
from dokigo import goboardv3 as goboard
import numpy as np


class Generator:
    def __init__(self, encoder_name):
        self.winner = None
        self.board_size = None
        self.encoder = None
        self.game = None
        self.boards = None
        self.moves = None
        self.data = None
        self.encoder_name = encoder_name

    def set_move(self, sgf_move):
        raise NotImplementedError

    def set_winner(self, winner):
        raise NotImplementedError

    def new_game(self, board_size):
        raise NotImplementedError

    def return_data(self):
        raise NotImplementedError

    def _player(self, sgf_player):
        if sgf_player == 'b':
            return Player.black
        elif sgf_player == 'w':
            return Player.white
        else:
            self.winner = None

    def _point(self, sgf_point):
        return Point(row=sgf_point[0] + 1, col=sgf_point[1] + 1)


class SupervisedLearningDataGenerator(Generator):
    def __init__(self, encoder_name):
        super().__init__(encoder_name)

    def set_winner(self, winner):
        return self._player(winner)

    def new_game(self, board_size):  # <1>
        self.board_size = (board_size, board_size)
        self.encoder = get_encoder_by_name(self.encoder_name, self.board_size)
        self.game = goboard.GameState.new_game(board_size)
        self.boards = []
        self.moves = []

    # <1> need to call the new_game function first to generate a new game.

    def set_move(self, sgf_move):
        color, location = sgf_move
        # todo conduct unit test for the following codes including pass,
        # also when we finish one game, we need to clean the data.
        self.boards.append(self.encoder.encode(self.game))
        move_one_hot = np.zeros(self.encoder.num_points())
        move = goboard.Move(point=self._point(location))
        move_one_hot[self.encoder.encode_point(move.point)] = 1
        self.moves.append(move_one_hot)
        self.game.next_player = self._player(color)
        self.game.apply_move(move)

    def return_data(self):
        return self.boards, self.moves
