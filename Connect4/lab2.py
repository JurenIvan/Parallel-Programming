import mpi4py
from mpi4py import MPI
import time

# naredba za pokretanje:
# mpiexec -n 3 python lab2.py

# "x" -> cpu, "o" -> human, " "->empty


HUMAN = 'P'
COMPUTER = 'C'
BLANK = '='

EMPTY_BOARD = BLANK * 42
NUM_OF_ROWS = 6
NUM_OF_COLS = 7

DEATH_PILL = 'DIE'
DEPTH = 8


class Board:

    def __init__(self, state_str: str):
        self.state = state_str

    def state_at(self, col: int, row: int) -> str:
        return self.state[row * NUM_OF_COLS + col]

    def set(self, col: int, row: int, player: str) -> None:
        self.state = self.state[:row * NUM_OF_COLS + col] + player + self.state[row * NUM_OF_COLS + col + 1:]

    def serialize(self) -> str:
        return self.state

    def topmost(self, col: int) -> int:
        for row in range(NUM_OF_ROWS - 1, -1, -1):
            if self.state_at(col, row) != BLANK:
                return row
        return -1

    def move(self, col: int, player: str) -> None:
        self.set(col, self.topmost(col) + 1, player)

    def undo_move(self, col: int) -> None:
        self.set(col, self.topmost(col), BLANK)

    def print(self) -> None:
        for row in range(NUM_OF_ROWS - 1, -1, -1):
            print(str(row), self.state[row * NUM_OF_COLS:(row + 1) * NUM_OF_COLS])
        print('  ', end='')
        for x in range(NUM_OF_COLS):
            print(x, end='')
        print()

    def print_ugly(self) -> None:
        for row in range(NUM_OF_ROWS - 1, -1, -1):
            print(self.state[row * NUM_OF_COLS:(row + 1) * NUM_OF_COLS])

    def game_end(self, col: int) -> bool:
        row = self.topmost(col)
        of_interest = self.state_at(col, row)
        return self.check_horizontal(col, row, of_interest) or \
               self.check_vertical(col, row, of_interest) or \
               self.check_diagonal_positive(col, row, of_interest) or \
               self.check_diagonal_negative(col, row, of_interest)

    def check_horizontal(self, col: int, row: int, of_interest: str) -> bool:
        left: int = 0
        right: int = 0
        # left
        for i in range(1, 4):
            if col - i >= 0 and self.state_at(col - i, row) == of_interest:
                left += 1
            else:
                break

        # right
        for i in range(1, 4):
            if col + i < NUM_OF_COLS and self.state_at(col + i, row) == of_interest:
                right += 1
            else:
                break

        return (left + right) >= 3

    def check_vertical(self, col: int, row: int, of_interest: str) -> bool:
        down: int = 0
        up: int = 0
        # down
        for i in range(1, 4):
            if row - i >= 0 and self.state_at(col, row - i) == of_interest:
                down += 1
            else:
                break

        # up
        for i in range(1, 4):
            if row + i < NUM_OF_ROWS and self.state_at(col, row + i) == of_interest:
                up += 1
            else:
                break

        return (down + up) >= 3

    def check_diagonal_positive(self, col: int, row: int, of_interest: str) -> bool:
        left: int = 0
        right: int = 0
        # left
        for i in range(1, 4):
            if col - i >= 0 and row - i >= 0 and self.state_at(col - i, row - i) == of_interest:
                left += 1
            else:
                break

        # right
        for i in range(1, 4):
            if col + i < NUM_OF_COLS and row + i < NUM_OF_ROWS and self.state_at(col + i,
                                                                                 row + i) == of_interest:
                right += 1
            else:
                break

        return (left + right) >= 3

    def check_diagonal_negative(self, col: int, row: int, of_interest: str) -> bool:
        left: int = 0
        right: int = 0
        # left
        for i in range(1, 4):
            if col - i >= 0 and row + i < NUM_OF_ROWS and self.state_at(col - i, row + i) == of_interest:
                left += 1
            else:
                break

        # right
        for i in range(1, 4):
            if col + i < NUM_OF_COLS and row - i >= 0 and self.state_at(col + i, row - i) == of_interest:
                right += 1
            else:
                break

        return (left + right) >= 3

    def move_legal(self, col: int) -> bool:
        return self.topmost(col) + 1 < NUM_OF_ROWS

    def evaluate(self, player: str, last_col: int, depth: int) -> float:
        if self.game_end(last_col):
            return 1 if player == COMPUTER else -1

        if depth == 0:
            return 0

        depth -= 1
        if player == COMPUTER:
            new_player = HUMAN
        else:
            new_player = COMPUTER

        b_all_lose = True
        b_all_win = True
        d_total = 0
        i_moves = 0

        for col in range(NUM_OF_COLS):
            if self.move_legal(col):
                i_moves += 1
                self.move(col, new_player)
                d_result = self.evaluate(new_player, col, depth)
                self.undo_move(col)
                if d_result > -1:
                    b_all_lose = False
                if d_result != 1:
                    b_all_win = False
                if d_result == 1 and new_player == COMPUTER:
                    return 1
                if d_result == -1 and new_player == HUMAN:
                    return -1
                d_total += d_result

        if b_all_win:
            return 1
        if b_all_lose:
            return -1
        return d_total / i_moves


class Master:
    def __init__(self, comm: mpi4py.MPI.Intracomm, number_of_processes: int, board: Board = Board(EMPTY_BOARD)):
        self.comm = comm
        self.number_of_processes = number_of_processes
        self.board = board

    def do(self) -> None:
        # print("Current game state")
        # self.board.print()
        while True:
            # col = int(input('Enter col (1-7) or -1 for exit:'))
            col = int(input(''))
            if col == -1:
                print("Computer Wins!")
                break
            self.board.move(col, HUMAN)
            # self.board.print()
            result = self.board.game_end(col)
            if result:
                print("Human Wins!")
                break
            # time_start = time.time()
            col = self.calculate_computer_move()
            # time_end = time.time()
            # print(time_end-time_start)
            self.board.move(col, COMPUTER)
            self.board.print_ugly()
            result = self.board.game_end(col)
            if result:
                print("Computer Wins!")
                break
        self.kill_slaves()

    def calculate_computer_move(self) -> int:
        tasks: dict = self.generate_tasks()
        tasks_copy: dict = tasks.copy()
        results: dict = {}
        if len(tasks) == 1:
            return tasks.popitem()[1]

        # distribute
        curr_worker = 1
        while curr_worker < self.number_of_processes and len(tasks_copy) != 0:
            (task_state, path) = tasks_copy.popitem()
            message = self.serialize_message(task_state, HUMAN, path[1], 6)
            self.comm.send(message, dest=curr_worker)
            curr_worker += 1

        while len(results) != len(tasks):
            for i in range(1, self.number_of_processes):
                if self.comm.iprobe(source=i):
                    message = self.comm.recv(source=i)
                    state, result = self.deserialize_message(message)
                    results[tasks.get(state)] = result
                    # print(str(i), state, str(result), tasks.get(state))
                    if len(tasks_copy) != 0:
                        (task_state, path) = tasks_copy.popitem()
                        message = self.serialize_message(task_state, HUMAN, path[1], DEPTH - 2)
                        self.comm.send(message, dest=i)

        return self.resolve_best_move(results)

    def resolve_best_move(self, results: dict) -> int:
        min_col: dict = {}
        for item in results.items():
            mov1 = item[0][0]
            result = item[1]
            min_col[mov1] = result if min_col.get(mov1) is None else min(min_col.get(mov1), result)

        min_val, min_move = -2, 0
        for item in min_col.items():
            if item[1] > min_val:
                min_val = item[1]
                min_move = item[0]

        for i in range(NUM_OF_COLS):
            out = -1 if min_col.get(i) is None else min_col.get(i)
            print('{0:.2f}'.format(out), end=" ")
        print()

        return min_move

    def generate_tasks(self) -> dict:  # dict<state, init_move>
        tasks: dict = {}
        new_tasks: dict = {}
        for i in range(NUM_OF_COLS):  # max 7 subtasks
            if self.board.move_legal(i):
                self.board.move(i, COMPUTER)

                if self.board.game_end(i):
                    self.board.undo_move(i)
                    return {self.board.serialize(): i}

                tasks[self.board.serialize()] = i
                self.board.undo_move(i)

        for task_state, move in tasks.items():
            for i in range(NUM_OF_COLS):  # max 49 subtasks
                board = Board(task_state)
                if board.move_legal(i):
                    board.move(i, HUMAN)

                    # if board.game_end(i):
                    #     continue

                    new_tasks[board.serialize()] = (move, i)
                    board.undo_move(i)

        return new_tasks

    def serialize_message(self, board_state: str, player: str, last_col: int, depth: int) -> str:
        return board_state + player + str(last_col) + ',' + str(depth)

    def kill_slaves(self) -> None:
        for i in range(1, self.number_of_processes):
            self.comm.isend(DEATH_PILL, dest=i)

    def deserialize_message(self, message: str) -> (str, float):
        split = message.split(',')
        return split[0], float(split[1])


class Slave:
    def __init__(self, comm: mpi4py.MPI.Intracomm):
        self.comm = comm

    def do(self):
        while True:
            if self.comm.iprobe(source=0):
                continue
            message = self.comm.recv(source=0)
            if message == DEATH_PILL:
                # print("UGH", flush=True)
                break

            board, player, last_col, depth = self.deserialize_message(message)
            result = board.evaluate(player, last_col, depth)
            self.comm.isend(board.serialize() + ',' + str(result), dest=0)

    def deserialize_message(self, message: str) -> (Board, str, int, int):
        state_len = (NUM_OF_COLS * NUM_OF_ROWS)
        state = message[:state_len]
        player = message[state_len:state_len + 1]

        last_part_of_string = message[state_len + 1:].split(',')
        last_col = int(last_part_of_string[0])
        depth = int(last_part_of_string[1])

        return Board(state), player, last_col, depth


def main():
    communicator = MPI.COMM_WORLD
    process_rank = communicator.Get_rank()
    number_of_processes = communicator.Get_size()

    if process_rank == 0:
        Master(communicator, number_of_processes).do()
    else:
        Slave(communicator).do()


if __name__ == '__main__':
    main()
