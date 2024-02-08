from core.board import Board
from core.pieces import Pieces
from core.move import Move
from core.match import Match
from bots.random_bot import RandomBot
from bots.bot_v1_negamax import NegaMaxV1
from bots.bot_v2_move_ordering import MoveOrderingV2
from bots.bot_v3_iterative_deepening import IterativeDeepeningV3
from bots.bot_v4_piece_tables import PieceTablesV4
from bots.bot_v5_transposition_table import TranspositionTableV5
from bots.bot_v6_killer_moves import KillerMovesV6
from tests.test_board import TestBoard
import time
import cProfile

numMatches = 1
renderGames = True

winners = []
# cProfile.run('KillerMovesV6().get_move()', sort='tottime')
# cProfile.run('TranspositionTableV5().get_move()', sort='tottime')
start_time = time.time()
print(f"Started playing matches...")
for game in range(0, numMatches):
    match = Match(bot1=TranspositionTableV5(), bot2=RandomBot(), board=Board(render=renderGames))
    winner = match.play()
    winners.append(winner)
end_time = time.time()
print(f"\nTime taken for {numMatches} matches = {end_time - start_time:0.2f}s")

print(f"White wins: {len([winner for winner in winners if winner == Pieces.White])}")
print(f"Draw: {len([winner for winner in winners if winner == None])}")
print(f"Black wins: {len([winner for winner in winners if winner == Pieces.Black])}")