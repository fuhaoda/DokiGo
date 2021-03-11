import random
from dokigo.agent.base import Agent
from dokigo.goboardv1 import Move #todo: make the Move do not dependent on goboard
from dokigo.base import Point
from dokigo.agent.utilities import is_point_an_eye

__all__ = ['RandomBot']


class RandomBot(Agent):
    def select_move(self, game_state):
        candidates = []
        for r in range(1, game_state.board.num_rows + 1):
            for c in range(1, game_state.board.num_cols + 1):
                candidate = Point(row=r, col=c)
                if game_state.is_valid_move(Move.play(candidate)) and not is_point_an_eye(game_state.board, candidate,
                                                                                          game_state.next_player):
                    candidates.append(candidate)
        if not candidates:
            return Move.pass_turn()

        return Move.play(random.choice(candidates))
