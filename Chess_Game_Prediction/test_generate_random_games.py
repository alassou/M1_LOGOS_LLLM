"""This algorithm generate one chess game, 
with n% of random moves (each move have n% chance to be random, but legal)."""

import chess
import chess.engine
import chess.pgn
from datetime import datetime
import random

def random_move(board):
    """Make a random valid move on the board."""
    legal_moves = list(board.legal_moves)
    if legal_moves:
        move = random.choice(legal_moves)
        board.push(move)
        return move
    return None

def generate_single_game(engine_path):
    """Generate a single chess game with Stockfish, logging random moves to the terminal."""
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    engine.configure({
        "Threads": 1,
        "Skill Level": 10
    })
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Event"] = "Simulated Game"
    game.headers["Site"] = "Local Simulation"
    game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    game.headers["Round"] = "?"
    game.headers["White"] = "Player1 (1800)"
    game.headers["Black"] = "Player2 (1800)"
    game.headers["Result"] = "*"
    node = game

    while not board.is_game_over():
        if random.random() < 0.05:  # 5% chance to make a random move
            move = random_move(board)
            if move:
                print(f"Random move made: {move.uci()}")
        else:
            result = engine.play(board, chess.engine.Limit(depth=2))
            move = result.move
            board.push(move)

        if move:
            node = node.add_variation(move)

    game.headers["Result"] = board.result()
    engine.quit()
    return game

if __name__ == '__main__':
    stockfish_path = "/opt/homebrew/Cellar/stockfish/16.1/bin/stockfish"
    game = generate_single_game(stockfish_path)
    print(game)
