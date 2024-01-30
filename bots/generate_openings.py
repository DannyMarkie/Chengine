import sys
sys.path.insert(1, 'C:/Users/Danny/Documents/Programming/ai/games/pythonChess/git/Chengine')

from core.move import Move
from core.board import Board

class GenerateOpenings:
    def from_pgn(self, file):
        with open(file) as pgn_file:
            output = pgn_file.read()
            split = output.split('\n')
            for line in split:
                board = Board()
                if line != '' and line[0] == '1' and line[1] == '.':
                    line = [move if not move[0].isnumeric() else move[2:] for move in line.split()]
                    for index, notation in enumerate(line):
                        print(f"notation: {notation}")
                        move = board.from_algebraic(notation)
                        print(f"move: ({move.startSquare}, {move.endSquare})")
                        board.move_piece(move)
                        if index > 7:
                            break


if __name__ == "__main__":
    file = 'bots/opening_book/Carlsen.pgn'
    GenerateOpenings().from_pgn(file)