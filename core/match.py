from core.board import Board
from core.pieces import Pieces
import pygame
import sys
import time

class Match:
    def __init__(self, bot1, bot2, board=Board()) -> None:
        self.bot1 = bot1
        self.bot2 = bot2
        self.board = board
        self.winner = None
        self.movesSincePawnPush = 0
        self.movesSinceCapture = 0

    def play(self):
        if self.board.render == True:
            print("Game starting in 2 seconds")
            self.board.update_render()
            time.sleep(2)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
        while self.winner == None and not len(self.board.generate_legal_moves()) == 0 and (self.movesSinceCapture < 51 and self.movesSincePawnPush < 51):
            board_clone = Board(fenString=self.board.to_fen())
            if self.board.turn == Pieces.White:
                move = self.bot1.get_move(board_clone)
                self.board.move_piece(move)
                if self.board.is_checkmate():
                    self.winner = Pieces.White
                    break
            elif self.board.turn == Pieces.Black:
                move = self.bot2.get_move(board_clone)
                self.board.move_piece(move)
                if self.board.is_checkmate():
                    self.winner = Pieces.Black
                    break
            # Update moves since captured piece
            if move.capturedPiece == Pieces.Empty:
                    self.movesSinceCapture += 1
            else:
                self.movesSinceCapture = 0
            # Update moves since pawn push
            if move.movedPiece & Pieces.pieceMask == Pieces.Pawn:
                self.movesSincePawnPush = 0
            else:
                self.movesSincePawnPush += 1
            # Update render if necessary
            if self.board.render == True:
                self.board.update_render()
                time.sleep(0.5)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit(0)
            # print(self.board.is_checkmate(), self.movesSinceCapture, self.movesSincePawnPush, len(self.board.generate_legal_moves()), self.winner)
        print(self.winner)
        if self.board.render == True:
            self.board.update_render()
            time.sleep(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
        return self.winner