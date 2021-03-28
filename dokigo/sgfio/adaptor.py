"""adaptor from dokigo to the sgfio"""

from dokigo.base import Player
from dokigo.scoring import compute_game_result


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
