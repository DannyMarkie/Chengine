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

    def __eq__(self, __value: object) -> bool:
        return self.startSquare == __value.startSquare and self.endSquare == __value.endSquare and self.movedPiece == __value.movedPiece and self.capturedPiece == __value.capturedPiece and self.flag == __value.flag
    
    def __hash__(self) -> int:
        return hash(self.startSquare + self.endSquare + self.movedPiece + self.capturedPiece + self.flag)