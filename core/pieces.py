class Pieces:
    class Value:
        Pawn = 100
        Bishop = 330
        Knight = 320
        Rook = 500
        Queen = 900
        King = 20000

    pieceMask = 0b00111
    colorMask = 0b11000

    Empty = 0

    Pawn = 1
    Bishop = 2
    Knight = 3
    Rook = 4
    Queen = 5
    King = 6

    White = 8
    Black = 16

    WhitePawn = White | Pawn
    WhiteBishop = White | Bishop
    WhiteKnight = White | Knight
    WhiteRook = White | Rook
    WhiteQueen = White | Queen
    WhiteKing = White | King

    BlackPawn = Black | Pawn
    BlackBishop = Black | Bishop
    BlackKnight = Black | Knight
    BlackRook = Black | Rook
    BlackQueen = Black | Queen
    BlackKing = Black | King

    def get_piece_value(self, piece):
        if piece == Pieces.Pawn:
            return self.Value.Pawn
        if piece == Pieces.Bishop:
            return self.Value.Bishop
        if piece == Pieces.Knight:
            return self.Value.Knight
        if piece == Pieces.Rook:
            return self.Value.Rook
        if piece == Pieces.Queen:
            return self.Value.Queen
        if piece == Pieces.King:
            return self.Value.King
        if piece == Pieces.Empty:
            return 0