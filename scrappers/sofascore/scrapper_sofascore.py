import subprocess
import sys

if __name__ == "__main__":
    script_paths = ["get_players_ids.py", "players_details_sofascore_scrapper.py", "get_ratings_from_sofascore.py"]
    for script_path in script_paths:
        try:
            subprocess.run(["python", script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing {script_path}: {e}")
            sys.exit(1)
