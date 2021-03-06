import unittest
from dokigo.base import Point
from dokigo.sgfio.data_generator import SupervisedLearningDataGenerator
from dokigo.encoders.base import get_encoder_by_name
from dokigo.sgfio import sgf
import numpy as np
from dokigo.utilities import print_board,print_move,point_from_coords
from dokigo.sgfio.adaptor import SGF_to_DokiGo

from dokigo import goboard

class TestSGFIO(unittest.TestCase):
    def test_generator(self):

        encoder_name = 'oneplane'
        generator = SupervisedLearningDataGenerator(encoder_name)

        with open('test_data/game1.sgf', "rb") as f:
            game = sgf.Sgf_game.from_bytes(f.read())

        board_size = game.get_size()
        generator.new_game(board_size)

        main_sequence = game.get_main_sequence()
        node = main_sequence[1]

        generator.set_move(node.get_move())
        X, y = generator.return_data()

        encoder = get_encoder_by_name(encoder_name, board_size)
        expected_X = np.zeros((encoder.num_planes,board_size,board_size))

        expected_y = np.zeros(encoder.num_points())
        expected_y[encoder.encode_point(Point(6,6))] = 1 #B[fd] = Point (6,6)
        self.assertEqual(X[0].tolist(),expected_X.tolist())
        self.assertEqual(y[0].tolist(), expected_y.tolist())

        #todo: develop unit test for X[1], and X[2]
        node = main_sequence[2]
        generator.set_move(node.get_move())


        node = main_sequence[3]
        generator.set_move(node.get_move())
        X, y = generator.return_data()



    def test_adaptor_sgf_2_dokigo(self):
        encoder_name = 'oneplane'
        generator = SupervisedLearningDataGenerator(encoder_name)
        sgf_data_retriever = SGF_to_DokiGo("test_data",generator)
        X, y = sgf_data_retriever.parse_one_episod('game1.sgf')
        self.assertTrue(isinstance(X,np.ndarray))
        self.assertTrue(isinstance(y,np.ndarray))
        self.assertEqual(X.shape, (61,1,9,9))
        self.assertEqual(y.shape, (61,81))


class TestGoBoard(unittest.TestCase):

    def test_ko(self):
        board_size = 9
        game = goboard.GameState.new_game(board_size)
        single_ko_moves = ['A2','A3','C2','C3','B1','B4','B3','B2']
        the_single_ko_move = 'B3'
        for item in single_ko_moves:
            point = point_from_coords(item.replace(' ', ''))
            move = goboard.Move.play(point)
            self.assertTrue(game.is_valid_move(move))
            game = game.apply_move(move)

        # print_board(game.board)
        # the above code can visualize the ko situation
        point = point_from_coords(the_single_ko_move.replace(' ', ''))
        move = goboard.Move.play(point)
        self.assertFalse(game.is_valid_move(move))
        self.assertTrue(game.does_move_violate_ko(game.next_player,move))

        circular_ko_moves = ['G2','G3','J2','J3','H1','H4','H3','A7','A8','C7','C8','B6','B9','B8','B7','H2','B3',
                             'B8','H3']
        for item in circular_ko_moves:
            point = point_from_coords(item.replace(' ', ''))
            move = goboard.Move.play(point)
            self.assertTrue(game.is_valid_move(move))
            game = game.apply_move(move)

        the_circular_ko_moves = 'B2'
        point = point_from_coords(the_circular_ko_moves.replace(' ', ''))
        move = goboard.Move.play(point)
        self.assertFalse(game.is_valid_move(move))
        self.assertTrue(game.does_move_violate_ko(game.next_player, move))

        # print_board(game.board)
        # the above code can visualize the ko situation


if __name__ == '__main__':
    unittest.main()
