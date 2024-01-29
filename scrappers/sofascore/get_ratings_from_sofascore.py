import csv
import json
import os

import requests
from tqdm import tqdm

headers = {
    'authority': 'api.sofascore.com',
    'accept': '*/*',
    'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"7dd2d62cd7"',
    'origin': 'https://www.sofascore.com',
    'referer': 'https://www.sofascore.com/',
    'sec-ch-ua': '"Chromium";v="118", "Opera GX";v="104", "Not=A?Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0',
    'If-Modified-Since': 'Wed, 25 Jan 2024 00:00:00 GMT'

}


def get_event_data(event, player_id):
    tournament_id = event.get("tournament", {}).get("uniqueTournament", {}).get("id", "")
    season_id = event.get("season", {}).get("id", "")
    ratings_response = requests.get(
        f'https://api.sofascore.com/api/v1/player/{player_id}/unique-tournament/{tournament_id}/season/{season_id}/last-ratings',
        headers=headers).json()
    ratings = ratings_response.get("lastRatings", [])
    rating_list = []
    for rating in ratings:
        rating_list.append(get_rating_from_event(rating))
    event_data = {'tournament_id': tournament_id, "season_id": season_id, "ratings": rating_list}
    return event_data


def get_player_events_data(sofascore_id, transfermarkt_id):
    events_response = requests.get(f'https://api.sofascore.com/api/v1/player/{sofascore_id}/events/last/0',
                                   headers=headers).json()
    events_data = events_response.get("events", [])
    event_list = []
    for event in events_data:
        event_data = get_event_data(event, sofascore_id)
        event_list.append(event_data)
    player_rating = {"sofascore_id": sofascore_id, "transfermarkt_id": transfermarkt_id, "events_rating": event_list}
    return player_rating


def get_players_ratings(players_id_src):
    players_rating = []
    with open(players_id_src, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        row_count = sum(1 for _ in csv_reader)
        csv_file.seek(0)
        progress_bar = tqdm(total=row_count, desc='Processing first CSV ', unit='row', dynamic_ncols=True)
        processed_rows = 0
        next(csv_reader)
        for row in csv_reader:
            processed_rows += 1
            progress_bar.update(1)
            sofascore_id = row['id_sofascore']
            transfermarkt_id = row['id_transfermarkt']
            if sofascore_id == "":
                player_rating = {"sofascore_id": sofascore_id, "transfermarkt_id": transfermarkt_id,
                                 "events_rating": ""}
                players_rating.append(player_rating)
            else:
                players_rating.append(get_player_events_data(sofascore_id, transfermarkt_id))

    return players_rating


def save_rating_into_json_file(players_rating_src, player_rating_list):
    with open(players_rating_src, "w", newline="") as json_file:
        json.dump(player_rating_list, json_file)


def get_rating_from_event(rating):
    event_rating = rating.get("rating", "")
    rating_data = {'rating': event_rating}
    return rating_data


if __name__ == '__main__':
    players_id_src = os.path.join('..', '..', 'data', 'players', 'players_ids.csv')
    players_rating_src = os.path.join('..', '..', 'data', 'sofascore', 'players_ratings.json')
    players_rating_list = get_players_ratings(players_id_src)
    save_rating_into_json_file(players_rating_src, players_rating_list)
