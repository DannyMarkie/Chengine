from bots.bot import Bot
import random

class RandomBot(Bot):
    def __init__(self) -> None:
        super().__init__()

    def get_move(self, board):
        moves = board.generate_legal_moves()
        indexes = []
        for index, move in enumerate(moves):
            if not board.move_is_legal(move, board):
                indexes.append(index)

        for index in sorted(indexes, reverse=True):
            del moves[index]
        return random.choice(moves)