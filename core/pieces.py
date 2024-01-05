class Pieces:
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