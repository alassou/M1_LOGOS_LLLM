"""This algorithm generate several number of chess games, 
with n% of random moves (each move have n% chance to be random, but legal). """

import chess
import chess.engine
import chess.pgn
from datetime import datetime
import concurrent.futures
import tqdm
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
    """Function to generate a single chess game with Stockfish, with a chance of random moves."""
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
        # Introduce a random move with 5% probability
        if random.random() < 0.05:
            move = random_move(board)
        else:
            result = engine.play(board, chess.engine.Limit(depth=5))
            move = result.move
            board.push(move)

        if move:
            node = node.add_variation(move)

    game.headers["Result"] = board.result()
    engine.quit()
    return game, board.fen()

def generate_chess_games(num_games, engine_path, output_file):
    """Function to generate multiple chess games in parallel."""
    games = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(generate_single_game, engine_path) for _ in range(num_games)]
        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=num_games, desc="Generating games with 5 percent of random moves"):
            game, final_fen = future.result()
            games.append((game, final_fen))

    with open(output_file, "w") as pgn_file:
        for game, _ in games:
            print(game, file=pgn_file, end="\n\n")

if __name__ == '__main__':
    stockfish_path = "/opt/homebrew/Cellar/stockfish/16.1/bin/stockfish"
    output_pgn = "chess_games_random.pgn"
    total_games = 10000
    generate_chess_games(total_games, stockfish_path, output_pgn)
