from ..models import Match, Group, db, Tournament, Schedule, ScheduleItem
from datetime import datetime, timedelta
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from collections import Counter

class TournamentScheduler:
    """use to generate schedule for a tournament"""
    def __init__(self, total_court):
        self.total_court = total_court
        self.scheduled_matches = []
        self.completed_matches = set()
        self.all_matches = []  # store all matches

    def schedule_tournament(self, matches, tournament_id):
        """schedule the tournament, handle the incomplete batches and dependencies"""
        # ensure matches is a list
        if not isinstance(matches, (list, tuple)):
            matches = [matches]
        
        self.all_matches = matches
        self.scheduled_matches = []  # reset the scheduled matches
        
        # 1. group the matches by round
        matches_by_round = self._group_by_round(matches)
        
        # 2. process the matches by round - ensure Round 1 is completely scheduled before processing Round 2
        for round_num in sorted(matches_by_round.keys()):
            round_matches = matches_by_round[round_num]
            
            # 3. initialize the candidate matches for the round
            candidate_matches = set()
            
            # 4. add the matches in the round to the candidate matches
            for match in round_matches:
                if self._can_schedule_match(match):
                    candidate_matches.add(match)
            
            # 5. schedule all matches in the round
            while candidate_matches:
                batch_matches = self._schedule_batch(candidate_matches)
                if not batch_matches:
                    break
                
                # 6. update the candidate matches
                for match in batch_matches:
                    candidate_matches.discard(match)
                    if match not in self.scheduled_matches:
                        self.scheduled_matches.append(match)
                
                # 7. re-check the matches that can be scheduled in the round
                self._update_candidate_matches_for_round(candidate_matches, round_matches)
        
        # 8. final stage: fill the remaining matches
        self._fill_remaining_matches()

        if tournament_id:
            schedule_data = {'start_time': '09:00', 'end_time': '18:00', 'match_duration': 30}
            self.create_schedule(tournament_id, schedule_data)

    def _group_by_round(self, matches):
        """group the matches by round"""
        matches_by_round = {}
        
        for match in matches:
            round_num = match.round or 1  # if no round, set to 1
            if round_num not in matches_by_round:
                matches_by_round[round_num] = []
            matches_by_round[round_num].append(match)
        
        return matches_by_round
    
    def _get_match_by_id(self, match_id):
        """get the match by match_id"""
        if not match_id:
            return None
        
        for match in self.all_matches:
            if match.id == match_id:
                return match
        return None
    
    def _schedule_batch(self, candidate_matches):
        """schedule a batch of matches"""
        selected_matches = []
        selected_players = set()
        
        # calculate the weight and sort
        weighted_matches = []
        for match in candidate_matches:
            weight = self._calculate_weight(match)
            weighted_matches.append((match, weight))
        
        weighted_matches.sort(key=lambda x: x[1], reverse=True)
        
        # greedy selection
        for match, weight in weighted_matches:
            if len(selected_matches) >= self.total_court:
                break
            
            match_players = self._get_match_players(match)
            if not (match_players & selected_players):
                selected_matches.append(match)
                selected_players.update(match_players)
        
        return selected_matches

    def _calculate_weight(self, match):
        """calculate the weight of the match"""
        weight = 0
        
        # 1. remaining games
        weight += self._compute_weight_for_remaining_games(match)
        
        # 2. resting time
        weight += self._compute_weight_for_resting_time(match)
        
        return weight
    
    def _compute_weight_for_remaining_games(self, match):
        """calculate the weight based on the remaining games"""
        weight = 0
        
        # get all players
        players = self._get_match_players(match)
        
        # calculate the remaining games for each player
        for player in players:
            remaining_games = self._get_remaining_games_for_player(player)
            weight += remaining_games * 10
        
        return weight
    
    def _get_match_players(self, match):
        """get all players in the match"""
        players = set()
        
        if match.event_type in ['MD', 'WD', 'XD']:
            if match.team1_player1_name:
                players.add(match.team1_player1_name)
            if match.team1_player2_name:
                players.add(match.team1_player2_name)
            if match.team2_player1_name:
                players.add(match.team2_player1_name)
            if match.team2_player2_name:
                players.add(match.team2_player2_name)
        else:
            if match.player1_name:
                players.add(match.player1_name)
            if match.player2_name:
                players.add(match.player2_name)
        
        return players
    
    def _get_remaining_games_for_player(self, player_name):
        """get the remaining games for the player"""
        remaining = 0
        
        for match in self.all_matches:
            if match.status != 'ended':
                players = self._get_match_players(match)
                if player_name in players:
                    remaining += 1
        
        return remaining
    
    def _compute_weight_for_resting_time(self, match):
        """calculate the weight based on the resting time (based on batch)"""
        penalty = 0
        
        # get the players of the current match
        current_players = self._get_match_players(match)
        
        # check if the players have appeared in the previous batches
        for player in current_players:
            if player in self._get_players_from_previous_batches():
                penalty -= 100  # heavily penalize consecutive players
        
        return penalty

    def _get_players_from_previous_batches(self):
        """get all players from the previous batches"""
        players = set()
        
        # get players from the scheduled matches
        for match in self.scheduled_matches:
            match_players = self._get_match_players(match)
            players.update(match_players)
        
        return players

    def _update_candidate_matches_for_round(self, candidate_matches, round_matches):
        """update the candidate matches for the round"""
        for match in round_matches:
            if match not in self.scheduled_matches and self._can_schedule_match(match):
                candidate_matches.add(match)

    def _fill_remaining_matches(self):
        """fill the remaining matches, minimize the number of affected players"""
        # get all the unscheduled matches
        scheduled_match_ids = {match.id for match in self.scheduled_matches}
        remaining_matches = [match for match in self.all_matches if match.id not in scheduled_match_ids]
        
        if not remaining_matches:
            return
        
        print(f"Found {len(remaining_matches)} remaining matches to schedule")
        
        # sort the remaining matches by round
        remaining_matches.sort(key=lambda x: (x.round or 1, x.match_number or 1))
        
        # try to fill the incomplete batches
        self._fill_incomplete_batches(remaining_matches)
        
        # if there are still remaining matches, create new batches
        remaining_match_ids = {match.id for match in remaining_matches}
        still_remaining = [match for match in self.all_matches if match.id in remaining_match_ids]
        
        if still_remaining:
            print(f"Creating new batches for {len(still_remaining)} remaining matches")
            self._create_new_batches_for_remaining(still_remaining)
        
        # final check
        final_remaining = [match for match in self.all_matches if match not in self.scheduled_matches]
        if final_remaining:
            print(f"Warning: {len(final_remaining)} matches still not scheduled")
            for match in final_remaining:
                print(f"  - Match {match.id}: {match.player1_name} vs {match.player2_name} (Round {match.round})")

    def _fill_incomplete_batches(self, remaining_matches):
        """fill the incomplete batches"""
        # reorganize the scheduled matches into batches
        batches = self._organize_matches_into_batches()
        
        for batch_idx, batch in enumerate(batches):
            if len(batch) < self.total_court:
                # this batch is not full, try to fill the matches
                self._fill_batch_with_remaining(batch_idx, batch, remaining_matches)

    def _fill_batch_with_remaining(self, batch_idx, batch, remaining_matches):
        """fill the remaining matches in the specified batch"""
        batch_players = set()
        for match in batch:
            match_players = self._get_match_players(match)
            batch_players.update(match_players)
        
        # find the matches that can be filled
        fillable_matches = []
        for match in remaining_matches:
            if self._can_fill_match_in_batch(match, batch_players):
                fillable_matches.append(match)
        
        # sort the matches by weight
        weighted_fillable = []
        for match in fillable_matches:
            weight = self._calculate_fill_weight(match, batch_idx)
            weighted_fillable.append((match, weight))
        
        weighted_fillable.sort(key=lambda x: x[1], reverse=True)
        
        # fill the matches
        for match, weight in weighted_fillable:
            if len(batch) >= self.total_court:
                break
            
            match_players = self._get_match_players(match)
            if not (match_players & batch_players):
                # insert the match into the correct position
                self._insert_match_into_batch(match, batch_idx)
                batch_players.update(match_players)
                # remove the match from the remaining matches
                remaining_matches.remove(match)

    def _can_fill_match_in_batch(self, match, batch_players):
        """check if the match can be filled into the batch"""
        # check the player conflict
        match_players = self._get_match_players(match)
        if match_players & batch_players:
            return False
        
        # check the dependency
        if not self._can_schedule_match(match):
            return False
        
        return True

    def _calculate_fill_weight(self, match, batch_idx):
        """calculate the weight of filling the match"""
        weight = 0
        
        # basic weight
        weight += self._calculate_weight(match)
        
        # additional consideration: penalty for player conflict in the batch
        batch_players = self._get_batch_players(batch_idx)
        match_players = self._get_match_players(match)
        
        if match_players & batch_players:
            weight -= 1000
        
        return weight

    def _insert_match_into_batch(self, match, batch_idx):
        """insert match into the specified batch"""
        # calculate the insert position
        insert_position = batch_idx * self.total_court + len(self._get_batch_matches(batch_idx))
        
        # insert into the correct position of scheduled_matches
        self.scheduled_matches.insert(insert_position, match)

    def _get_batch_matches(self, batch_idx):
        """get matches in the specified batch"""
        start_idx = batch_idx * self.total_court
        end_idx = start_idx + self.total_court
        return self.scheduled_matches[start_idx:end_idx]

    def _get_batch_players(self, batch_idx):
        """get players in the specified batch"""
        batch_matches = self._get_batch_matches(batch_idx)
        players = set()
        
        for match in batch_matches:
            match_players = self._get_match_players(match)
            players.update(match_players)
        
        return players

    def _write_schedule(self, filename):
        """write schedule to Excel file, including color markers and stats"""
        rows = []
        all_consecutive_players = []
        
        # reorganize scheduled_matches into batches
        batches = self._organize_matches_into_batches()
        
        for batch_idx, batch in enumerate(batches, 1):
            batch_rows = []
            
            # add actual matches
            for court_idx, match in enumerate(batch, 1):
                # get match info (using Match object attributes)
                category = match.event_type
                group = Group.query.filter_by(id=match.group_id).first()
                flight = group.name if group else ''
                
                # get player info - 修正處理 Winner of Match
                if match.event_type in ['MD', 'WD', 'XD']:
                    # 雙打
                    team1_p1 = match.team1_player1_name or ''
                    team1_p2 = match.team1_player2_name or ''
                    team2_p1 = match.team2_player1_name or ''
                    team2_p2 = match.team2_player2_name or ''
                    
                    # 處理 Winner of Match
                    if 'Winner of Match' in team1_p1:
                        player1s = f"Winner of {team1_p1}"
                    else:
                        player1s = f"{team1_p1} / {team1_p2}" if team1_p1 and team1_p2 else ''
                    
                    if 'Winner of Match' in team2_p1:
                        player2s = f"Winner of {team2_p1}"
                    else:
                        player2s = f"{team2_p1} / {team2_p2}" if team2_p1 and team2_p2 else ''
                    
                    match_type = "Double"
                else:
                    # 單打
                    player1_name = match.player1_name or ''
                    player2_name = match.player2_name or ''
                    
                    # 處理 Winner of Match
                    if 'Winner of Match' in player1_name:
                        player1s = f"Winner of {player1_name}"
                    else:
                        player1s = player1_name
                    
                    if 'Winner of Match' in player2_name:
                        player2s = f"Winner of {player2_name}"
                    else:
                        player2s = player2_name
                    
                    match_type = "Single"
                
                # 檢查連續出場選手（只統計實際選手比賽，不統計晉級比賽）
                consecutive_players = []
                if not self._is_winner_match(match):
                    consecutive_players = self._get_consecutive_players_for_match(match, batch_idx)
                    consecutive_str = ", ".join(consecutive_players) if consecutive_players else ""
                    all_consecutive_players.extend(consecutive_players)
                else:
                    consecutive_str = ""
                
                batch_rows.append({
                    'Batch': batch_idx,
                    'Court': f"Court {court_idx}",
                    'Match_Type': match_type,
                    'Category': category,
                    'Group': flight,
                    'Player1/Team1': player1s,
                    'Player2/Team2': player2s,
                    'Consecutive_Players': consecutive_str,
                    'Status': match.status or 'Scheduled',
                    'Score1': match.player1_score or 0,
                    'Score2': match.player2_score or 0,
                    'Umpire': '',
                    'Notes': ''
                })
            
            # fill empty rows to reach the total_court number
            for court_idx in range(len(batch) + 1, self.total_court + 1):
                batch_rows.append({
                    'Batch': batch_idx,
                    'Court': f"Court {court_idx}",
                    'Match_Type': '',
                    'Category': '',
                    'Group': '',
                    'Player1/Team1': '',
                    'Player2/Team2': '',
                    'Consecutive_Players': '',
                    'Status': '',
                    'Score1': '',
                    'Score2': '',
                    'Umpire': '',
                    'Notes': ''
                })
            
            # add all rows of this batch to the total rows list
            rows.extend(batch_rows)

        # calculate the stats of affected players
        player_counts = Counter(all_consecutive_players)
        total_affected_players = len(player_counts)
        
        # add stats info row
        rows.append({})  # empty row
        rows.append({
            'Batch': 'Stats',
            'Court': '',
            'Match_Type': '',
            'Category': '',
            'Group': '',
            'Player1/Team1': '',
            'Player2/Team2': '',
            'Consecutive_Players': '',
            'Status': '',
            'Score1': '',
            'Score2': '',
            'Umpire': '',
            'Notes': ''
        })
        
        # add the total count of affected players
        rows.append({
            'Batch': 'Total Affected Players',
            'Court': '',
            'Match_Type': '',
            'Category': '',
            'Group': '',
            'Player1/Team1': '',
            'Player2/Team2': '',
            'Consecutive_Players': '',
            'Status': '',
            'Score1': '',
            'Score2': '',
            'Umpire': '',
            'Notes': total_affected_players
        })
        
        # add the count of each affected player
        for player, count in player_counts.most_common():  # sorted by count (descending order)
            rows.append({
                'Batch': '',
                'Court': '',
                'Match_Type': '',
                'Category': '',
                'Group': '',
                'Player1/Team1': player,
                'Player2/Team2': '',
                'Consecutive_Players': '',
                'Status': '',
                'Score1': '',
                'Score2': '',
                'Umpire': '',
                'Notes': f"Consecutive {count} times"
            })

        # Write to Excel file
        import pandas as pd
        df = pd.DataFrame(rows)
        df.to_excel(filename, index=False, sheet_name='MatchSchedule')

        # Use openpyxl to add color markers
        wb = load_workbook(filename)
        ws = wb['MatchSchedule']
        
        # Yellow for marking consecutive players
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        
        # Green for marking regular match rows
        green_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
        
        # Blue for marking stats info
        blue_fill = PatternFill(start_color="87CEEB", end_color="87CEEB", fill_type="solid")
        
        # Red for marking affected players
        red_fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
        
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column), 2):
            consecutive_cell = row[7]  # Consecutive_Players row
            category_cell = row[3]     # Category row
            batch_cell = row[0]        # Batch row
            
            # Check if the row is a stats info row
            if batch_cell.value == 'Stats':
                for cell in row:
                    cell.fill = blue_fill
            elif batch_cell.value == 'Total Affected Players':
                for cell in row:
                    cell.fill = red_fill
            elif batch_cell.value == '' and row[5].value and 'Consecutive' in str(row[11].value or ''):
                # affected players detailed stats row
                for cell in row:
                    cell.fill = red_fill
            elif consecutive_cell.value:  # consecutive players row
                for cell in row:
                    cell.fill = yellow_fill
            elif category_cell.value:   # match row
                for cell in row:
                    cell.fill = green_fill

        wb.save(filename)
        return filename

    def _organize_matches_into_batches(self):
        """將已安排的比賽重新組織成 batches"""
        batches = []
        current_batch = []
        
        for match in self.scheduled_matches:
            current_batch.append(match)
            
            if len(current_batch) >= self.total_court:
                batches.append(current_batch)
                current_batch = []
        
        # 添加最後一個不完整的 batch
        if current_batch:
            batches.append(current_batch)
        
        return batches

    def _get_consecutive_players_for_match(self, match, current_batch_idx):
        """獲取該比賽中連續出場的選手"""
        consecutive_players = []
        match_players = self._get_match_players(match)
        
        # 檢查選手是否在前一個 batch 中出現過
        if current_batch_idx > 1:
            previous_batch_players = self._get_players_from_batch(current_batch_idx - 1)
            for player in match_players:
                if player in previous_batch_players:
                    consecutive_players.append(player)
        
        return consecutive_players

    def _get_players_from_batch(self, batch_idx):
        """獲取指定 batch 中的所有選手"""
        players = set()
        batches = self._organize_matches_into_batches()
        
        if 0 <= batch_idx - 1 < len(batches):
            batch = batches[batch_idx - 1]
            for match in batch:
                match_players = self._get_match_players(match)
                players.update(match_players)
        
        return players
        
    def _players_not_in_selected_players(self, match, seelcted_players):
        """check if players in match are not in the selected_players set"""
        match_players = self._get_match_players(match)
        for player in match_players:
            if player in seelcted_players:
                return False
        return True

    def _create_new_batches_for_remaining(self, remaining_matches):
        """為剩餘比賽創建新的 batch，考慮依賴關係和選手衝突"""
        if not remaining_matches:
            return
        
        # 按輪次和比賽編號排序
        remaining_matches.sort(key=lambda x: (x.round or 1, x.match_number or 1))
        
        # 分組處理：按輪次分組
        matches_by_round = {}
        for match in remaining_matches:
            round_num = match.round or 1
            if round_num not in matches_by_round:
                matches_by_round[round_num] = []
            matches_by_round[round_num].append(match)
        
        # 按輪次順序處理
        for round_num in sorted(matches_by_round.keys()):
            round_matches = matches_by_round[round_num]
            self._process_round_matches(round_matches)

    def _process_round_matches(self, round_matches):
        """處理單一輪次的比賽"""
        current_batch = []
        current_batch_players = set()
        
        # 計算權重並排序
        weighted_matches = []
        for match in round_matches:
            # 檢查比賽是否已經安排過
            if match not in self.scheduled_matches:
                weight = self._calculate_weight(match)
                weighted_matches.append((match, weight))
        
        weighted_matches.sort(key=lambda x: x[1], reverse=True)
        
        for match, weight in weighted_matches:
            # 再次檢查比賽是否已經安排過
            if match in self.scheduled_matches:
                continue
        
            # 檢查依賴關係
            if not self._can_schedule_match(match):
                continue
        
            # 檢查選手衝突
            match_players = self._get_match_players(match)
        
            if match_players & current_batch_players:
                # 選手衝突，開始新的 batch
                if current_batch:
                    self.scheduled_matches.extend(current_batch)
                    current_batch = []
                    current_batch_players = set()
        
            # 檢查 batch 是否已滿
            if len(current_batch) >= self.total_court:
                # batch 已滿，開始新的 batch
                self.scheduled_matches.extend(current_batch)
                current_batch = []
                current_batch_players = set()
        
            # 加入當前 batch
            current_batch.append(match)
            current_batch_players.update(match_players)
        
        # 處理最後一個不完整的 batch
        if current_batch:
            self.scheduled_matches.extend(current_batch)
    
    def _can_schedule_match(self, match):
        """檢查比賽是否可以安排（修正 elimination dependency）"""
        # skip by matches
        if self._is_bye_match(match):
            return False
        
        if not match.round or match.round == 1:
            return True
        
        # 檢查前驅比賽是否存在
        prev_match1 = self._get_match_by_id(match.prev_match1_id)
        prev_match2 = self._get_match_by_id(match.prev_match2_id)
        
        # 如果前驅比賽不存在，可能是第一輪的比賽
        if not prev_match1 or not prev_match2:
            return True
        
        # 檢查前驅比賽是否已安排
        prev_match1_scheduled = prev_match1 in self.scheduled_matches
        prev_match2_scheduled = prev_match2 in self.scheduled_matches
        
        return prev_match1_scheduled and prev_match2_scheduled

    def _is_bye_match(self, match):
        """check if the match is a bye match"""
        return (match.player1_name == 'BYE' or match.player2_name == 'BYE' or
            match.team1_player1_name == 'BYE' or match.team1_player2_name == 'BYE' or
            match.team2_player1_name == 'BYE' or match.team2_player2_name == 'BYE')

    def _is_winner_match(self, match):
        """Check ifi the match is a winner match（match info including 'Winner of Match'）"""
        if match.player1_name and 'Winner of Match' in match.player1_name:
            return True
        if match.player2_name and 'Winner of Match' in match.player2_name:
            return True
        if match.team1_player1_name and 'Winner of Match' in match.team1_player1_name:
            return True
        if match.team1_player2_name and 'Winner of Match' in match.team1_player2_name:
            return True
        if match.team2_player1_name and 'Winner of Match' in match.team2_player1_name:
            return True
        if match.team2_player2_name and 'Winner of Match' in match.team2_player2_name:
            return True
        return False

    def create_schedule(self, tournament_id, schedule_data):
        """create the schedule in the database - 覆蓋現有賽程，只保留一個版本"""
        try:
            tournament = Tournament.query.filter_by(id=tournament_id).first()
            if not tournament:
                raise ValueError(f"Tournament {tournament_id} not found")
            
            # 刪除現有的賽程和相關項目
            existing_schedules = Schedule.query.filter_by(tournament_id=tournament_id).all()
            for existing_schedule in existing_schedules:
                # 刪除相關的 schedule items
                ScheduleItem.query.filter_by(schedule_id=existing_schedule.id).delete()
                db.session.delete(existing_schedule)
            
            db.session.commit()
            
            # 創建新賽程
            schedule_dict = {
                'tournament_id': tournament_id,
                'start_date': tournament.start_date,
                'end_date': tournament.end_date,
                'start_time': datetime.strptime(schedule_data['start_time'], '%H:%M').time(),
                'end_time': datetime.strptime(schedule_data['end_time'], '%H:%M').time(),
                'total_courts': self.total_court,
                'match_duration': schedule_data.get('match_duration', 60),
                'total_matches': len(self.scheduled_matches),
                'total_batches': len(self.scheduled_matches) // self.total_court + (1 if len(self.scheduled_matches) % self.total_court > 0 else 0),
                'status': 'active'
            }
            
            # 直接創建 Schedule 實例
            schedule = Schedule(**schedule_dict)
            db.session.add(schedule)
            db.session.flush()  # 獲取 schedule.id
            
            # 創建 schedule items
            current_date = schedule.start_date
            current_time = schedule.start_time
            batch_number = 1
            order_in_batch = 0
            
            for i, match in enumerate(self.scheduled_matches):
                # 檢查是否需要新的批次
                if order_in_batch >= self.total_court:
                    batch_number += 1
                    current_time = self._add_time(current_time, schedule_data.get('batch_interval', 120))
                    order_in_batch = 0
                    
                    # 檢查是否需要新的一天
                    if current_time >= schedule.end_time:
                        current_date += timedelta(days=1)
                        current_time = schedule.start_time
                
                # 準備 schedule_item_dict
                schedule_item_dict = {
                    'schedule_id': schedule.id,
                    'match_id': match.id,
                    'batch_number': batch_number,
                    'order_in_batch': order_in_batch,
                    'court_number': order_in_batch + 1,
                    'scheduled_date': current_date,
                    'scheduled_start_time': datetime.combine(current_date, current_time),
                    'scheduled_end_time': datetime.combine(current_date, current_time) + timedelta(minutes=schedule.match_duration),
                    'status': 'scheduled'
                }
                
                # 創建 ScheduleItem 實例
                schedule_item = ScheduleItem(**schedule_item_dict)
                db.session.add(schedule_item)
                
                order_in_batch += 1
            
            db.session.commit()
            return schedule.id
            
        except Exception as e:
            db.session.rollback()
            raise e

    def _add_time(self, time, minutes):
        """時間加法"""
        dt = datetime.combine(datetime.today(), time)
        new_dt = dt + timedelta(minutes=minutes)
        return new_dt.time()