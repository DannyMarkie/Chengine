from core.board import Board
from core.pieces import Pieces
from core.move import Move
from core.match import Match
from bots.random_bot import RandomBot
from tests.test_board import TestBoard
import time

numMatches = 100
renderGames = False

winners = []
start_time = time.time()
print(f"Started playing matches...")
for game in range(0, numMatches):
    match = Match(bot1=RandomBot(), bot2=RandomBot(), board=Board(render=renderGames))
    winner = match.play()
    winners.append(winner)
end_time = time.time()
print(f"\nTime taken for {numMatches} matches = {end_time - start_time:0.2f}s")

print(f"White wins: {len([winner for winner in winners if winner == Pieces.White])}")
print(f"Draw: {len([winner for winner in winners if winner == None])}")
print(f"Black wins: {len([winner for winner in winners if winner == Pieces.Black])}")