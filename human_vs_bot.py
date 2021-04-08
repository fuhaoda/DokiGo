from dokigo.agent.mcts import MCTSAgent
from dokigo.agent.predict import DeepLearningAgent

from dokigo import goboard
from dokigo import base
from dokigo.utilities import print_board,print_move,point_from_coords, load_nn_model
import random

from dokigo.sgfio import sgf, adaptor

import os

def main():
    board_size = 9
    game = goboard.GameState.new_game(board_size)
    #bot = RandomBot()
    #bot = MCTSAgent(100,1.5)
    model, encoder = load_nn_model("dokigo/DL_policy_prediction_MCTS/mcts_r50k.h5")
    bot = DeepLearningAgent(model, encoder)
    human_player = random.choice(list(base.Player))
    print("Game Start! You will play: %s and AI will play: %s" % (human_player.name, human_player.other.name))

    sgfgame = sgf.Sgf_game(board_size)  # recorder
    sgf_info = adaptor.DokiGo_to_SGF()  # adaptor


    while not game.is_over():
        print(chr(27)+"[2J")
        print_board(game.board)

        if game.next_player == human_player:
            while True:
                human_move = input('-- ')
                if human_move == 'pass':
                    move = goboard.Move.pass_turn()
                    break
                elif human_move == 'resign':
                    move = goboard.Move.resign()
                    break
                else:
                    point = point_from_coords(human_move.replace(' ', ''))
                    move = goboard.Move.play(point)
                    if game.board.is_on_grid(move.point) and game.is_valid_move(move):
                        break
                print("This is not a value move!")
        else:
            move = bot.select_move(game)
        print_move(game.next_player,move)
        game = game.apply_move(move)

        node = sgfgame.extend_main_sequence()
        sgf_info.set_move(game.next_player, move)  # recorder get info
        node.set_move(sgf_info.move_color, sgf_info.move_coordinates)  # set node



    sgf_info.set_game_result(game, sgfgame)  # set game result
    with open(f"game_human_vs_bot.sgf", "wb") as f:  # write into a file
        f.write(sgfgame.serialise())

if __name__ == '__main__':
    main()



#bug 1
#todo: black can move in white eye
#todo: check human input a valid move