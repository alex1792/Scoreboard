import pandas as pd
import random

"""Read file and save all categories and flight in tb"""
def read_files(f, categories, filght):
    # file_name = 'contestants.xlsx'
    # f = pd.read_excel(file_name, engine='openpyxl')

    categories = ['MS', 'WS', 'MD', 'WD', 'XD']
    flight = ['A', 'B', 'C']


    # save all categories and flight in tb
    # eg: tb = {"MS-A": [], "MS-B": [], ...}
    tb = {}
    for category in categories:
        categorized = f.groupby(category)
        for name, group_df in categorized:
            teams = []
            if 'D' in category:
                player_name = [f"{first} {last}" for first, last in zip(group_df['First Name'], group_df['Last Name'])]
                partner_name = [pn for pn in group_df[f'{category} Partner Name']]
                for p1, p2 in zip(player_name, partner_name):
                    teams.append((p1, p2))
            else:
                player_names = [f"{first} {last}" for first, last in zip(group_df['First Name'], group_df['Last Name'])]
                for p in player_names:
                    teams.append((p,))
            # remove duplicates
            unique_teams = list(set(teams))
            key = f"{category}-{name}"
            tb[key] = unique_teams
    
    return tb

"""Group players into groups of num_player"""
def group_players(player_names, num_player):
    # copy player_names so that it won't mutate the original data
    player_names_copy = player_names.copy()
    
    # shuffle the player_names
    random.shuffle(player_names_copy)

    # group players, each group should be in size num_player
    groups = []
    while(len(player_names_copy) >= num_player):
        group = player_names_copy[:num_player]
        groups.append(group)
        player_names_copy = player_names_copy[num_player:]
    
    if len(player_names_copy) > 0:
        groups.append(player_names_copy)
    
    return groups

"""Print the matches"""
def print_match(matches):
    for m in matches:
        print(m)

"""Generate round-robin matches"""
def generate_round_robin(groups):
    round_robin_matches = []
    for group in groups:
        for i in range(len(group)):
            for j in range(i + 1, len(group), 1):
                match = {
                    "id": None,
                    "players": [group[i], group[j]],
                    "winner": None,
                    "next_match": None
                }
                round_robin_matches.append(match)

    return round_robin_matches

"""Update the round-robin matches"""
def update_round_robin(matches, player1, player2, winner):
    for i in range(len(matches)):
        if [player1, player2] == matches[i]['players']:
            matches[i]['winner'] = winner
            break
"""Check if the number of players is ideal"""
def is_ideal(num_players):
    return num_players in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]

"""Compute the min number that >= 2^n"""
def next_power_of_two(n):
    """compute the min number that >= 2^n"""
    if n < 1: return 1
    power = 1
    while power < n:
        power *= 2
    return power

"""Generate elimination matches"""
def generate_elimination(player_names):
    n = len(player_names)
    if n < 2:
        return [] if n == 0 else [{"id": "R1-M1", "players": [player_names[0], "BYE"], "winner": player_names[0]}]
    
    # compute how many byes
    total_slots = next_power_of_two(n)
    num_byes = total_slots - n
    
    # random shuffle players and pick byes
    random.shuffle(player_names)
    byes = player_names[:num_byes]      # bye players
    # active_players = player_names[num_byes:]  # not byes

    # random shuffle again
    random.shuffle(player_names)
    
    matches = []
    round_number = 1
    
    # first round (both byes and non-byes)
    current_round = []
    idx = 0
    while idx < len(player_names) - 1:
        match_id = f"R{round_number}-M{len(current_round)+1}"
        match = {}
        if player_names[idx] in byes:
            match = {
                "id": match_id,
                "players": [player_names[idx], "BYE"],
                "winner": player_names[idx],
                "next_match": None
            }
            idx += 1
        else:
            match = {
                "id": match_id,
                "players": [player_names[idx], player_names[idx + 1]],
                "winner": None,
                "next_match": None
            }
            idx += 2
        current_round.append(match)
        matches.append(match)
    
    # second round and so on
    while len(current_round) > 1:
        round_number += 1
        next_round = []
        
        
        for i in range(0, len(current_round), 2):
            # handle odd players (last round)
            if i+1 >= len(current_round):
                # set the last player 'BYE'
                last_player = f"Winner of {current_round[i]['id']}"
                next_round.append({
                    "id": f"R{round_number}-M{len(next_round)+1}",
                    "players": [last_player, "BYE"],
                    "winner": last_player,
                    "next_match": None
                })
                break
                
            match_id = f"R{round_number}-M{len(next_round)+1}"
            new_match = {
                "id": match_id,
                "players": [
                    f"Winner of {current_round[i]['id']}",
                    f"Winner of {current_round[i+1]['id']}"
                ],
                "winner": None,
                "next_match": None
            }
            next_round.append(new_match)
            matches.append(new_match)
            
            # update the next_match
            current_round[i]["next_match"] = match_id
            current_round[i+1]["next_match"] = match_id
        
        current_round = next_round
    
    return matches

"""Set matches[match_id]'s winner to winner, and update the next match"""
def update_elimination_match(matches, match_id, winner):
    next_match_id = ""
    for match in matches:
        if match['id'] == match_id:
            # update winner
            match['winner'] = winner
            next_match_id = match['next_match']
        if match['id'] == next_match_id:
            for i in range(len(match['players'])):
                if match_id in match['players'][i]:
                    match['players'][i] = winner
                    break

"""Format the team columns in excel file"""
def format_team(team):
    # handle team, it might be tuple, list, or None
    if isinstance(team, (tuple, list)):
        return ' / '.join(team)
    elif isinstance(team, str):
        return team
    else:
        return None

"""Save the matches to excel file"""
def to_excel(all_match, filename='all_match.xlsx'):
    rows = []
    for cat, matches in all_match.items():
        for match in matches:
            # print(match)
            rows.append({
                'ID': match['id'],
                'Category': cat[:2],
                'Flight': cat[-1],
                'Round': match['id'][1] if match.get('id') else None,
                'Team1': format_team(match['players'][0]),
                'Team2': format_team(match['players'][1]),
                'Winner': format_team(match.get('winner', None)),
                'Next Match': match.get('next_match', None)
            })

    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False, sheet_name='All_Match')

"""Generate the matches
    args:
        table: the table of players, a dictionary {'MS-A': [player1, player2, ...], 'MS-B': [player1, player2, ...], ...}
        rules: the rules of the matches, 'r' for round-robin, 'e' for elimination. When choosing 'r', the value should be a tuple of (num_player, num_group).
        filename: the filename of the excel file

    example:
        rules = {
            'MS-A': ['r', 4],
            'MS-B': ['e'],
            'MS-C': ['e'],
            'WS-A': ['e'],
            'WS-B': ['e'],
            'WS-C': ['e'],
            'MD-A': ['e'],
            'MD-B': ['e'],
            'MD-C': ['e'],
            'WD-A': ['e'],
            'WD-B': ['e'],
            'WD-C': ['e'],
            'XD-A': ['e'],
            'XD-B': ['e'],
            'XD-C': ['e']
        }
"""
def generate_match(f, categories, flight, rules, filename):
    try:
        table = read_files(f, categories, flight)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    all_match = {}
    for cat, rule in rules.items():
        if cat not in table:
            continue

        if len(rule) > 1 and rule[0] == 'r':  # Round Robin with group size
            group_size = rule[1]  # 使用傳入的分組大小
            group = group_players(table[cat], group_size)
            match = generate_round_robin(group)
            all_match[cat] = match
            # print_match(match)
        else:  # Elimination
            match = generate_elimination(table[cat])
            all_match[cat] = match
            # print_match(match)

    # print_match(all_match)
    to_excel(all_match, filename)  
    return None