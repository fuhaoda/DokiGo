from dokigo import goboardv1 as goboard
from dokigo import base
from dokigo.utilities import print_board,print_move,point_from_coords
import random

def main():
    board_size = 9
    game = goboard.GameState.new_game(board_size)

    you_color = random.choice(list(base.Player))
    print("Game Start! You will play: %s and your opponent will play: %s" % (you_color.name, you_color.other.name))

    while not game.is_over():
        print(chr(27)+"[2J")
        print_board(game.board)

        if game.next_player == you_color:
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
        print_move(game.next_player,move)
        game = game.apply_move(move)

if __name__ == '__main__':
    main()



#bug 1
#todo: black can move in white eye
#todo: check human input a valid move