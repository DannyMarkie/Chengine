import sys
sys.path.insert(1, 'C:/Users/Danny/Documents/Programming/ai/games/pythonChess/git/Chengine')

from core.board import Board
from core.pieces import Pieces
from core.move import Move
import unittest
import time
import pygame

class TestBoard(unittest.TestCase):
    symbolFromPiece = {Pieces.Queen: 'q', Pieces.Rook: 'r', Pieces.Bishop: 'b', Pieces.Knight: 'n'}
    def perft(self, depth, board=Board(render=False), verbose=False):
        fen = board.to_fen()
        depth -= 1
        moves = board.generate_legal_moves()
        total = []
        for move in moves:
            board = Board(fenString=fen, render=board.render)
            board.move_piece(move)
            if board.render == True:
                board.update_render()
                time.sleep(0.1)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit(0)
            continuations = [0]
            if depth > 0:
                continuations = TestBoard().generate_move_sequences(depth=depth, board=board, lastMove=move)
            if verbose:
                print(f"{chr(97+ move.startSquare%8)}{8-abs(int(move.startSquare / 8))}{chr(97+ move.endSquare%8)}{8-abs(int(move.endSquare / 8))}{self.symbolFromPiece[move.movedPiece] if move.flag & Move.Flag.promote  == Move.Flag.promote else ''} ({move.startSquare},{move.endSquare}): {len(continuations)}")
            total += continuations
            board.undo_move(move)
        if verbose:
            print(f"\nNodes searched: {len(total)}")
        return total

    def generate_move_sequences(self, depth, board=Board(render=False), lastMove=None):
        moves = []
        if depth == 1:
            lastMoves = board.generate_legal_moves(last_move=lastMove)
            for move in lastMoves:
                board.move_piece(move)
                if board.render == True:
                        board.update_render()
                        time.sleep(0.1)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                sys.exit(0)
                board.undo_move(move)
            return lastMoves
      
        for move in board.generate_legal_moves(last_move=lastMove):
            board.move_piece(move)
            if board.render == True:
                board.update_render()
                time.sleep(0.1)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit(0)
            if not board.is_checkmate():
                moves += self.generate_move_sequences(depth=depth - 1, board=board, lastMove=move)
            board.undo_move(move)
        
        return moves

    def test_move_generation_pos1(self, render=False, depth=4):
        legal_moves_ply = [20, 400, 8_902, 197_281, 4_865_609, 119_060_324, 3_195_901_860, 84_998_978_956]
        for ply in range(1, depth+1):
            startTime = time.perf_counter()
            moves = self.perft(depth=ply, board=Board(render=render))
            endTime = time.perf_counter()
            print(f"Position: 1\t Depth: {ply} ply\tLegal moves generated: {len(moves)} \t\tExpected output: {legal_moves_ply[ply-1]}\t\tTime: {endTime-startTime:0.2f}s\t{'Passed' if len(moves) == legal_moves_ply[ply-1] else 'Failed'}")
            self.assertEqual(len(moves), legal_moves_ply[ply-1])
    
    def test_move_generation_pos2(self, render=False, depth=3):
        legal_moves_ply = [48, 2_039, 97_862, 4_085_603, 193_690_690, 8_031_647_685]
        for ply in range(1, depth+1):
            startTime = time.perf_counter()
            moves = self.perft(depth=ply, board=Board(render=render, fenString="r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -"))
            endTime = time.perf_counter()
            print(f"Position: 2\t Depth: {ply} ply\tLegal moves generated: {len(moves)} \t\tExpected output: {legal_moves_ply[ply-1]}\t\tTime: {endTime-startTime:0.2f}s\t{'Passed' if len(moves) == legal_moves_ply[ply-1] else 'Failed'}")
            self.assertEqual(len(moves), legal_moves_ply[ply-1])

    def test_move_generation_pos3(self, render=False, depth=5):
        legal_moves_ply = [14, 191, 2_812, 43_238, 674_624, 11_030_083, 178_633_661, 3_009_794_393]
        for ply in range(1, depth+1):
            startTime = time.perf_counter()
            moves = self.perft(depth=ply, board=Board(render=render, fenString="8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -"))
            endTime = time.perf_counter()
            print(f"Position: 3\t Depth: {ply} ply\tLegal moves generated: {len(moves)} \t\tExpected output: {legal_moves_ply[ply-1]}\t\tTime: {endTime-startTime:0.2f}s\t{'Passed' if len(moves) == legal_moves_ply[ply-1] else 'Failed'}")
            self.assertEqual(len(moves), legal_moves_ply[ply-1])

    def test_move_generation_pos4(self, render=False, depth=4):
        legal_moves_ply = [6, 264, 9_467, 422_333, 15_833_292, 706_045_033]
        for ply in range(1, depth+1):
            startTime = time.perf_counter()
            moves = self.perft(depth=ply, board=Board(render=render, fenString="r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"))
            endTime = time.perf_counter()
            print(f"Position: 4\t Depth: {ply} ply\tLegal moves generated: {len(moves)} \t\tExpected output: {legal_moves_ply[ply-1]}\t\tTime: {endTime-startTime:0.2f}s\t{'Passed' if len(moves) == legal_moves_ply[ply-1] else 'Failed'}")
            self.assertEqual(len(moves), legal_moves_ply[ply-1])

    def test_move_generation_pos5(self, render=False, depth=3):
        legal_moves_ply = [44, 1_486, 62_379, 2_103_487, 89_941_194]
        for ply in range(1, depth+1):
            startTime = time.perf_counter()
            moves = self.perft(depth=ply, board=Board(render=render, fenString="rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"))
            endTime = time.perf_counter()
            print(f"Position: 5\t Depth: {ply} ply\tLegal moves generated: {len(moves)} \t\tExpected output: {legal_moves_ply[ply-1]}\t\tTime: {endTime-startTime:0.2f}s\t{'Passed' if len(moves) == legal_moves_ply[ply-1] else 'Failed'}")
            self.assertEqual(len(moves), legal_moves_ply[ply-1])

    def test_move_generation_pos6(self, render=False, depth=3):
        legal_moves_ply = [46, 2_079, 89_890, 3_894_594, 164_075_551, 6_923_051_137, 287_188_994_746, 11_923_589_843_526]
        for ply in range(1, depth+1):
            startTime = time.perf_counter()
            moves = self.perft(depth=ply, board=Board(render=render, fenString="r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10"))
            endTime = time.perf_counter()
            print(f"Position: 6\t Depth: {ply} ply\tLegal moves generated: {len(moves)} \t\tExpected output: {legal_moves_ply[ply-1]}\t\tTime: {endTime-startTime:0.2f}s\t{'Passed' if len(moves) == legal_moves_ply[ply-1] else 'Failed'}")
            self.assertEqual(len(moves), legal_moves_ply[ply-1])

if __name__ == "__main__":    
    unittest.main()