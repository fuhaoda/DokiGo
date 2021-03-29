import argparse
from multiprocessing import Process, Queue, cpu_count
from dokigo import goboardv2 as goboard
from dokigo.agent import mcts
import os
from dokigo.sgfio import sgf, adaptor


def worker(args, pid):

    board_size = args.board_size
    rounds = args.rounds
    max_moves = args.max_moves
    temperature = args.temperature

    for i in range(args.num_games):
        print('Process %d: Generating game %d/%d...' % (pid, i + 1, args.num_games))

        game = goboard.GameState.new_game(board_size)
        bot = mcts.MCTSAgent(rounds, temperature)
        num_moves = 0

        sgfgame = sgf.Sgf_game(board_size)  # recorder
        sgf_info = adaptor.DokiGo_to_SGF()  # adaptor

        while not game.is_over():
            # print_board(game.board)
            move = bot.select_move(game)
            # print_move(game.next_player, move)

            node = sgfgame.extend_main_sequence()
            sgf_info.set_move(game.next_player, move)  # recorder get info
            node.set_move(sgf_info.move_color, sgf_info.move_coordinates)  # set node

            game = game.apply_move(move)
            num_moves += 1
            if num_moves > max_moves:
                break

        sgf_info.set_game_result(game, sgfgame)  # set game result

        with open(f"./selfplay_data/process{pid}_game{i}_rounds{rounds}.sgf", "wb") as f:  # write into a file
            f.write(sgfgame.serialise())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', '-b', type=int, default=9)
    parser.add_argument('--rounds', '-r', type=int, default=3)
    parser.add_argument('--temperature', '-t', type=float, default=0.8)
    parser.add_argument('--max-moves', '-m', type=int, default=60,
                        help='Max moves per game.')
    parser.add_argument('--num-games', '-n', type=int, default=20)
    parser.add_argument('--cpu-cores', '-c', type=int, default=-1)

    args = parser.parse_args()  # <1>

    if args.cpu_cores == -1:
        args.cpu_cores = cpu_count()

    if not os.path.exists('selfplay_data'):
        os.makedirs('selfplay_data')

    processes = []

    for pid in range(args.cpu_cores):
        p = Process(target=worker, args=(args, pid))
        p.start()
        processes.append(p)

    for process in processes:
        process.join()


if __name__ == '__main__':
    main()
