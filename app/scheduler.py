import pandas as pd
import random
from collections import Counter
from itertools import combinations
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# read files
def read_file(fname='24FALL_USC_OPEN_TEST.xlsx'):
    f = pd.read_excel(fname, engine='openpyxl')
    return f

# split player names, compute weights
# match = [team1_names, team2_names, category, flight, weight]
def get_match_info(f):
    # get all player's name
    player1s = f['team1'].tolist()
    player2s = f['team2'].tolist()
    categories = f['category'].tolist()
    flights = f['flight']
            
    # analyze each player's name and their total games
    players = {}
    matches = []
    for player1, player2, category, flight in zip(player1s, player2s, categories, flights):
        # men's single, women's single
        if category == "MS" or category == "WS":
            players[player1] = players.get(player1, 0) + 1
            players[player2] = players.get(player2, 0) + 1
            matches.append([[player1], [player2], category, flight])
        # men's doubles, women's double, mixed doubles
        else:
            p1s = [p.strip() for p in player1.strip().split('/')]
            # print(p1s)
            for p in p1s:
                players[p] = players.get(p, 0) + 1
            p2s = [p.strip() for p in player2.strip().split('/')]
            # print(p2s)
            for p in p2s:
                players[p] = players.get(p, 0) + 1
            matches.append([p1s, p2s, category, flight])
            
    # compute weight of each match
    for m in matches:
        if m[2] == "MS" or m[2] == "WS":
            m.append(players[m[0][0]] + players[m[1][0]])
        else:
            total = 0
            for p in m[0]:
                total += players[p]
            for p in m[1]:
                total += players[p]
            m.append(total / 2)
    return matches

# Calculate the weight of each match
def count_player_matches(matches):
    counter = Counter()
    for m in matches:
        for p in m[0] + m[1]:
            counter[p] += 1
    return counter

def calc_weight(match, player_counts):
    p1s, p2s = match[0], match[1]
    if len(p1s) == 1 and len(p2s) == 1:  # single
        return player_counts[p1s[0]] + player_counts[p2s[0]]
    else:  # doubles
        return (sum(player_counts[p] for p in p1s) + sum(player_counts[p] for p in p2s)) / 2

def update_weights(matches, player_counts):
    for match in matches:
        match[4] = calc_weight(match, player_counts)
    return matches

def update_remaining_weights(matches):
    """update remaining weights based on each player's remaining matches"""
    player_counts = {}
    # calculate the remaining match for each player
    for match in matches:
        for p in set(match[0]) | set(match[1]):
            player_counts[p] = player_counts.get(p, 0) + 1
    
    # update weight of each match (match weight = weight of team 1 + weight of team 2)
    updated_matches = []
    for match in matches:
        players = set(match[0]) | set(match[1])
        new_weight = sum(player_counts.get(p, 0) for p in players)
        updated_match = (*match[:-1], new_weight)
        updated_matches.append(updated_match)
    return updated_matches

# print sorted match
def print_sorted_match(matches):
    sorted_match = sorted(matches, key=lambda x:x[4], reverse=True)
    print('='*100)
    print('Sorted match:')
    for m in sorted_match:
        print(m)
    print('='*100)

# GREEDY ALGORITHM
def scheduler(matches, total_court, monte_carlo=False):
    batches = []
    prev_batch_players = set()
    
    while matches:
        # weight
        matches_sorted = sorted(matches, key=lambda m: -m[4])  
        
        batch = []
        players_in_batch = set()
        remaining = []
        candidates = []  
        
        # collect the valid matches, and put them into the candidate pool 
        for match in matches_sorted:
            p1s, p2s = set(match[0]), set(match[1])
            if (not (p1s & players_in_batch) and \
                not (p2s & players_in_batch) and \
                not (p1s & prev_batch_players) and \
                not (p2s & prev_batch_players)):
                candidates.append(match)
            else:
                remaining.append(match)
        
        # Monte Carlo, randomly fill the batch
        while len(batch) < total_court and candidates:
            if monte_carlo:
                # randomly choose one match
                selected = random.choice(candidates)
            else:
                # original greedy algo, pick the highest weight match
                selected = candidates[0]  
            
            batch.append(selected)
            candidates.remove(selected)
            # update players in batch
            players_in_batch.update(selected[0])
            players_in_batch.update(selected[1])
            
            # dynamically update the candidate pool: remove confilct match, add new candidates
            new_candidates = []
            for candidate in candidates:
                cp1, cp2 = set(candidate[0]), set(candidate[1])
                if not (cp1 & players_in_batch or cp2 & players_in_batch):
                    new_candidates.append(candidate)
                else:
                    remaining.append(candidate)
            candidates = new_candidates
        
        # if this batch can't schedule any match, then return
        if not batch:
            break
            
        batches.append(batch)
        prev_batch_players = players_in_batch
        matches = remaining + candidates  # the remaining match will go into next round
        matches = update_remaining_weights(matches)  # update weights

    
    
    return fit_remaining_into_batch(batches, matches, total_court)

# fit the remaining match into batch that are not full
def fit_remaining_into_batch(batches, remaining, total_court, monte_carlo=True):
    if not remaining:
        return batches, remaining, 0
    
    player_last_batch = {}
    total_inserted = 0

    # initialize the last batch of each player
    for batch_idx, batch in enumerate(batches):
        for match in batch:
            for player in set(match[0]) | set(match[1]):
                player_last_batch[player] = batch_idx

    while True:
        inserted_this_round = False

        # update weights and sort by weight (large -> small)
        remaining = update_remaining_weights(remaining)
        remaining = sorted(remaining, key=lambda x: -x[4])

        for batch_idx, batch in enumerate(batches):
            # get the current batch players name set
            current_batch_players = set()
            for m in batch:
                current_batch_players.update(m[0])
                current_batch_players.update(m[1])
            
            # collect all insertable match, and save them into the candidate pool
            candidate_matches = []
            for j, match in enumerate(remaining):
                players = set(match[0]) | set(match[1])

                # check if players of potential inserting match are in current batch or not
                if players & current_batch_players:
                    continue
                else:
                    candidate_matches.append((j, match))
            
            # if the candidate is not empty, then randomly insert
            if candidate_matches:
                if monte_carlo:
                    selected_index, selected_match = random.choice(candidate_matches)
                else:
                    # default choose the hightest weight
                    selected_index, selected_match = candidate_matches[0]
                
                batch.append(selected_match)
                
                players = set(selected_match[0]) | set(selected_match[1])
                current_batch_players.update(players)
                for p in players:
                    player_last_batch[p] = batch_idx
                remaining.pop(selected_index)
                total_inserted += 1
                inserted_this_round = True
                break  # break after insertion

        if not inserted_this_round:
            break  # if there's no insertion, then break

    # handle the remaining match, concat at the end
    if remaining:
        new_batches, remaining = schedule_remaining_simple(remaining, total_court)
        batches.extend(new_batches)
        total_inserted += sum(len(b) for b in new_batches)

    # print(f'insert {total_inserted} matches into schedule')
    return batches, remaining, total_inserted

# schedule the remaining match into batch that are not full
def schedule_remaining_simple(remaining, total_court):
    batches = []
    while remaining:
        batch = []
        players_in_batch = set()
        i = 0
        while i < len(remaining) and len(batch) < total_court:
            match = remaining[i]
            players = set(match[0]) | set(match[1])
            if not (players & players_in_batch):  # only check current_batch
                batch.append(match)
                players_in_batch.update(players)
                remaining.pop(i)
            else:
                i += 1
        batches.append(batch)
    return batches, remaining

# annotate consecutive players
def annotate_consecutive_players(batches):
    prev_batch_players = set()
    new_batches = []
    for batch in batches:
        new_batch = []
        current_batch_players = set()
        for match in batch:
            players = set(match[0]) | set(match[1])
            # find consecutive players (if current player plays in this and previous batch)
            consecutive_players = [p for p in players if p in prev_batch_players]
            marked_match = list(match) + [consecutive_players]
            new_batch.append(marked_match)
            current_batch_players.update(players)
        prev_batch_players = current_batch_players  # update previous batch players
        new_batches.append(new_batch)
    return new_batches


# backtracking method
def can_batch(batch, prev_batch_players):
    players_in_batch = set()
    for match in batch:
        p1s, p2s = set(match[0]), set(match[1])
        if (p1s | p2s) & players_in_batch:
            return False
        if (p1s | p2s) & prev_batch_players:
            return False
        players_in_batch.update(p1s)
        players_in_batch.update(p2s)
    return True

# backtracking method
def backtracking_scheduler(matches, total_court, batches=None, prev_batch_players=None):
    # print('called')
    if batches is None:
        batches = []
    if prev_batch_players is None:
        prev_batch_players = set()

    if not matches:
        return batches  # all matches are scheduled

    if len(matches) >= total_court:
        for batch in combinations(matches, total_court):
            if can_batch(batch, prev_batch_players):
                remaining = [m for m in matches if m not in batch]
                players_in_batch = set()
                for match in batch:
                    players_in_batch.update(match[0])
                    players_in_batch.update(match[1])
                result = backtracking_scheduler(remaining, total_court, batches + [list(batch)], players_in_batch)
                if result is not None:
                    return result
    else:
        # last batch, size may not to be fixed
        for batch_size in range(len(matches), 0, -1):
            for batch in combinations(matches, batch_size):
                if can_batch(batch, prev_batch_players):
                    remaining = [m for m in matches if m not in batch]
                    players_in_batch = set()
                    for match in batch:
                        players_in_batch.update(match[0])
                        players_in_batch.update(match[1])
                    result = backtracking_scheduler(remaining, total_court, batches + [list(batch)], players_in_batch)
                    if result is not None:
                        return result

    return None  # match can't be scheduled

# write schedule to excel file
def write_schedule(batches, total_court, filename):
    rows = []
    for batch_idx, batch in enumerate(batches, 1):
        for match in batch:
            consecutive_players = match[5] if len(match) > 5 else []
            consecutive_str = ", ".join(consecutive_players) if consecutive_players else ""
            rows.append({
                'Batch': batch_idx,
                'Player1s': ' / '.join(match[0]),
                'Player2s': ' / '.join(match[1]),
                'Category': match[2],
                'Flight': match[3],
                'Affected_Players': consecutive_str
            })
        if len(batch) < total_court:
            for _ in range(total_court - len(batch)):
                rows.append({
                    'Batch': batch_idx,
                    'Player1s': None,
                    'Player2s': None,
                    'Category': None,
                    'Flight': None,
                    'Affected_Players': None
                })

    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False, sheet_name='MatchSchedule')

    # use openpyxl to fill color
    wb = load_workbook(filename)
    ws = wb['MatchSchedule']
    fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # yellow

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        consecutive_cell = row[5]
        if consecutive_cell.value:
            for cell in row:
                cell.fill = fill

    wb.save(filename)

# print final schedule
def print_final_schedule(batches, remaining):
    print('='*100)
    for batch_idx, batch in enumerate(batches, 1):
        for match in batch:
            print(f'{batch_idx}\t{match}')
    print('='*100)
    print('='*100)
    print('these match can not be assigned:')
    for r in remaining:
        print(r)
    print('='*100)

# generate schedule using greedy algorithm
def generate_schedule(f, total_court, output_fname):
    # f = read_file(fname)
    
    matches = get_match_info(f)
    
    # print_sorted_match(matches)
    
    batches, remaining, total_insert = scheduler(matches, total_court)

    batches = annotate_consecutive_players(batches)
    
    write_schedule(batches, total_court, output_fname)
    
    print_final_schedule(batches, remaining)

# generating schedule using backtracking(TLE)
def generate_schedule_backtracking(fname, total_court):
    f = read_file(fname)
    matches = get_match_info(f)

    schedule = backtracking_scheduler(matches, total_court)
    write_schedule(schedule, total_court, 'backtracking_schedule.xlsx')
    if schedule:
        for i, batch in enumerate(schedule):
            print(f"Round {i+1}: {batch}")
    else:
        print("No feasible schedule found.")

# example: You need to have three variables to run the whole process
# how many courts in the arena
# total_court = 6
# file_name = '24FALL_USC_OPEN_TEST.xlsx'
# output_schedule_file_name = '24Fall_USC_OPEN_schedule.xlsx'

# generate_schedule(file_name, total_court, output_schedule_file_name)