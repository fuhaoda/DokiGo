from dokigo.agent.naive import RandomBot
from dokigo.agent.mcts import MCTSAgent
from dokigo import goboardv1 as goboard
from dokigo import base
from dokigo.utilities import print_board,print_move,point_from_coords
import random



def main():
    board_size = 9
    total_games = 100
    strong_bot_wins = 0
    for m in range(total_games):

        game = goboard.GameState.new_game(board_size)
        bot_1 = RandomBot()
        bot_2 = MCTSAgent(100, 1.5)
        bot_1_color = random.choice(list(base.Player))
        bot_2_color = bot_1_color.other

        while not game.is_over():
            # print(chr(27) + "[2J")
            # print_board(game.board)

            if game.next_player == bot_1_color:
                move = bot_1.select_move(game)
            else:
                move = bot_2.select_move(game)
            #print_move(game.next_player, move)
            print("we are in game #:", m+1)
            print("The advanced algorithm win #", strong_bot_wins)
            game = game.apply_move(move)

        if game.winner() == bot_2_color:
            strong_bot_wins += 1

    print("The winning rate is %.3f"%(strong_bot_wins/total_games))

if __name__ == '__main__':
    main()
