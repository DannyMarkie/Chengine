from bots.bot import Bot
from core.pieces import Pieces
from core.move import Move
from core.board import Board
import time
import random
import threading
import numpy as np

class PieceTableProgressionV7(Bot):
    killerBias = 10
    killerMoves = {}
    thinkTimeOut = False
    maxValue = 48_400 - 40_000
    bgpawnTable = [   0,  0,  0,  0,  0,  0,  0,  0,
                    50, 50, 50, 50, 50, 50, 50, 50,
                    10, 10, 20, 30, 30, 20, 10, 10,
                    5,  5, 10, 25, 25, 10,  5,  5,
                    0,  0,  0, 20, 20,  0,  0,  0,
                    5, -5,-10,  0,  0,-10, -5,  5,
                    5, 10, 10,-20,-20, 10, 10,  5,
                    0,  0,  0,  0,  0,  0,  0,  0   ]
    egpawnTable = [ 0,   0,   0,   0,   0,   0,   0,   0,
                    178, 173, 158, 134, 147, 132, 165, 187,
                    94, 100,  85,  67,  56,  53,  82,  84,
                    32,  24,  13,   5,  -2,   4,  17,  17,
                    13,   9,  -3,  -7,  -7,  -8,   3,  -1,
                    4,   7,  -6,   1,   0,  -5,  -1,  -8,
                    13,   8,   8,  10,  13,   0,   2,  -7,
                    0,   0,   0,   0,   0,   0,   0,   0    ]
    knightTable = [ -50,-40,-30,-30,-30,-30,-40,-50,
                    -40,-20,  0,  0,  0,  0,-20,-40,
                    -30,  0, 10, 15, 15, 10,  0,-30,
                    -30,  5, 15, 20, 20, 15,  5,-30,
                    -30,  0, 15, 20, 20, 15,  0,-30,
                    -30,  5, 10, 15, 15, 10,  5,-30,
                    -40,-20,  0,  5,  5,  0,-20,-40,
                    -50,-40,-30,-30,-30,-30,-40,-50]
    bishopTable = [ -20,-10,-10,-10,-10,-10,-10,-20,
                    -10,  0,  0,  0,  0,  0,  0,-10,
                    -10,  0,  5, 10, 10,  5,  0,-10,
                    -10,  5,  5, 10, 10,  5,  5,-10,
                    -10,  0, 10, 10, 10, 10,  0,-10,
                    -10, 10, 10, 10, 10, 10, 10,-10,
                    -10,  5,  0,  0,  0,  0,  5,-10,
                    -20,-10,-10,-10,-10,-10,-10,-20,]
    rookTable = [   0,  0,  0,  0,  0,  0,  0,  0,
                    5, 10, 10, 10, 10, 10, 10,  5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    0,  0,  0,  5,  5,  0,  0,  0   ]
    queenTable = [  -20,-10,-10, -5, -5,-10,-10,-20,
                    -10,  0,  0,  0,  0,  0,  0,-10,
                    -10,  0,  5,  5,  5,  5,  0,-10,
                    -5,  0,  5,  5,  5,  5,  0, -5,
                    0,  0,  5,  5,  5,  5,  0, -5,
                    -10,  5,  5,  5,  5,  5,  0,-10,
                    -10,  0,  5,  0,  0,  0,  0,-10,
                    -20,-10,-10, -5, -5,-10,-10,-20 ]
    mgKingTable = [ -30,-40,-40,-50,-50,-40,-40,-30,
                    -30,-40,-40,-50,-50,-40,-40,-30,
                    -30,-40,-40,-50,-50,-40,-40,-30,
                    -30,-40,-40,-50,-50,-40,-40,-30,
                    -20,-30,-30,-40,-40,-30,-30,-20,
                    -10,-20,-20,-20,-20,-20,-20,-10,
                    20, 20,  0,  0,  0,  0, 20, 20,
                    20, 30, 10,  0,  0, 10, 30, 20  ]
    egKingTable = [ -50,-40,-30,-20,-20,-30,-40,-50,
                    -30,-20,-10,  0,  0,-10,-20,-30,
                    -30,-10, 20, 30, 30, 20,-10,-30,
                    -30,-10, 30, 40, 40, 30,-10,-30,
                    -30,-10, 30, 40, 40, 30,-10,-30,
                    -30,-10, 20, 30, 30, 20,-10,-30,
                    -30,-30,  0,  0,  0,  0,-30,-30,
                    -50,-30,-30,-30,-30,-30,-30,-50 ]
    gameStates = {}


    def __init__(self, thinkTime=10) -> None:
        self.thinkTime = thinkTime
        self.zobrist = self.init_zobrist()
        self.mask = 0xFFFF_FFFF
        self.transpositionTable = {} # Key is Zobrist masked by mask and value is array with at index 0 the move and at index 1 the eval
        super().__init__()

    def init_zobrist(self):
        zobristTable = [[random.randint(0, pow(2, 64)) for x in range(24)] for i in range(64)]
        return zobristTable
    
    def compute_hash(self, board):
        h = 0
        for index, piece in enumerate(board.board):
            if piece != Pieces.Empty:
                h ^= self.zobrist[index][piece]
        return h
    
    def set_timeout(self):
        self.thinkTimeOut = True
    
    def get_move(self, board=Board()):
        isMaximizingPlayer = 1 if board.turn == Pieces.White else -1
        currentDepth = 1
        startTime = time.time()
        move = None
        t = threading.Timer(self.thinkTime, self.set_timeout)
        t.daemon = True
        t.start()
        while time.time() - self.thinkTime < startTime:
            print(currentDepth)
            self.nodes = 0
            self.prunedTrees = 0
            self.hashLookups = 0
            if move is not None:
                move, evaluation = self.search(board=board, maxDepth=currentDepth, maxDepthExtension=currentDepth+2, isMaximizingPlayer=isMaximizingPlayer, prevBestMove=move)
            else:
                move, evaluation = self.search(board=board, maxDepth=currentDepth, maxDepthExtension=currentDepth+2, isMaximizingPlayer=isMaximizingPlayer)
            currentDepth += 1
        print(f"Eval: {evaluation:.1f}\nTime taken: {time.time() - startTime}\nNodes searched: {self.nodes}\nHash Lookups: {self.hashLookups}")
        self.thinkTimeOut = False
        board.move_piece(move)
        if str(board.board) in self.gameStates:
            self.gameStates[str(board.board)] += 1
        else: 
            self.gameStates[str(board.board)] = 1
        board.undo_move(move)
        return move

    def search(self, board, maxDepth, depth=0, maxDepthExtension=1, isMaximizingPlayer=1, lastMove=None, alpha=-1000000, beta=1000000, prevBestMove=None):
        extension = 0
        if depth == maxDepth or depth == maxDepthExtension:
            evaluation = self.evaluate(board=board)
            return lastMove, evaluation
        
        hashValue = self.compute_hash(board)
        
        bestEval = -1000000 if isMaximizingPlayer == 1 else 1000000
        bestMove = lastMove
        moves = board.generate_legal_moves()
        sorted_moves = self.order_moves(moves=moves, board=board)
        if prevBestMove is not None:
            board.move_piece(prevBestMove)
            if board.is_in_check():
                extension += 2
            if prevBestMove.capturedPiece != Pieces.Empty:
                extension += 1
            self.nodes += 1
            thisMove, evaluation = self.search(board=board, depth=depth+1, maxDepth=maxDepth+extension, maxDepthExtension=maxDepthExtension, isMaximizingPlayer=-isMaximizingPlayer, alpha=alpha, beta=beta, lastMove=prevBestMove)
            board.undo_move(prevBestMove)
            extension = 0
            if isMaximizingPlayer == 1:
                bestEval = max(bestEval, evaluation)
                alpha = max(alpha, bestEval)
            else:
                bestEval = min(bestEval, evaluation)
                beta = min(beta, bestEval)
            if bestEval == evaluation:
                bestMove = prevBestMove
        for move in sorted_moves:
            if self.thinkTimeOut:
                break
            if not board.move_is_legal(move, board):
                continue
            board.move_piece(move)
            if self.gameStates.get(str(board.board)) == 2:
                print("Yes")
                evaluation = 0
            else:
                hashValue ^= self.zobrist[move.startSquare][board.board[move.startSquare]]
                hashValue ^= self.zobrist[move.endSquare][board.board[move.endSquare]]
                if not hashValue & self.mask in self.transpositionTable:
                    if board.is_in_check():
                        extension += 2
                    if move.capturedPiece != Pieces.Empty:
                        extension += 1
                    self.nodes += 1
                    thisMove, evaluation = self.search(board=board, depth=depth+1, maxDepth=maxDepth+extension, maxDepthExtension=maxDepthExtension, isMaximizingPlayer=-isMaximizingPlayer, alpha=alpha, beta=beta, lastMove=move)
                else:
                    self.hashLookups += 1
                    thisMove, evaluation = self.transpositionTable.get(hashValue & self.mask)
            board.undo_move(move)
            hashValue ^= self.zobrist[move.startSquare][board.board[move.startSquare]]
            hashValue ^= self.zobrist[move.endSquare][board.board[move.endSquare]]
            extension = 0
            if isMaximizingPlayer == 1:
                bestEval = max(bestEval, evaluation)
                if bestEval > beta:
                    self.killerMoves[move] = 1
                    break
                alpha = max(alpha, bestEval)
            else:
                bestEval = min(bestEval, evaluation)
                if bestEval < alpha:
                    break
                beta = min(beta, bestEval)
            if self.thinkTimeOut:
                break
            if bestEval == evaluation:
                bestMove = move
        self.transpositionTable[hashValue & self.mask] = [bestMove, bestEval]
        return bestMove, bestEval
    
    def evaluate(self, board):
        evaluation = 0
        whiteMoves = board.generate_legal_moves(turn=Pieces.White)
        blackMoves = board.generate_legal_moves(turn=Pieces.Black)

        if board.turn == Pieces.White and not board.has_legal_moves():
            if board.is_checkmate(turn=Pieces.Black):
                return 1000000
            else: return 0
        elif board.turn == Pieces.Black and not board.has_legal_moves():
            if board.is_checkmate(turn=Pieces.White):
                return -1000000
            else: return 0 

        mobility = len(whiteMoves) - len(blackMoves)

        currentValue = sum([Pieces().get_piece_value(piece=piece & Pieces.pieceMask) for piece in board.board]) - 40_000
        currentSplit = min(1, currentValue / self.maxValue)
        currentPawnTable = np.array(self.bgpawnTable) * currentSplit + np.array(self.egpawnTable) * (1 - currentSplit)
        currentKingTable = np.array(self.mgKingTable) * currentSplit + np.array(self.egKingTable) * (1 - currentSplit)

        for index, piece in enumerate(board.board):
            if piece & Pieces.pieceMask == Pieces.Pawn:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * (Pieces.Value.Pawn + currentPawnTable[index]) if offset == 1 else offset * (Pieces.Value.Pawn + currentPawnTable[::-1][index])
            if piece & Pieces.pieceMask == Pieces.Knight:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * (Pieces.Value.Knight + self.knightTable[index]) if offset == 1 else offset * (Pieces.Value.Knight + self.knightTable[::-1][index])
            if piece & Pieces.pieceMask == Pieces.Bishop:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * (Pieces.Value.Bishop + self.bishopTable[index]) if offset == 1 else offset * (Pieces.Value.Bishop + self.bishopTable[::-1][index])
            if piece & Pieces.pieceMask == Pieces.Rook:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * (Pieces.Value.Rook + self.rookTable[index]) if offset == 1 else offset * (Pieces.Value.Rook + self.rookTable[::-1][index])
            if piece & Pieces.pieceMask == Pieces.Queen:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * (Pieces.Value.Queen + self.queenTable[index]) if offset == 1 else offset * (Pieces.Value.Queen + self.queenTable[::-1][index])
            if piece & Pieces.pieceMask == Pieces.King:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * (Pieces.Value.King + currentKingTable[index]) if offset == 1 else offset * (Pieces.Value.King + currentKingTable[::-1][index])

        evaluation += (0.1 * mobility)
        
        return evaluation / 100
    
    def order_moves(self, moves, board):
        scoreGuesses = [0 for move in moves]
        for index, move in enumerate(moves):
            if move in self.killerMoves:
                scoreGuesses[index] -= self.killerBias
            if move.capturedPiece != Pieces.Empty:
                scoreGuesses[index] += 10 * Pieces().get_piece_value(move.capturedPiece & Pieces.pieceMask) - Pieces().get_piece_value(move.movedPiece & Pieces.pieceMask)
            if move.flag == Move.Flag.promote:
                scoreGuesses[index] += Pieces().get_piece_value(move.movedPiece & Pieces.pieceMask)
            if board.target_is_attacked(turn=board.turn, board=board.board, targetSquare=move.endSquare):
                scoreGuesses[index] -= Pieces().get_piece_value(move.movedPiece & Pieces.pieceMask)
        tups = zip(scoreGuesses, moves)
        moves = sorted(list(tups), key=lambda x: x[0])
        return [move[1] for move in list(moves)]