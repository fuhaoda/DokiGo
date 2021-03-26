import argparse
import numpy as np
from multiprocessing import Process, Queue

from dokigo.encoders.base import get_encoder_by_name
from dokigo import goboardv2 as goboard
from dokigo.agent import mcts
from dokigo.utilities import print_board, print_move

def generate_game(board_size, rounds, max_moves, tempature):
    boards, moves = [],[]
    encoder = get_encoder_by_name('oneplane',board_size)
    game = goboard.GameState.new_game(board_size)
    bot = mcts.MCTSAgent(rounds, tempature)

    num_moves = 0
    while not game.is_over():
        #print_board(game.board)
        move = bot.select_move(game)
        if move.is_play:
            boards.append(encoder.encode(game))
            move_one_hot = np.zeros(encoder.num_points())
            move_one_hot[encoder.encode_point(move.point)] = 1
            moves.append(move_one_hot)

        #print_move(game.next_player, move)
        game = game.apply_move(move)
        num_moves +=1
        if num_moves > max_moves:
            break
    return np.array(boards), np.array(moves)

def worker(q, args,pid):
    xs = []
    ys = []

    for i in range(args.num_games):
        print('Process %d: Generating game %d/%d...' % (pid, i + 1, args.num_games))
        x, y = generate_game(args.board_size, args.rounds, args.max_moves, args.temperature)  # <2>
        xs.append(x)
        ys.append(y)

    x = np.concatenate(xs)
    y = np.concatenate(ys)
    q.put([x,y])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', '-b', type=int, default=9)
    parser.add_argument('--rounds', '-r', type=int, default=2)
    parser.add_argument('--temperature', '-t', type=float, default=0.8)
    parser.add_argument('--max-moves', '-m', type=int, default=60,
                        help='Max moves per game.')
    parser.add_argument('--num-games', '-n', type=int, default=2)
    parser.add_argument('--cpu-cores', '-c', type=int, default=4)
    parser.add_argument('--board-out')
    parser.add_argument('--move-out')

    args = parser.parse_args()  # <1>

    q = Queue()
    processes =[]

    for pid in range(args.cpu_cores):
        p = Process(target=worker, args=(q,args,pid))
        p.start()
        processes.append(p)



    x = []
    y = []
    for _ in range(args.cpu_cores):
        xt, yt = q.get()
        x.append(xt)
        y.append(yt)

    for process in processes:
        process.join()

    np.save(args.board_out, np.concatenate(x))
    np.save(args.move_out, np.concatenate(y))


if __name__ == '__main__':
    main()