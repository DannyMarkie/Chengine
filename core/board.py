from core.pieces import Pieces
from core.move import Move
from core.assets import Assets
import numpy as np
import pygame
import time

class Board:
    windowSize = 800
    startFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    def __init__(self, fenString=startFen, render=False) -> None:
        self.render = render
        self.load_fen(fenString)
        if render:
            self.setup_render()

    def to_fen(self):
        fen = ""
        symbolFromPieceType = {Pieces.King: 'k', Pieces.Pawn: 'p', Pieces.Knight: 'n', Pieces.Bishop: 'b', Pieces.Rook: 'r', Pieces.Queen: 'q'}
        empty = 0
        for rank in range(0, 8):
            empty = 0
            for file in range(0,8):
                piece = self.board[rank * 8 + file]
                if piece & Pieces.colorMask != 0:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    if piece & Pieces.colorMask == Pieces.White:
                        fen += symbolFromPieceType.get(piece & Pieces.pieceMask).upper()
                    else:
                        fen += symbolFromPieceType.get(piece & Pieces.pieceMask)
                else:
                    empty += 1
            if empty > 0:
                fen += str(empty)
                empty = 0
            if rank != 7:
                fen += '/'
        # fen = fen[::-1]
        fen += f"{' w' if self.turn & Pieces.colorMask == Pieces.White else ' b'}"
        fen += " "
        fen += 'K' if self.whiteCastleKingSide else ''
        fen += 'Q' if self.whiteCastleQueenSide else ''
        fen += 'k' if self.blackCastleKingSide else ''
        fen += 'q' if self.blackCastleQueenSide else ''
        return fen
                    
    def load_fen(self, fenString):
        self.board = [Pieces.Empty for n in range(0, 64)]
        pieceTypeFromSymbol = {'k': Pieces.King, 'p': Pieces.Pawn, 'n': Pieces.Knight, 'b': Pieces.Bishop, 'r': Pieces.Rook, 'q': Pieces.Queen}
        splitFen = fenString.split()
        fenBoard = splitFen[0]
        self.turn = Pieces.White if splitFen[1] == 'w' else Pieces.Black
        castlingRights = ''
        if len(splitFen) > 2 :
            if not splitFen[2].isnumeric():
                castlingRights = splitFen[2]

        self.whiteCastleQueenSide, self.blackCastleKingSide, self.blackCastleQueenSide, self.whiteCastleKingSide = False, False, False, False

        if 'k' in castlingRights:
            self.blackCastleKingSide = True
        if 'q' in castlingRights:
            self.blackCastleQueenSide = True
        if 'K' in castlingRights:
            self.whiteCastleKingSide = True
        if 'Q' in castlingRights:
            self.whiteCastleQueenSide = True

        self.removedWhiteCastleRightsKing, self.removedWhiteCastleRightsQueen = not self.whiteCastleKingSide, not self.whiteCastleQueenSide
        self.removedBlackCastleRightsKing, self.removedBlackCastleRightsQueen = not self.blackCastleKingSide, not self.blackCastleQueenSide

        file, rank = 0, 0

        for symbol in fenBoard:
            if symbol == '/':
                file = 0
                rank += 1
            else:
                if symbol.isnumeric():
                    file += int(symbol)
                else:
                    pieceColor = Pieces.White if symbol.isupper() else Pieces.Black
                    pieceType = pieceTypeFromSymbol.get(symbol.lower())
                    self.board[rank * 8 + file] = pieceColor | pieceType
                    file += 1

    def move_piece(self, move):
        self.turn = ~self.turn & Pieces.colorMask
        self.justRemovedWhiteCastleRightsKing, self.justRemovedWhiteCastleRightsQueen = False, False
        self.justRemovedBlackCastleRightsKing, self.justRemovedBlackCastleRightsQueen = False, False
        
        # Remove castling rights if rook gets taken
        if move.capturedPiece == Pieces.Rook:
            rank = move.endSquare % 8
            if move.capturedPiece & Pieces.colorMask == Pieces.White:
                # If not yet removed castle rights, do it
                if rank == 0 and not self.removedWhiteCastleRightsQueen:
                    self.whiteCastleQueenSide = False
                    self.removedWhiteCastleRightsQueen, self.justRemovedWhiteCastleRightsQueen = True, True
                elif not self.removedWhiteCastleRightsKing:
                    self.whiteCastleKingSide = False
                    self.removedWhiteCastleRightsKing, self.justRemovedWhiteCastleRightsKing = True, True
            else:
                # If not yet removed castle rights, do it
                if rank == 0 and not self.removedBlackCastleRightsQueen:
                    self.blackCastleQueenSide = False
                    self.removedBlackCastleRightsQueen, self.justRemovedBlackCastleRightsQueen = True, True
                elif not self.removedBlackCastleRightsKing:
                    self.blackCastleKingSide = False
                    self.removedBlackCastleRightsKing, self.justRemovedBlackCastleRightsKing = True, True

        # Remove castling rights if rook moves
        if move.movedPiece == Pieces.Rook:
            if move.movedPiece & Pieces.colorMask == Pieces.White:
                # If not yet removed castle rights, do it
                if move.startSquare == 56 and not self.removedWhiteCastleRightsQueen:
                    self.whiteCastleQueenSide = False
                    self.removedWhiteCastleRightsQueen, self.justRemovedWhiteCastleRightsQueen = True, True
                elif move.startSquare == 63 and not self.removedWhiteCastleRightsKing:
                    self.whiteCastleKingSide = False
                    self.removedWhiteCastleRightsKing, self.justRemovedWhiteCastleRightsKing = True, True
            else:
                # If not yet removed castle rights, do it
                if move.startSquare == 0 and not self.removedBlackCastleRightsQueen:
                    self.blackCastleQueenSide = False
                    self.removedBlackCastleRightsQueen, self.justRemovedBlackCastleRightsQueen = True, True
                elif move.startSquare == 7 and not self.removedBlackCastleRightsKing:
                    self.blackCastleKingSide = False
                    self.removedBlackCastleRightsKing, self.justRemovedBlackCastleRightsKing = True, True
        
        # Remove castling rights if king moves
        if move.movedPiece & Pieces.pieceMask == Pieces.King:
            if move.movedPiece & Pieces.colorMask == Pieces.White and (not self.removedWhiteCastleRightsKing and not self.removedWhiteCastleRightsQueen) :
                self.removedWhiteCastleRightsKing, self.justRemovedWhiteCastleRightsKing = True, True
                self.whiteCastleKingSide = False
                self.removedWhiteCastleRightsQueen, self.justRemovedWhiteCastleRightsQueen = True, True
                self.whiteCastleQueenSide = False
            elif not self.removedBlackCastleRightsKing and self.removedBlackCastleRightsQueen:
                self.removedBlackCastleRightsKing, self.justRemovedBlackCastleRightsKing = True, True
                self.blackCastleKingSide = False
                self.removedBlackCastleRightsQueen, self.justRemovedBlackCastleRightsQueen = True, True
                self.blackCastleQueenSide = False

        # Promote
        if move.flag & Move.Flag.promote == Move.Flag.promote:
            self.board[move.endSquare] = self.board[move.startSquare] & Pieces.colorMask | move.movedPiece
            self.board[move.startSquare] = Pieces.Empty
            return
        # Castle
        if move.flag & Move.Flag.castle == Move.Flag.castle:
            if move.movedPiece & Pieces.colorMask == Pieces.White:
                self.removedWhiteCastleRightsKing, self.justRemovedWhiteCastleRightsKing = True, True
                self.whiteCastleKingSide = False
                self.removedWhiteCastleRightsQueen, self.justRemovedWhiteCastleRightsQueen = True, True
                self.whiteCastleQueenSide = False
            else:
                self.removedBlackCastleRightsKing, self.justRemovedBlackCastleRightsKing = True, True
                self.blackCastleKingSide = False
                self.removedBlackCastleRightsQueen, self.justRemovedBlackCastleRightsQueen = True, True
                self.blackCastleQueenSide = False
            self.board[move.startSquare] = Pieces.Empty
            self.board[move.endSquare] = Pieces.Empty
            if move.startSquare > move.endSquare:
                self.board[move.startSquare - 2] = move.movedPiece
                self.board[move.startSquare - 1] = (move.movedPiece & Pieces.colorMask) | Pieces.Rook
            else:
                self.board[move.startSquare + 2] = move.movedPiece
                self.board[move.startSquare + 1] = (move.movedPiece & Pieces.colorMask) | Pieces.Rook
            return
        # En Passant
        if move.flag & Move.Flag.en_passant == Move.Flag.en_passant:
            endfile = move.endSquare % 8
            startfile = move.startSquare % 8
            self.board[move.endSquare] = self.board[move.startSquare]
            self.board[move.startSquare] = Pieces.Empty
            self.board[move.startSquare + endfile - startfile] = Pieces.Empty
            return
        # Normal move
        self.board[move.endSquare] = self.board[move.startSquare]
        self.board[move.startSquare] = Pieces.Empty

    def undo_move(self, move):
        self.turn = ~self.turn & Pieces.colorMask
        # Return castling rights
        if self.justRemovedBlackCastleRightsKing:
            self.blackCastleKingSide = True
            self.removedBlackCastleRightsKing = False
        if self.justRemovedBlackCastleRightsQueen:
            self.blackCastleQueenSide = True
            self.removedBlackCastleRightsQueen = False
        if self.justRemovedWhiteCastleRightsKing:
            self.whiteCastleKingSide = True
            self.removedWhiteCastleRightsKing = False
        if self.justRemovedWhiteCastleRightsQueen:
            self.whiteCastleQueenSide = True
            self.removedWhiteCastleRightsQueen = False

        # Promote
        if move.flag & Move.Flag.promote == Move.Flag.promote:
            self.board[move.startSquare] = self.board[move.endSquare] & Pieces.colorMask | Pieces.Pawn
            self.board[move.endSquare] = move.capturedPiece
            return

        # Castle
        if move.flag & Move.Flag.castle == Move.Flag.castle:
            if move.movedPiece & Pieces.colorMask == Pieces.White:
                self.removedWhiteCastleRightsKing, self.justRemovedWhiteCastleRightsKing = False, False
                self.whiteCastleKingSide = True
                self.removedWhiteCastleRightsQueen, self.justRemovedWhiteCastleRightsQueen = False, False
                self.whiteCastleQueenSide = True
            else:
                self.removedBlackCastleRightsKing, self.justRemovedBlackCastleRightsKing = False, False
                self.blackCastleKingSide = True
                self.removedBlackCastleRightsQueen, self.justRemovedBlackCastleRightsQueen = False, False
                self.blackCastleQueenSide = True
            if move.startSquare > move.endSquare:
                self.board[move.startSquare - 2] = Pieces.Empty
                self.board[move.startSquare - 1] = Pieces.Empty
            else:
                self.board[move.startSquare + 2] = Pieces.Empty
                self.board[move.startSquare + 1] = Pieces.Empty

            self.board[move.startSquare] = move.movedPiece
            self.board[move.endSquare] = (move.movedPiece & Pieces.colorMask) | Pieces.Rook
            return

        # En Passant
        if move.flag & Move.Flag.en_passant == Move.Flag.en_passant:
            endfile = move.endSquare % 8
            startfile = move.startSquare % 8
            self.board[move.startSquare] = self.board[move.endSquare]
            self.board[move.endSquare] = Pieces.Empty
            offset = 1 if self.turn & Pieces.colorMask == Pieces.White else -1
            self.board[move.endSquare + (offset * 8)] = ~self.turn & Pieces.colorMask | Pieces.Pawn
            return
        # Normal move
        self.board[move.startSquare] = self.board[move.endSquare]
        self.board[move.endSquare] = move.capturedPiece
    
    def move_is_legal(self, move, board=None):
        if board == None:
            board = self.board

        board.move_piece(move)
        if not self.is_in_check(~board.turn & Pieces.colorMask, self.board):
            board.undo_move(move)
            return True
        board.undo_move(move)
        return False

    def has_legal_moves(self, board=None):
        if board == None:
            board = self

        moves = board.generate_legal_moves(board=board.board)
        indexes = []
        for index, move in enumerate(moves):
            if not board.move_is_legal(move, board):
                indexes.append(index)

        for index in sorted(indexes, reverse=True):
            del moves[index]

        return not (len(moves) == 0)

    def target_is_attacked(self, turn, board, targetSquare):
        if turn == None:
            turn = self.turn
        if board == None:
            board = self.board

        bishopDirections = [-9, -7, 7, 9]
        rookDirections = [-8, -1, 1, 8]
        row = int(targetSquare/8)
        col = targetSquare % 8
        # Check if knight can capture king
        if int((targetSquare-10)/8) == row-1 and (targetSquare-10)%8 == col-2 and int((targetSquare-10)/8) >= 0 and (targetSquare-10 >= 0 and targetSquare-10 < 64) and board[targetSquare-10] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 1 up 2 right
        if int((targetSquare-6)/8) == row-1 and (targetSquare-6)%8 == col+2 and int((targetSquare-6)/8) >= 0 and (targetSquare-6 >= 0 and targetSquare-6 < 64) and board[targetSquare-6] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 2 up 1 left
        if int((targetSquare-17)/8) == row-2 and (targetSquare-17)%8 == col-1 and int((targetSquare-17)/8) >= 0 and (targetSquare-17 >= 0 and targetSquare-17 < 64) and board[targetSquare-17] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 2 up 1 right
        if int((targetSquare-15)/8) == row-2 and (targetSquare-15)%8 == col+1 and int((targetSquare-15)/8) >= 0 and (targetSquare-15 >= 0 and targetSquare-15 < 64) and board[targetSquare-15] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 1 down 2 right
        if int((targetSquare+10)/8) == row+1 and (targetSquare+10)%8 == col+2 and int((targetSquare+10)/8) < 8 and (targetSquare+10 >= 0 and targetSquare+10 < 64) and board[targetSquare+10] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 1 down 2 left
        if int((targetSquare+6)/8) == row+1 and (targetSquare+6)%8 == col-2 and int((targetSquare+6)/8) < 8 and (targetSquare+6 >= 0 and targetSquare+6 < 64) and board[targetSquare+6] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 2 down 1 right
        if int((targetSquare+17)/8) == row+2 and (targetSquare+17)%8 == col+1 and int((targetSquare+17)/8) < 8 and (targetSquare+17 >= 0 and targetSquare+17 < 64) and board[targetSquare+17] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 2 down 1 left
        if int((targetSquare+15)/8) == row+2 and (targetSquare+15)%8 == col-1 and int((targetSquare+15)/8) < 8 and (targetSquare+15 >= 0 and targetSquare+15 < 64) and board[targetSquare+15] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True

        # Check if pawn can capture king
        if turn == Pieces.Black:
            nextSquare = targetSquare+(7)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            if (abs(file - row) == 1 and abs(rank - col) == 1) and (nextSquare >= 0 and nextSquare < 64) and board[nextSquare] == Pieces.WhitePawn:
                return True
            nextSquare = targetSquare+(9)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            if (abs(file - row) == 1 and abs(rank - col) == 1) and (nextSquare >= 0 and nextSquare < 64) and board[nextSquare] == Pieces.WhitePawn:
                return True
            
        if turn == Pieces.White:
            nextSquare = targetSquare+(-7)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            if (abs(file - row) == 1 and abs(rank - col) == 1) and (nextSquare >= 0 and nextSquare < 64) and board[nextSquare] == Pieces.BlackPawn:
                return True
            nextSquare = targetSquare+(-9)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            if (abs(file - row) == 1 and abs(rank - col) == 1) and (nextSquare >= 0 and nextSquare < 64) and board[nextSquare] == Pieces.BlackPawn:
                return True

        # Check if bishop/queen/king can capture king diagonally
        for direction in bishopDirections:
            i=1
            nextSquare = targetSquare+(direction*i)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            while ((rank < 8 and rank >= 0 and file < 8 and file >= 0) and (abs(file - row) == i and abs(rank - col) == i) and (nextSquare >= 0 and nextSquare < 64)):
                i += 1
                if board[nextSquare] != Pieces.Empty:
                    if (board[nextSquare] == ~turn & Pieces.colorMask | Pieces.Bishop) or (board[nextSquare] == ~turn & Pieces.colorMask | Pieces.Queen) or (i == 2 and board[nextSquare] == ~turn & Pieces.colorMask | Pieces.King):
                        return True
                    break
                nextSquare = targetSquare+direction*i
                rank = (nextSquare) % 8
                file = int(nextSquare / 8)

        # Check if rook/queen/king can capture king orthogonally
        for direction in rookDirections:
            i=1
            nextSquare = targetSquare+(direction*i)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            while ((rank < 8 and rank >= 0 and file < 8 and file >= 0) and (abs(file - row) == i or abs(rank - col) == i) and (abs(file - row) + abs(rank - col) == i) and (nextSquare >= 0 and nextSquare < 64)):
                i += 1
                if board[nextSquare] != Pieces.Empty:
                    if (board[nextSquare] == ~turn & Pieces.colorMask | Pieces.Rook) or (board[nextSquare] == ~turn & Pieces.colorMask | Pieces.Queen) or (i == 2 and board[nextSquare] == ~turn & Pieces.colorMask | Pieces.King):
                        return True
                    break
                nextSquare = targetSquare+direction*i
                rank = (nextSquare) % 8
                file = int(nextSquare / 8)
        return False

    def is_in_check(self, turn=None, board=None):
        if turn == None:
            turn = self.turn
        if board == None:
            board = self.board

        bishopDirections = [-9, -7, 7, 9]
        rookDirections = [-8, -1, 1, 8]
        kingSquare = board.index(turn | Pieces.King)
        row = int(kingSquare/8)
        col = kingSquare % 8
        # Check if knight can capture king
        if int((kingSquare-10)/8) == row-1 and (kingSquare-10)%8 == col-2 and int((kingSquare-10)/8) >= 0 and (kingSquare-10 >= 0 and kingSquare-10 < 64) and board[kingSquare-10] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 1 up 2 right
        if int((kingSquare-6)/8) == row-1 and (kingSquare-6)%8 == col+2 and int((kingSquare-6)/8) >= 0 and (kingSquare-6 >= 0 and kingSquare-6 < 64) and board[kingSquare-6] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 2 up 1 left
        if int((kingSquare-17)/8) == row-2 and (kingSquare-17)%8 == col-1 and int((kingSquare-17)/8) >= 0 and (kingSquare-17 >= 0 and kingSquare-17 < 64) and board[kingSquare-17] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 2 up 1 right
        if int((kingSquare-15)/8) == row-2 and (kingSquare-15)%8 == col+1 and int((kingSquare-15)/8) >= 0 and (kingSquare-15 >= 0 and kingSquare-15 < 64) and board[kingSquare-15] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 1 down 2 right
        if int((kingSquare+10)/8) == row+1 and (kingSquare+10)%8 == col+2 and int((kingSquare+10)/8) < 8 and (kingSquare+10 >= 0 and kingSquare+10 < 64) and board[kingSquare+10] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 1 down 2 left
        if int((kingSquare+6)/8) == row+1 and (kingSquare+6)%8 == col-2 and int((kingSquare+6)/8) < 8 and (kingSquare+6 >= 0 and kingSquare+6 < 64) and board[kingSquare+6] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 2 down 1 right
        if int((kingSquare+17)/8) == row+2 and (kingSquare+17)%8 == col+1 and int((kingSquare+17)/8) < 8 and (kingSquare+17 >= 0 and kingSquare+17 < 64) and board[kingSquare+17] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True
        # 2 down 1 left
        if int((kingSquare+15)/8) == row+2 and (kingSquare+15)%8 == col-1 and int((kingSquare+15)/8) < 8 and (kingSquare+15 >= 0 and kingSquare+15 < 64) and board[kingSquare+15] == ~turn & Pieces.colorMask | Pieces.Knight:
            return True

        # Check if pawn can capture king
        if turn == Pieces.Black:
            nextSquare = kingSquare+(7)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            if (abs(file - row) == 1 and abs(rank - col) == 1) and (nextSquare >= 0 and nextSquare < 64) and board[nextSquare] == Pieces.WhitePawn:
                return True
            nextSquare = kingSquare+(9)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            if (abs(file - row) == 1 and abs(rank - col) == 1) and (nextSquare >= 0 and nextSquare < 64) and board[nextSquare] == Pieces.WhitePawn:
                return True
            
        if turn == Pieces.White:
            nextSquare = kingSquare+(-7)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            if (abs(file - row) == 1 and abs(rank - col) == 1) and (nextSquare >= 0 and nextSquare < 64) and board[nextSquare] == Pieces.BlackPawn:
                return True
            nextSquare = kingSquare+(-9)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            if (abs(file - row) == 1 and abs(rank - col) == 1) and (nextSquare >= 0 and nextSquare < 64) and board[nextSquare] == Pieces.BlackPawn:
                return True

        # Check if bishop/queen/king can capture king diagonally
        for direction in bishopDirections:
            i=1
            nextSquare = kingSquare+(direction*i)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            while ((rank < 8 and rank >= 0 and file < 8 and file >= 0) and (abs(file - row) == i and abs(rank - col) == i) and (nextSquare >= 0 and nextSquare < 64)):
                i += 1
                if board[nextSquare] != Pieces.Empty:
                    if (board[nextSquare] == ~turn & Pieces.colorMask | Pieces.Bishop) or (board[nextSquare] == ~turn & Pieces.colorMask | Pieces.Queen) or (i == 2 and board[nextSquare] == ~turn & Pieces.colorMask | Pieces.King):
                        return True
                    break
                nextSquare = kingSquare+direction*i
                rank = (nextSquare) % 8
                file = int(nextSquare / 8)

        # Check if rook/queen/king can capture king orthogonally
        for direction in rookDirections:
            i=1
            nextSquare = kingSquare+(direction*i)
            rank = nextSquare % 8
            file = int(nextSquare / 8)
            while ((rank < 8 and rank >= 0 and file < 8 and file >= 0) and (abs(file - row) == i or abs(rank - col) == i) and (abs(file - row) + abs(rank - col) == i) and (nextSquare >= 0 and nextSquare < 64)):
                i += 1
                if board[nextSquare] != Pieces.Empty:
                    if (board[nextSquare] == ~turn & Pieces.colorMask | Pieces.Rook) or (board[nextSquare] == ~turn & Pieces.colorMask | Pieces.Queen) or (i == 2 and board[nextSquare] == ~turn & Pieces.colorMask | Pieces.King):
                        return True
                    break
                nextSquare = kingSquare+direction*i
                rank = (nextSquare) % 8
                file = int(nextSquare / 8)
        return False

    def is_checkmate(self, turn=None):
        if turn == None:
            turn = self.turn
        return (self.is_in_check(turn=turn, board=self.board) and not self.has_legal_moves())

    def generate_legal_moves(self, last_move=None, board=None, turn=None):
        if board is None:
            board = self.board
        if turn is None:
            turn = self.turn

        promotionPieces = [Pieces.Queen, Pieces.Rook, Pieces.Bishop, Pieces.Knight]

        moves = []

        # Castling
        if turn == Pieces.White:
            if self.whiteCastleKingSide and board[63] == Pieces.WhiteRook and board[60] == Pieces.WhiteKing:
                if (not self.target_is_attacked(turn, board, 60) and not self.target_is_attacked(turn, board, 62) and not self.target_is_attacked(turn, board, 61)) and board[62] == Pieces.Empty and board[61] == Pieces.Empty:
                    move = Move(startSquare=60, endSquare=63, movedPiece=Pieces.WhiteKing, flag=Move.Flag.castle)
                    moves.append(move)
            if self.whiteCastleQueenSide and board[56] == Pieces.WhiteRook and board[60] == Pieces.WhiteKing:
                if (not self.target_is_attacked(turn, board, 60) and not self.target_is_attacked(turn, board, 59) and not self.target_is_attacked(turn, board, 58)) and (board[59] == Pieces.Empty and board[58] == Pieces.Empty and board[57] == Pieces.Empty):
                    move = Move(startSquare=60, endSquare=56, movedPiece=Pieces.WhiteKing, flag=Move.Flag.castle)
                    moves.append(move)
        elif turn == Pieces.Black:
            if self.blackCastleKingSide and board[7] == Pieces.BlackRook and board[4] == Pieces.BlackKing:
                if not self.target_is_attacked(turn, board, 4) and not self.target_is_attacked(turn, board, 5) and not self.target_is_attacked(turn, board, 6) and board[5] == Pieces.Empty and board[6] == Pieces.Empty:
                    move = Move(startSquare=4, endSquare=7, movedPiece=Pieces.BlackKing, flag=Move.Flag.castle)
                    moves.append(move)
            if self.blackCastleQueenSide and board[0] == Pieces.BlackRook and board[4] == Pieces.BlackKing:
                if not self.target_is_attacked(turn, board, 4) and not self.target_is_attacked(turn, board, 3) and not self.target_is_attacked(turn, board, 2) and board[3] == Pieces.Empty and board[2] == Pieces.Empty and board[1] == Pieces.Empty:
                    move = Move(startSquare=4, endSquare=0, movedPiece=Pieces.BlackKing, flag=Move.Flag.castle)
                    moves.append(move)

        for index, piece in enumerate(board):
            # No Piece
            if piece == Pieces.Empty:
                continue
# ______________________________________________________________________________________________________ #
            # Pawns
            if piece == Pieces.WhitePawn and turn == Pieces.White:
                startRank = index % 8
                startFile = int(index/8)
                file = int((index-8)/8)
                # Check if square in front is empty
                if board[index - 8] == Pieces.Empty:
                    move = Move(index, index-8, Pieces.Pawn, board[index-8])
                    self.move_piece(move)
                    if not file == 0:
                        moves.append(move)
                    self.undo_move(move)
                    if file == 0:
                        for promoted in promotionPieces:
                            move = Move(index, index-8, promoted, board[index-8], flag=Move.Flag.promote)
                            self.move_piece(move)
                            moves.append(move)
                            self.undo_move(move)
                    # If Pawn hasnt moved yet, check for 2 squares ahead
                    if index > 47 and index < 56 and board[index - 16] == Pieces.Empty:
                        move = Move(index, index-16, Pieces.Pawn, board[index-16])
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                # Check for captures
                nextSquare = index+(-7)
                rank = nextSquare % 8
                file = int(nextSquare / 8)
                if (abs(file - startFile) == 1 and abs(rank - startRank) == 1) and board[index-7] & Pieces.colorMask == Pieces.Black:
                    move = Move(index, index-7, Pieces.Pawn, board[index-7])
                    self.move_piece(move)
                    if not file == 0:
                        moves.append(move)
                    self.undo_move(move)
                    if file == 0:
                        for promoted in promotionPieces:
                            move = Move(index, index-7, promoted, board[index-7], flag=Move.Flag.promote)
                            self.move_piece(move)
                            moves.append(move)
                            self.undo_move(move)
                nextSquare = index+(-9)
                rank = nextSquare % 8
                file = int(nextSquare / 8)
                if (abs(file - startFile) == 1 and abs(rank - startRank) == 1) and board[index-9] & Pieces.colorMask == Pieces.Black:
                    move = Move(index, index-9, Pieces.Pawn, board[index-9])
                    self.move_piece(move)
                    if not file == 0:
                        moves.append(move)
                    self.undo_move(move)
                    if file == 0:
                        for promoted in promotionPieces:
                            move = Move(index, index-9, promoted, board[index-9], flag=Move.Flag.promote)
                            self.move_piece(move)
                            moves.append(move)
                            self.undo_move(move)
                # En Passant
                # If other pawn made double step resulting in end position being next to this pawn, allow capturing as if other pawn only moved one square
                if last_move is not None: 
                    if last_move.movedPiece == Pieces.Pawn and (last_move.endSquare == index-1 or last_move.endSquare == index+1) and last_move.startSquare == last_move.endSquare-16 and int(index/8) == int(last_move.endSquare/8):
                        move = Move(index, index - 8 + (last_move.endSquare - index), Pieces.Pawn, board[index - 8 + (last_move.endSquare - index)], Move.Flag.en_passant)
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                continue
            elif piece == Pieces.BlackPawn and turn == Pieces.Black:
                startRank = index % 8
                startFile = int(index/8)
                file = int((index+8)/8)
                # Check if square in front is empty
                if board[index + 8] == Pieces.Empty:
                    move = Move(index, index+8, Pieces.Pawn, board[index+8])
                    self.move_piece(move)
                    if not file == 7:
                        moves.append(move)
                    self.undo_move(move)
                    if file == 7:
                        for promoted in promotionPieces:
                            move = Move(index, index+8, promoted, board[index+8], flag=Move.Flag.promote)
                            self.move_piece(move)
                            moves.append(move)
                            self.undo_move(move)
                    # If Pawn hasnt moved yet, check for 2 squares ahead
                    if index > 7 and index < 16 and board[index + 16] == Pieces.Empty:
                        move = Move(index, index+16, Pieces.Pawn, board[index+16])
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                # Check for captures
                nextSquare = index+(7)
                rank = nextSquare % 8
                file = int(nextSquare / 8)
                if (abs(file - startFile) == 1 and abs(rank - startRank) == 1) and board[index+7] & Pieces.colorMask == Pieces.White:
                    move = Move(index, index+7, Pieces.Pawn, board[index+7])
                    self.move_piece(move)
                    if not file == 7:
                        moves.append(move)
                    self.undo_move(move)
                    if file == 7:
                        for promoted in promotionPieces:
                            move = Move(index, index+7, promoted, board[index+7], flag=Move.Flag.promote)
                            self.move_piece(move)
                            moves.append(move)
                            self.undo_move(move)
                nextSquare = index+(9)
                rank = nextSquare % 8
                file = int(nextSquare / 8)
                if (abs(file - startFile) == 1 and abs(rank - startRank) == 1) and board[index+9] & Pieces.colorMask == Pieces.White:
                    move = Move(index, index+9, Pieces.Pawn, board[index+9])
                    self.move_piece(move)
                    if not file == 7:
                        moves.append(move)
                    self.undo_move(move)
                    if file == 7:
                        for promoted in promotionPieces:
                            move = Move(index, index+9, promoted, board[index+9], flag=Move.Flag.promote)
                            self.move_piece(move)
                            moves.append(move)
                            self.undo_move(move)
                # En Passant
                if last_move is not None: 
                    if last_move.movedPiece == Pieces.Pawn and (last_move.endSquare == index-1 or last_move.endSquare == index+1) and last_move.startSquare == last_move.endSquare+16 and int(index/8) == int(last_move.endSquare/8):
                        move = Move(index, index + 8 + (last_move.endSquare - index), Pieces.Pawn, board[index + 8 + (last_move.endSquare - index)], Move.Flag.en_passant)
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                continue
# ______________________________________________________________________________________________________ #
            # Knights
            if piece & Pieces.pieceMask == Pieces.Knight and piece & Pieces.colorMask == turn:
                row = int(index/8)
                col = index % 8
                # 1 up 2 left
                if int((index-10)/8) == row-1 and (index-10)%8 == col-2 and int((index-10)/8) >= 0 and Pieces.colorMask & board[index-10] != turn and (index-10 >= 0 and index-10 < 64):
                    move = Move(index, index-10, Pieces.Knight, board[index-10])
                    self.move_piece(move)
                    moves.append(move)
                    self.undo_move(move)
                # 1 up 2 right
                if int((index-6)/8) == row-1 and (index-6)%8 == col+2 and int((index-6)/8) >= 0 and Pieces.colorMask & board[index-6] != turn and (index-6 >= 0 and index-6 < 64):
                    move = Move(index, index-6, Pieces.Knight, board[index-6])
                    self.move_piece(move)
                    moves.append(move)
                    self.undo_move(move)
                # 2 up 1 left
                if int((index-17)/8) == row-2 and (index-17)%8 == col-1 and int((index-17)/8) >= 0 and Pieces.colorMask & board[index-17] != turn and (index-17 >= 0 and index-17 < 64):
                    move = Move(index, index-17, Pieces.Knight, board[index-17])
                    self.move_piece(move)
                    moves.append(move)
                    self.undo_move(move)
                # 2 up 1 right
                if int((index-15)/8) == row-2 and (index-15)%8 == col+1 and int((index-15)/8) >= 0 and Pieces.colorMask & board[index-15] != turn and (index-15 >= 0 and index-15 < 64):
                    move = Move(index, index-15, Pieces.Knight, board[index-15])
                    self.move_piece(move)
                    moves.append(move)
                    self.undo_move(move)
                # 1 down 2 right
                if int((index+10)/8) == row+1 and (index+10)%8 == col+2 and int((index+10)/8) < 8 and Pieces.colorMask & board[index+10] != turn and (index+10 >= 0 and index+10 < 64):
                    move = Move(index, index+10, Pieces.Knight, board[index+10])
                    self.move_piece(move)
                    moves.append(move)
                    self.undo_move(move)
                # 1 down 2 left
                if int((index+6)/8) == row+1 and (index+6)%8 == col-2 and int((index+6)/8) < 8 and Pieces.colorMask & board[index+6] != turn and (index+6 >= 0 and index+6 < 64):
                    move = Move(index, index+6, Pieces.Knight, board[index+6])
                    self.move_piece(move)
                    moves.append(move)
                    self.undo_move(move)
                # 2 down 1 right
                if int((index+17)/8) == row+2 and (index+17)%8 == col+1 and int((index+17)/8) < 8 and Pieces.colorMask & board[index+17] != turn and (index+17 >= 0 and index+17 < 64):
                    move = Move(index, index+17, Pieces.Knight, board[index+17])
                    self.move_piece(move)
                    moves.append(move)
                    self.undo_move(move)
                # 2 down 1 left
                if int((index+15)/8) == row+2 and (index+15)%8 == col-1 and int((index+15)/8) < 8 and Pieces.colorMask & board[index+15] != turn and (index+15 >= 0 and index+15 < 64):
                    move = Move(index, index+15, Pieces.Knight, board[index+15])
                    self.move_piece(move)
                    moves.append(move)
                    self.undo_move(move)
                continue        
# ______________________________________________________________________________________________________ #       
            # Bishops
            if piece & Pieces.pieceMask == Pieces.Bishop and piece & Pieces.colorMask == turn:
                moveDirections = [-9, -7, 7, 9]
                startRank = index % 8
                startFile = int(index/8)
                for direction in moveDirections:
                    i=1
                    nextSquare = index+(direction*i)
                    rank = nextSquare % 8
                    file = int(nextSquare / 8)
                    while ((rank < 8 and rank >= 0 and file < 8 and file >= 0) and (abs(file - startFile) == i and abs(rank - startRank) == i)) and (nextSquare >= 0 and nextSquare < 64) and ((board[nextSquare] == Pieces.Empty) or board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask):
                        move = Move(index, nextSquare, Pieces.Bishop, board[nextSquare])
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                        i += 1
                        if board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask:
                            break
                        nextSquare = index+direction*i
                        rank = (nextSquare) % 8
                        file = int(nextSquare / 8)
                continue            
# ______________________________________________________________________________________________________ #
            # Rooks
            if piece & Pieces.pieceMask == Pieces.Rook and piece & Pieces.colorMask == turn:
                moveDirections = [-8, -1, 1, 8]
                startRank = index % 8
                startFile = int(index/8)
                for direction in moveDirections:
                    i=1
                    nextSquare = index+direction*i
                    rank = nextSquare % 8
                    file = int(nextSquare / 8)
                    while (rank < 8 and rank >= 0 and file < 8 and file >= 0 and (abs(file - startFile) == i or abs(rank - startRank) == i) and (abs(file - startFile) + abs(rank - startRank) == i)) and (nextSquare >= 0 and nextSquare < 64) and (board[nextSquare] == Pieces.Empty or board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask):
                        move = Move(index, index + direction*i, Pieces.Rook, board[index+direction*i])
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                        i += 1
                        if board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask:
                            break
                        nextSquare = index+direction*i
                        rank = (nextSquare) % 8
                        file = int(nextSquare / 8)
                continue
# ______________________________________________________________________________________________________ #
            # Queens
            if piece & Pieces.pieceMask == Pieces.Queen and piece & Pieces.colorMask == turn:
                bishopDirections = [-9, -7, 7, 9]
                rookDirections = [-8, -1, 1, 8]
                startRank = index % 8
                startFile = int(index/8)
                for direction in rookDirections:
                    i=1
                    nextSquare = index+direction*i
                    rank = nextSquare % 8
                    file = int(nextSquare / 8)
                    while (rank < 8 and rank >= 0 and file < 8 and file >= 0 and (abs(file - startFile) == i or abs(rank - startRank) == i) and (abs(file - startFile) + abs(rank - startRank) == i)) and (nextSquare >= 0 and nextSquare < 64) and (board[nextSquare] == Pieces.Empty or board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask):
                        move = Move(index, index + direction*i, Pieces.Queen, board[index+direction*i])
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                        i += 1
                        if board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask:
                            break
                        nextSquare = index+direction*i
                        rank = (nextSquare) % 8
                        file = int(nextSquare / 8)
                for direction in bishopDirections:
                    i=1
                    nextSquare = index+direction*i
                    rank = nextSquare % 8
                    file = int(nextSquare / 8)
                    while (rank < 8 and rank >= 0 and file < 8 and file >= 0 and (abs(file - startFile) == i and abs(rank - startRank) == i)) and (nextSquare >= 0 and nextSquare < 64)  and (board[nextSquare] == Pieces.Empty or board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask):
                        move = Move(index, index + direction*i, Pieces.Queen, board[index+direction*i])
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                        i += 1
                        if board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask:
                            break
                        nextSquare = index+direction*i
                        rank = (nextSquare) % 8
                        file = int(nextSquare / 8)
                continue            
# ______________________________________________________________________________________________________ #
            # Kings
            if piece & Pieces.pieceMask == Pieces.King and piece & Pieces.colorMask == turn:
                bishopDirections = [-9, -7, 7, 9]
                rookDirections = [-8, -1, 1, 8]
                startRank = index % 8
                startFile = int(index/8)
                for direction in rookDirections:
                    i=1
                    nextSquare = index+direction*i
                    rank = nextSquare % 8
                    file = int(nextSquare / 8)
                    if (rank < 8 and rank >= 0 and file < 8 and file >= 0 and (abs(file - startFile) == i or abs(rank - startRank) == i) and (abs(file - startFile) + abs(rank - startRank) == i)) and (nextSquare >= 0 and nextSquare < 64) and (board[nextSquare] == Pieces.Empty or board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask):
                        move = Move(index, index + direction*i, Pieces.King, board[index+direction*i])
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                for direction in bishopDirections:
                    i=1
                    nextSquare = index+direction*i
                    rank = nextSquare % 8
                    file = int(nextSquare / 8)
                    if (rank < 8 and rank >= 0 and file < 8 and file >= 0 and (abs(file - startFile) == i and abs(rank - startRank) == i)) and (nextSquare >= 0 and nextSquare < 64)  and (board[nextSquare] == Pieces.Empty or board[nextSquare] & Pieces.colorMask == ~turn & Pieces.colorMask):
                        move = Move(index, index + direction*i, Pieces.King, board[index+direction*i])
                        self.move_piece(move)
                        moves.append(move)
                        self.undo_move(move)
                continue                            
# ______________________________________________________________________________________________________ #
            
        return moves
    
    def setup_render(self):
        pygame.init()
        self.gameDisplay = pygame.display.set_mode((self.windowSize,self.windowSize))
        pygame.display.set_caption('ChEngine')
        self.clock = pygame.time.Clock()
        self.update_render()

    def update_render(self):
        self.gameDisplay.fill((255, 255, 255))
        squareSize = self.windowSize / 8
        offset = 1
        for index, square in enumerate(self.board):
            if index % 8 == 0: offset += 1
            x = (index % 8) * squareSize
            y = int(index/8) * squareSize
            color = (181, 151, 98) if (index + offset) % 2 == 0 else (128, 105, 66)
            pygame.draw.rect(self.gameDisplay, color, pygame.Rect(x, y, squareSize, squareSize))
            
            # Draw white pieces 
            if square == Pieces.WhitePawn:
                self.gameDisplay.blit(Assets.whitePawn, (x+12.5, y+12.5))
            if square == Pieces.WhiteQueen:
                self.gameDisplay.blit(Assets.whiteQueen, (x+7.5, y+7.5))
            if square == Pieces.WhiteKing:
                self.gameDisplay.blit(Assets.whiteKing, (x+10, y+10))
            if square == Pieces.WhiteRook:
                self.gameDisplay.blit(Assets.whiteRook, (x+12.5, y+12.5))
            if square == Pieces.WhiteKnight:
                self.gameDisplay.blit(Assets.whiteKnight, (x+12.5, y+12.5))
            if square == Pieces.WhiteBishop:
                self.gameDisplay.blit(Assets.whiteBishop, (x+10, y+10))

            # Draw black pieces
            if square == Pieces.BlackPawn:
                self.gameDisplay.blit(Assets.blackPawn, (x+12.5, y+12.5))
            if square == Pieces.BlackQueen:
                self.gameDisplay.blit(Assets.blackQueen, (x+7.5, y+7.5))
            if square == Pieces.BlackKing:
                self.gameDisplay.blit(Assets.blackKing, (x+10, y+10))
            if square == Pieces.BlackRook:
                self.gameDisplay.blit(Assets.blackRook, (x+12.5, y+12.5))
            if square == Pieces.BlackKnight:
                self.gameDisplay.blit(Assets.blackKnight, (x+12.5, y+12.5))
            if square == Pieces.BlackBishop:
                self.gameDisplay.blit(Assets.blackBishop, (x+10, y+10))
        pygame.display.flip()
    
    def exitWindow(self):
        pygame.quit()

    def __str__(self) -> str:
        stringified = "\n"
        for index, entry in enumerate(self.board):
            if index % 8 == 0 and index != 0:
                stringified += "\n----------------------------------------\n"
            stringified += bin(entry) + " | "
        return stringified