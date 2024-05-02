import csv
import os

import pandas as pd
from tqdm import tqdm

flags_file_path = os.path.join('..', 'data', 'flags', 'flags_KM.csv')
player_club_minutes_file_path = os.path.join('..', 'data', 'transfermarkt', 'player_club_minutes.csv')
player_values_file_path = os.path.join('..', 'data', 'transfermarkt', 'player_value.csv')


def get_all_players_count(df):
    if 'id' in df.columns:
        liczba_unikalnych_id = df['id'].nunique()
        return liczba_unikalnych_id
    else:
        print('W pliku nie ma kolumny \'id\'')


def get_sum_of_minutes_in_game(df):
    if 'minutes' in df.columns:
        df['minutes'] = pd.to_numeric(df['minutes'], errors='coerce')
        suma = df['minutes'].sum()
        return suma
    else:
        print('W pliku nie ma kolumny \'minutes\'')


def get_percent_of_average(player_club_minutes_file_path):
    df = pd.read_csv(player_club_minutes_file_path, low_memory=False)
    number_of_players = get_all_players_count(df)
    sum_minutes_in_game = get_sum_of_minutes_in_game(df)
    average_minutes_per_player = sum_minutes_in_game / number_of_players
    return average_minutes_per_player * 0.01


def create_flag_file(flags_file_path):
    columns = ["id", "season", "team", "ZERO_EXP", "ALWAYS_ON_BENCH", "PROGRESS_SINCE_NEW_TEAM",
               "SAME_RESULTS_FOR_LONG_TIME"]
    if not os.path.exists(flags_file_path):
        with open(flags_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
        print(f"Plik '{flags_file_path}' został stworzony z nagłówkami kolumn.")
    else:
        print(f"Plik '{flags_file_path}' już istnieje.")


def get_season_dates(season):
    years = season.split('/')
    start_date = f"01.08.{years[0]}"
    end_date = f"31.07.{years[1]}"
    start_date_df = pd.to_datetime(start_date, format='%d.%m.%Y', errors='coerce')
    end_date_df = pd.to_datetime(end_date, format='%d.%m.%Y', errors='coerce')
    return start_date_df, end_date_df


def get_club_name(player_values, season, player_id):
    start_season, end_season = get_season_dates(season)
    player_values.loc[:, 'date'] = pd.to_datetime(player_values['date'], format='%d.%m.%Y',
                                                  errors='coerce')
    filtered_player_value_df = player_values[
        (player_values['id'] == player_id) & (player_values['date'] >= start_season) & (
                player_values['date'] <= end_season)]
    if len(filtered_player_value_df) == 0:
        team = "UNKNOWN"
    elif len(filtered_player_value_df) == 1:
        team = filtered_player_value_df['club'].iloc[0]
    else:
        team = "; ".join(filtered_player_value_df['club'].unique().tolist())
    return team


def get_prev_season(season):
    start_year, end_year = season.split('/')
    start_year = int(start_year) - 1
    end_year = int(end_year) - 1
    prev_season = f"{start_year}/{end_year}"
    return prev_season


def generate_progress_since_new_team_flag(season, player_value_df, filtered_player_club_minutes_by_id_df, flags_df):
    start_current_season, end_current_season = get_season_dates(season)

    prev_season = get_prev_season(season)
    start_prev_season, end_prev_season = get_season_dates(prev_season)

    player_value_df.loc[:, 'date'] = pd.to_datetime(player_value_df['date'], format='%d.%m.%Y', errors='coerce')
    prev_season_club_df = player_value_df[
        (player_value_df['date'] >= start_prev_season) & (player_value_df['date'] <= end_prev_season)].copy()
    current_season_club_df = player_value_df[
        (player_value_df['date'] >= start_current_season) & (player_value_df['date'] <= end_current_season)].copy()
    if prev_season_club_df.empty or current_season_club_df.empty:
        progress_since_new_team_flag = ""
    else:
        prev_season_club_df.sort_values(by='date', inplace=True, ascending=False)
        current_season_club_df.sort_values(by='date', inplace=True)
        prev_season_club = prev_season_club_df.iloc[0]['club']
        current_season_club = current_season_club_df.iloc[0]['club']

        if prev_season_club == current_season_club:
            progress_since_new_team_flag = ""
        else:
            progress_flag = False

            minutes_in_current_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == season][
                    'minutes'].sum()
            minutes_in_prev_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == prev_season][
                    'minutes'].sum()
            if minutes_in_prev_season < minutes_in_current_season:
                progress_flag = True

            own_goal_in_current_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == season][
                    'own_goal'].sum()
            own_goal_in_prev_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == prev_season][
                    'own_goal'].sum()

            if own_goal_in_prev_season < own_goal_in_current_season:
                progress_flag = True

            matches_in_current_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == season][
                    'matches'].sum()
            matches_in_prev_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == prev_season][
                    'matches'].sum()
            if matches_in_prev_season < matches_in_current_season:
                progress_flag = True

            if progress_flag:
                progress_since_new_team_flag = "PROGRESS_SINCE_NEW_TEAM"
            else:
                progress_since_new_team_flag = ""
    return progress_since_new_team_flag


def generate_same_results_for_long_time_flag(season, player_value_df, filtered_player_club_minutes_by_id_df, flags_df):
    start_current_season, end_current_season = get_season_dates(season)

    prev_season = get_prev_season(season)
    start_prev_season, end_prev_season = get_season_dates(prev_season)

    player_value_df.loc[:, 'date'] = pd.to_datetime(player_value_df['date'], format='%d.%m.%Y', errors='coerce')
    prev_season_club_df = \
        player_value_df[
            (player_value_df['date'] >= start_prev_season) & (player_value_df['date'] <= end_prev_season)].copy()
    current_season_club_df = player_value_df[
        (player_value_df['date'] >= start_current_season) & (player_value_df['date'] <= end_current_season)].copy()

    if len(prev_season_club_df) == 0 or len(current_season_club_df) == 0:
        same_results_for_long_time_flag = ""
    else:
        prev_season_club_df.sort_values(by='date', inplace=True, ascending=False)
        current_season_club_df.sort_values(by='date', inplace=True)

        prev_season_club = prev_season_club_df.iloc[0]['club']
        current_season_club = current_season_club_df.iloc[0]['club']

        if prev_season_club == current_season_club:
            same_results_for_long_time_flag = ""
        else:
            same_results_for_long_time_flag = False

            minutes_in_current_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == season][
                    'minutes'].sum()
            minutes_in_prev_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == prev_season][
                    'minutes'].sum()
            if minutes_in_prev_season >= minutes_in_current_season:
                same_results_for_long_time_flag = True

            own_goal_in_current_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == season][
                    'own_goal'].sum()
            own_goal_in_prev_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == prev_season][
                    'own_goal'].sum()

            if own_goal_in_prev_season >= own_goal_in_current_season:
                same_results_for_long_time_flag = True

            matches_in_current_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == season][
                    'matches'].sum()
            matches_in_prev_season = \
                filtered_player_club_minutes_by_id_df[filtered_player_club_minutes_by_id_df['season'] == prev_season][
                    'matches'].sum()
            if matches_in_prev_season >= matches_in_current_season:
                same_results_for_long_time_flag = True

            if same_results_for_long_time_flag:
                same_results_for_long_time_flag = "SAME_RESULT_FOR_LONG_TIME"
            else:
                same_results_for_long_time_flag = ""
    return same_results_for_long_time_flag


def generate_flags(chosen_flags, unique_ids, player_club_minutes, player_values, flags_df):
    row_count = sum(1 for _ in unique_ids)
    progress_bar = tqdm(total=row_count, desc='Generating flags: ', unit='row', dynamic_ncols=True)
    processed_rows = 0
    for player_id in unique_ids:
        processed_rows += 1
        progress_bar.update(1)
        filtered_player_club_minutes_by_id_df = player_club_minutes[player_club_minutes['id'] == player_id]
        unique_seasons = filtered_player_club_minutes_by_id_df['season'].unique().tolist()
        for season in unique_seasons:
            team = get_club_name(player_values, season, player_id)
            filtered_player_club_minutes_by_id_and_season_df = filtered_player_club_minutes_by_id_df[
                filtered_player_club_minutes_by_id_df['season'] == season]
            filtered_player_value_by_id_df = player_values[player_values['id'] == player_id]
            if "ZERO_EXP" in chosen_flags:
                zero_exp_flag = generate_zero_exp_flag(filtered_player_club_minutes_by_id_and_season_df, flags_df)
            else:
                zero_exp_flag = ""

            if "ALWAYS_ON_BENCH" in chosen_flags:
                always_on_bench_flag = generate_always_on_bench_flag(filtered_player_club_minutes_by_id_and_season_df,
                                                                     flags_df)
            else:
                always_on_bench_flag = ""
            if "PROGRESS_SINCE_NEW_TEAM" in chosen_flags:
                progress_since_new_team_flag = generate_progress_since_new_team_flag(season,
                                                                                     filtered_player_value_by_id_df,
                                                                                     filtered_player_club_minutes_by_id_df,
                                                                                     flags_df)
            else:
                progress_since_new_team_flag = ""
            if "SAME_RESULTS_FOR_LONG_TIME" in chosen_flags:
                same_result_for_long_time_flag = generate_same_results_for_long_time_flag(season,
                                                                                          filtered_player_value_by_id_df,
                                                                                          filtered_player_club_minutes_by_id_df,
                                                                                          flags_df)
            else:
                same_result_for_long_time_flag = ""

            flags_df.loc[len(flags_df)] = [player_id, season, team, zero_exp_flag, always_on_bench_flag,
                                           progress_since_new_team_flag, same_result_for_long_time_flag]


def generate_zero_exp_flag(filtered_player_club_minutes_by_id_and_season_df, flags_df):
    minutes_in_game = filtered_player_club_minutes_by_id_and_season_df['minutes'].sum()
    percent_of_average = get_percent_of_average(player_club_minutes_file_path)
    if minutes_in_game < percent_of_average:
        player_zero_exp_flag = "ZERO_EXP"
    else:
        player_zero_exp_flag = ""
    return player_zero_exp_flag


def generate_always_on_bench_flag(filtered_player_club_minutes_by_id_and_season_df, flags_df):
    from_bench_no = filtered_player_club_minutes_by_id_and_season_df["from_bench"].sum()
    minutes_in_game = filtered_player_club_minutes_by_id_and_season_df['minutes'].sum()
    percent_of_average = get_percent_of_average(player_club_minutes_file_path)
    if minutes_in_game < percent_of_average and from_bench_no > 0:
        player_always_on_bench_flag = "ALWAYS_ON_BENCH"
    else:
        player_always_on_bench_flag = ""

    return player_always_on_bench_flag


def create_flag(player_values_file_path, player_club_minutes_file_path, flags_file_path, chosen_flags):
    player_values = pd.read_csv(player_values_file_path, low_memory=False)
    player_club_minutes = pd.read_csv(player_club_minutes_file_path, low_memory=False)
    flags_file = pd.read_csv(flags_file_path, low_memory=False)
    flags_df = pd.DataFrame(columns=flags_file.columns)

    unique_ids = player_values['id'].unique().tolist()

    generate_flags(chosen_flags, unique_ids, player_club_minutes, player_values, flags_df)
    return flags_df


def main():
    available_flags = [
        "ZERO_EXP",
        "ALWAYS_ON_BENCH",
        "SAME_RESULTS_FOR_LONG_TIME",
        "PROGRESS_SINCE_NEW_TEAM"
    ]

    print("Dostępne flagi do wygenerowania:")
    for index, flag in enumerate(available_flags, start=1):
        print(f"{index}. {flag}")

    chosen_indexes = input("Podaj numery flag, które chcesz wygenerować (np. 1, 2): ")

    try:
        chosen_indexes = [int(x.strip()) for x in chosen_indexes.split(',')]
    except ValueError:
        print("Błędny format danych wejściowych. Proszę użyć tylko liczb oddzielonych przecinkami.")
        return

    chosen_flags = [available_flags[i - 1] for i in chosen_indexes if 1 <= i <= len(available_flags)]

    print("Wybrane flagi to:")
    for flag in chosen_flags:
        print(flag)

    return chosen_flags


if __name__ == '__main__':
    chosen_flags = main()

    create_flag_file(flags_file_path)

    flag_df = create_flag(player_values_file_path, player_club_minutes_file_path, flags_file_path, chosen_flags)
    flags_file = pd.read_csv(flags_file_path, low_memory=False)
    pd.concat([flags_file, flag_df]).to_csv(flags_file_path, index=False)
