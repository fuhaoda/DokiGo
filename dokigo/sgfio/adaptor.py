"""adaptor from dokigo to the sgfio"""

from dokigo.base import Player
from dokigo.scoring import compute_game_result
import os
from dokigo.sgfio import sgf
import numpy as np

class DokiGo_to_SGF:
    def __init__(self):
        self.player = None
        self._move = None

    def set_move(self, player, move):
        self.player = player
        self.move = move

    @property
    def move_color(self):
        if self.player == Player.black:
            return 'b'
        elif self.player == Player.white:
            return 'w'
        else:
            return None

    @property
    def move_coordinates(self):
        if self.move.is_play:
            return (self.move.point.row - 1, self.move.point.col - 1)
        else:
            return None

    def set_game_result(self, game_state, sgf_game):

        if not game_state.is_over():
            return None

        root_node = sgf_game.get_root()
        if game_state.last_move.is_resign:
            if game_state.next_player == Player.black:
                root_node.set("RE", "B+R")
                return
            else:
                root_node.set("RE", "W+R")
                return
        root_node.set("RE", str(compute_game_result(game_state)))


class SGF_to_DokiGo:
    def __init__(self, file_path, data_generator):
        self.file_path = file_path
        self.generator = data_generator
        self.total_episods = 0
        self.sgf_files = []
        self._count_episods()

    def _count_episods(self):
        if not os.path.exists(self.file_path):
            print(f"There is no directory under name {self.file_path}")
            return None
        self.sgf_files = os.listdir(self.file_path)
        for file in self.sgf_files:
            if file.split(".")[-1] != "sgf":
                self.sgf_files.remove(file)
        self.total_episods = len(self.sgf_files)

    def parse_one_episod(self, sgf_file):
        file_location = os.path.join(self.file_path, sgf_file)
        if not os.path.exists(file_location):
            print(f"There is no SGF file as {file_location}")
            return None

        with open(file_location, "rb") as f:
            game = sgf.Sgf_game.from_bytes(f.read())



        board_size = game.get_size()
        self.generator.new_game(board_size)

        winner = game.get_winner()
        self.generator.set_winner(winner)

        main_sequence = game.get_main_sequence()

        if len(main_sequence) == 0:
            return None

        for node in main_sequence[1:]:
            self.generator.set_move(node.get_move())

        return self.generator.return_data()

    def parse_episods(self, size=None):
        Xt = []
        yt = []

        for file in self.sgf_files:
            X, y = self.parse_one_episod(file)
            Xt.append(X)
            yt.append(y)

        X = np.concatenate(Xt)
        y = np.concatenate(yt)

        return X,y


