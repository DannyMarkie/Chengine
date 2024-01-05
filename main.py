from core.board import Board
from core.pieces import Pieces
from core.move import Move
from tests.test_board import TestBoard
import time

board = Board(fenString="r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10", render=False)
print(board.to_fen())
TestBoard().perft(depth=4, board=board, verbose=True)
time.sleep(2)
