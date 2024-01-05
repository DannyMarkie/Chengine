from bots.bot import Bot
import random

class RandomBot(Bot):
    def __init__(self) -> None:
        super().__init__()

    def get_move(self, board):
        moves = board.generate_legal_moves()
        return random.choice(moves)