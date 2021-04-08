import numpy as np

from dokigo.agent.base import Agent
from dokigo.agent.utilities import is_point_an_eye
from dokigo import encoders
from dokigo import goboard
from dokigo import utilities

__all__ = [
    'DeepLearningAgent',
]


class DeepLearningAgent(Agent):
    def __init__(self, model, encoder):
        super().__init__()
        self.model = model
        self.encoder = encoder

    def predict(self, game_state):
        encoded_state = self.encoder.encode(game_state)
        input_tensor = np.array([encoded_state])
        return self.model.predict(input_tensor.reshape(-1,9,9,1))[0] #todo check dimension and reshape operation rule

    def select_move(self, game_state):
        num_moves = self.encoder.board_width * self.encoder.board_height
        move_probs = self.predict(game_state)
        move_probs = move_probs ** 3  # <1>
        eps = 1e-6
        move_probs = np.clip(move_probs, eps, 1 - eps)  # <2>
        move_probs = move_probs / np.sum(move_probs)  # <3>
        # <1> Increase the distance between the move likely and least likely moves.
        # <2> Prevent move probs from getting stuck at 0 or 1
        # <3> Re-normalize to get another probability distribution.
        candidates = np.arange(num_moves)  # <1>
        ranked_moves = np.random.choice(
            candidates, num_moves, replace=False, p=move_probs)  # <2>
        for point_idx in ranked_moves:
            point = self.encoder.decode_point_index(point_idx)
            if game_state.is_valid_move(goboard.Move.play(point)) and \
                    not is_point_an_eye(game_state.board, point, game_state.next_player):  # <3>
                return goboard.Move.play(point)
        return goboard.Move.pass_turn()  # <4>

    # <1> Turn the probabilities into a ranked list of moves.
    # <2> Sample potential candidates
    # <3> Starting from the top, find a valid move that doesn't reduce eye-space.
    # <4> If no legal and non-self-destructive moves are left, pass.


