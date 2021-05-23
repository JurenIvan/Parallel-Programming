import unittest

from lab2 import Board, Slave, Master
from lab2 import NUM_OF_COLS

from lab2 import NUM_OF_ROWS


class TestStringMethods(unittest.TestCase):

    def test_horizontal1(self):
        board = Board(' ' * (NUM_OF_ROWS * NUM_OF_COLS))

        board.move(0, 'o')
        board.move(1, 'o')
        board.move(2, 'o')
        board.move(3, 'x')
        board.move(4, 'o')
        board.move(5, 'o')
        board.move(6, 'o')

        board.move(0, 'x')
        board.move(1, 'x')
        board.move(2, 'x')
        board.move(3, 'x')

        self.assertTrue(board.game_end(0))
        self.assertTrue(board.game_end(1))
        self.assertTrue(board.game_end(2))
        self.assertTrue(board.game_end(3))
        self.assertFalse(board.game_end(4))
        self.assertFalse(board.game_end(5))
        self.assertFalse(board.game_end(6))

    def test_horizontal2(self):
        board = Board(' ' * (NUM_OF_ROWS * NUM_OF_COLS))

        board.move(0, 'o')
        board.move(1, 'o')
        board.move(2, 'o')
        board.move(3, 'x')
        board.move(4, 'o')
        board.move(5, 'o')
        board.move(6, 'o')

        board.move(3, 'x')
        board.move(4, 'x')
        board.move(5, 'x')
        board.move(6, 'x')

        self.assertTrue(board.game_end(6))
        self.assertTrue(board.game_end(5))
        self.assertTrue(board.game_end(4))
        self.assertTrue(board.game_end(3))
        self.assertFalse(board.game_end(2))
        self.assertFalse(board.game_end(1))
        self.assertFalse(board.game_end(0))

    def test_horizontal3(self):
        board = Board(' ' * (NUM_OF_ROWS * NUM_OF_COLS))

        board.move(3, 'x')
        board.move(4, 'x')
        board.move(5, 'x')
        board.move(6, 'x')

        self.assertTrue(board.game_end(6))
        self.assertTrue(board.game_end(5))
        self.assertTrue(board.game_end(4))
        self.assertTrue(board.game_end(3))

    def test_vertical(self):
        board = Board(' ' * (NUM_OF_ROWS * NUM_OF_COLS))

        board.move(0, 'x')
        board.move(0, 'x')
        board.move(0, 'x')
        board.move(0, 'x')
        board.move(1, 'o')

        self.assertTrue(board.game_end(0))
        self.assertFalse(board.game_end(1))

    def test_diagonal1(self):
        board = Board(' ' * (NUM_OF_ROWS * NUM_OF_COLS))

        for i in range(4):
            for j in range(0, i):
                board.move(i, 'o')

        board.move(0, 'x')
        board.move(1, 'x')
        board.move(2, 'x')
        board.move(3, 'x')

        board.move(4, 'x')
        board.move(5, 'o')
        board.move(6, 'o')

        self.assertFalse(board.game_end(4))
        self.assertFalse(board.game_end(5))
        self.assertFalse(board.game_end(6))
        self.assertTrue(board.game_end(0))
        self.assertTrue(board.game_end(1))
        self.assertTrue(board.game_end(2))
        self.assertTrue(board.game_end(3))

    def test_diagonal2(self):
        board = Board(' ' * (NUM_OF_ROWS * NUM_OF_COLS))

        for i in range(4):
            for j in range(0, i):
                board.move(j, 'o')

        board.move(0, 'x')
        board.move(1, 'x')
        board.move(2, 'x')
        board.move(3, 'x')

        board.move(4, 'x')
        board.move(5, 'o')
        board.move(6, 'o')

        self.assertFalse(board.game_end(4))
        self.assertFalse(board.game_end(5))
        self.assertFalse(board.game_end(6))
        self.assertTrue(board.game_end(0))
        self.assertTrue(board.game_end(1))
        self.assertTrue(board.game_end(2))
        self.assertTrue(board.game_end(3))

    def test_move_legal(self):
        board = Board(' ' * (NUM_OF_ROWS * NUM_OF_COLS))

        self.assertTrue(board.move_legal(0))

        for i in range(NUM_OF_ROWS):
            self.assertTrue(board.move_legal(0))
            board.move(0, 'x')

        self.assertFalse(board.move_legal(0))

    def test_slave_deserializeMessage(self):
        slave = Slave(None)

        message = ' ' * 42 + 'x' + '20,31'

        board, player, last_col, depth = slave.deserialize_message(message)

        self.assertEqual(board.serialize(), ' ' * 42)
        self.assertEqual(player, 'x')
        self.assertEqual(last_col, 20)
        self.assertEqual(depth, 31)

    def test_master_serializeMessage(self):
        master = Master(None, 10)

        board_state = ' ' * 20 + 'x' + ' ' * 21

        message = master.serialize_message(Board(board_state), 'x', 17, 20)

        self.assertEqual(message, board_state + 'x17,20')

    def test_generate_tasks(self):
        master = Master(None, 10)

        sol = master.generate_tasks()

        self.assertEqual(len(sol), 49)

    def test_dict(self):

        dict1 = {'a': 1}
        dict2 = dict1.copy()
        self.assertEqual(len(dict1), 1)
        self.assertEqual(len(dict2), 1)
        dict1.popitem()
        self.assertEqual(len(dict1), 0)
        self.assertEqual(len(dict2), 1)

    def test_resolve_best_move(self):

        master = Master(None, 0, Board(' ' * 42))

        results = {(1, 0): 0.1,
                   (1, 1): -0.1,
                   (1, 2): 0.2,
                   (1, 3): -0.3,
                   (1, 4): 0.4,

                   (2, 0): 0.1,
                   (2, 1): -0.1,
                   (2, 2): 0.2,
                   (2, 3): -0.2,
                   (2, 4): 0.4,

                   (3, 0): 0.1,
                   (3, 1): -0.1,
                   (3, 2): 0.2,
                   (3, 3): -0.4,
                   (3, 4): 0.4}

        best_move = master.resolve_best_move(results)

        self.assertEqual(best_move, 2)

    def test_weird_bug(self):
        board_state = 'ooxxxx o xxxo o      xx     o      o      o      '
        board = Board(board_state)
        board.print()
        board.move(1, 'x')
        board.print()
        self.assertEqual(True, board.game_end(1))


# computer chose 1
# 5 o
# 4 o
# 3 o
# 2 xx o
# 1 oxxxxo
# 0 ooxxxx
#   0123456