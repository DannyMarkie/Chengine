from bots.bot import Bot
from core.pieces import Pieces

class NegaMaxV1(Bot):
    def __init__(self) -> None:
        super().__init__()

    def get_move(self, board):
        isMaximizingPlayer = 1 if board.turn == Pieces.White else -1
        move, evaluation = self.search(board=board, maxDepth=4, isMaximizingPlayer=isMaximizingPlayer)
        print(move.startSquare, evaluation*isMaximizingPlayer)
        return move

    def search(self, board, maxDepth, depth=0, maxExtendedDepth=3, isMaximizingPlayer=1, lastMove=None, alpha=-1000000, beta=1000000):
        extension = 0
        if depth == maxDepth or depth == maxExtendedDepth:
            evaluation = self.evaluate(board=board)
            return lastMove, evaluation
        
        bestEval = -1000000 if isMaximizingPlayer == 1 else 1000000
        bestMove = lastMove
        for move in board.generate_legal_moves():
            board.move_piece(move)
            if board.is_in_check():
                extension += 1
            if move.capturedPiece != Pieces.Empty:
                extension += 1
            thisMove, evaluation = self.search(board=board, depth=depth+1, maxDepth=maxDepth+extension, isMaximizingPlayer=-isMaximizingPlayer, alpha=alpha, beta=beta, lastMove=move)
            board.undo_move(move)
            extension = 0
            if isMaximizingPlayer == 1:
                bestEval = max(bestEval, evaluation)
                if bestEval > beta:
                    break
                alpha = max(alpha, bestEval)
            else:
                bestEval = min(bestEval, evaluation)
                if bestEval < alpha:
                    break
                beta = min(beta, bestEval)
            if bestEval == evaluation:
                bestMove = move
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
        evaluation += (0.05 * mobility)
        
        return evaluation / 100