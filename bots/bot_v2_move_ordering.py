from bots.bot import Bot
from core.pieces import Pieces
from core.move import Move
from core.board import Board

class MoveOrderingV2(Bot):
    def __init__(self) -> None:
        super().__init__()

    def get_move(self, board):
        isMaximizingPlayer = 1 if board.turn == Pieces.White else -1
        move, evaluation = self.search(board=board, maxDepth=2, isMaximizingPlayer=isMaximizingPlayer)
        print(move.startSquare, evaluation)
        return move

    def search(self, board, maxDepth, depth=0, maxExtendedDepth=3, isMaximizingPlayer=1, lastMove=None, alpha=-1000000, beta=1000000):
        extension = 0
        if depth == maxDepth or depth == maxExtendedDepth:
            evaluation = isMaximizingPlayer * self.evaluate(board=board)
            return lastMove, evaluation
        
        bestEval = -1000000
        bestMove = lastMove
        moves = board.generate_legal_moves()
        sorted_moves = self.order_moves(moves=moves, board=board)
        for move in sorted_moves:
            if not board.move_is_legal(move, board):
                continue
            board.move_piece(move)
            if board.is_in_check():
                extension += 1
            if move.capturedPiece != Pieces.Empty:
                extension += 1
            thisMove, evaluation = self.search(board=board, depth=depth+1, maxDepth=maxDepth+extension, isMaximizingPlayer=-isMaximizingPlayer, alpha=alpha, beta=beta, lastMove=move)
            evaluation = -evaluation
            bestEval = max(bestEval, evaluation)
            if bestEval == evaluation:
                bestMove = move
            alpha = max(alpha, bestEval)
            board.undo_move(move)
            extension = 0
            if beta <= alpha:
                break
        return bestMove, bestEval
    
    def evaluate(self, board):
        evaluation = 0
        if board.turn == Pieces.White:
            whiteMoves = board.generate_legal_moves()
            blackMoves = board.generate_legal_moves(turn=Pieces.Black)
        else:
            blackMoves = board.generate_legal_moves()
            whiteMoves = board.generate_legal_moves(turn=Pieces.White)

        if board.turn == Pieces.White and len(blackMoves) == 0:
            if board.is_checkmate(turn=Pieces.Black):
                return 1000000
            else: return 0
        elif board.turn == Pieces.Black and len(whiteMoves) == 0:
            if board.is_checkmate(turn=Pieces.White):
                return -1000000
            else: return 0 

        mobility = len(whiteMoves) - len(blackMoves)

        for piece in board.board:
            if piece & Pieces.pieceMask == Pieces.Pawn:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * Pieces.Value.Pawn
            if piece & Pieces.pieceMask == Pieces.Knight:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * Pieces.Value.Knight
            if piece & Pieces.pieceMask == Pieces.Bishop:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * Pieces.Value.Bishop
            if piece & Pieces.pieceMask == Pieces.Rook:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * Pieces.Value.Rook
            if piece & Pieces.pieceMask == Pieces.Queen:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * Pieces.Value.Queen
            if piece & Pieces.pieceMask == Pieces.King:
                offset = 1 if piece & Pieces.colorMask == Pieces.White else -1
                evaluation += offset * Pieces.Value.King

        # print(0.1*mobility, evaluation)
        evaluation += (0.1 * mobility)
        
        return evaluation / 100
    
    def order_moves(self, moves, board):
        scoreGuesses = [0 for move in moves]
        for index, move in enumerate(moves):
            if move.capturedPiece != Pieces.Empty:
                scoreGuesses[index] += 10 * Pieces().get_piece_value(move.capturedPiece & Pieces.pieceMask) - Pieces().get_piece_value(move.movedPiece & Pieces.pieceMask)
            if move.flag == Move.Flag.promote:
                scoreGuesses[index] += Pieces().get_piece_value(move.movedPiece & Pieces.pieceMask)
            if board.target_is_attacked(turn=board.turn, board=board.board, targetSquare=move.endSquare):
                scoreGuesses[index] -= Pieces().get_piece_value(move.movedPiece & Pieces.pieceMask)
        tups = zip(scoreGuesses, moves)
        moves = sorted(list(tups), key=lambda x: x[0])
        return [move[1] for move in list(moves)]