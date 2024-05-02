"""This algorithm generate several number of chess games, 
at level 1800 elo (Stockfish) """

import chess
import chess.engine
import chess.pgn
from datetime import datetime
import concurrent.futures
import tqdm

def generate_single_game(engine_path):
    """Fonction pour générer une seule partie d'échecs avec Stockfish."""
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    # Configurer Stockfish pour utiliser un seul thread et un niveau de compétence ajusté.
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
        result = engine.play(board, chess.engine.Limit(depth=5))
        move = result.move
        board.push(move)
        node = node.add_variation(move)

    game.headers["Result"] = board.result()
    engine.quit()
    return game

def generate_chess_games(num_games, engine_path, output_file):
    """Fonction pour générer plusieurs parties d'échecs en parallèle."""
    games = []
    # Détecter automatiquement le nombre optimal de processus à utiliser.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Soumettre les tâches pour générer les parties.
        futures = [executor.submit(generate_single_game, engine_path) for _ in range(num_games)]
        # Progression de la génération des parties avec barre de progression.
        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=num_games, desc="Generating games"):
            games.append(future.result())

    # Écriture de toutes les parties générées dans un fichier PGN.
    with open(output_file, "w") as pgn_file:
        for game in games:
            print(game, file=pgn_file, end="\n\n")

if __name__ == '__main__':
    # Définition du chemin d'accès à Stockfish et du nombre de parties à générer.
    stockfish_path = "/opt/homebrew/Cellar/stockfish/16.1/bin/stockfish"
    output_pgn = "chess_games.pgn"
    total_games = 10000  # Modifier selon les besoins.
    generate_chess_games(total_games, stockfish_path, output_pgn)