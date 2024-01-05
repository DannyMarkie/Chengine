from core.pieces import Pieces

class Move:
    class Flag:
        en_passant = 1
        castle = 2
        promote = 4

    def __init__(self, startSquare=0, endSquare=0, movedPiece=Pieces.Empty, capturedPiece=Pieces.Empty, flag=0b0000) -> None:
        self.startSquare = startSquare
        self.endSquare = endSquare
        self.movedPiece = movedPiece
        self.capturedPiece = capturedPiece
        self.flag = flag