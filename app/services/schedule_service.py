from ..models import Match, Group, db
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
        self.all_matches = []  # 存儲所有比賽

    def schedule_tournament(self, matches):
        """安排整個錦標賽，處理 batch 不滿和依賴關係"""
        # 確保 matches 是列表
        if not isinstance(matches, (list, tuple)):
            matches = [matches]
        
        self.all_matches = matches
        self.scheduled_matches = []  # 重置已安排的比賽
        
        # 1. 按輪次分組
        matches_by_round = self._group_by_round(matches)
        
        # 2. 按輪次順序處理 - 確保 Round 1 完全安排完才處理 Round 2
        for round_num in sorted(matches_by_round.keys()):
            round_matches = matches_by_round[round_num]
            
            # 3. 初始化該輪的候選集
            candidate_matches = set()
            
            # 4. 將該輪比賽加入候選集
            for match in round_matches:
                if self._can_schedule_match(match):
                    candidate_matches.add(match)
            
            # 5. 安排該輪的所有比賽
            while candidate_matches:
                batch_matches = self._schedule_batch(candidate_matches)
                if not batch_matches:
                    break
                
                # 6. 更新候選集
                for match in batch_matches:
                    candidate_matches.discard(match)
                    if match not in self.scheduled_matches:
                        self.scheduled_matches.append(match)
                
                # 7. 重新檢查該輪中可以安排的比賽
                self._update_candidate_matches_for_round(candidate_matches, round_matches)
        
        # 8. 最後階段：填入剩餘比賽
        self._fill_remaining_matches()

    def _group_by_round(self, matches):
        """按輪次分組比賽"""
        matches_by_round = {}
        
        for match in matches:
            round_num = match.round or 1  # 如果沒有 round，設為 1
            if round_num not in matches_by_round:
                matches_by_round[round_num] = []
            matches_by_round[round_num].append(match)
        
        return matches_by_round
    
    def _get_match_by_id(self, match_id):
        """根據 match_id 獲取比賽"""
        if not match_id:
            return None
        
        for match in self.all_matches:
            if match.id == match_id:
                return match
        return None
    
    def _schedule_batch(self, candidate_matches):
        """安排一個 batch 的比賽"""
        selected_matches = []
        selected_players = set()
        
        # 計算權重並排序
        weighted_matches = []
        for match in candidate_matches:
            weight = self._calculate_weight(match)
            weighted_matches.append((match, weight))
        
        weighted_matches.sort(key=lambda x: x[1], reverse=True)
        
        # 貪婪選擇比賽
        for match, weight in weighted_matches:
            if len(selected_matches) >= self.total_court:
                break
            
            match_players = self._get_match_players(match)
            if not (match_players & selected_players):
                selected_matches.append(match)
                selected_players.update(match_players)
        
        return selected_matches

    def _calculate_weight(self, match):
        """計算比賽權重"""
        weight = 0
        
        # 1. 剩餘比賽數量
        weight += self._compute_weight_for_remaining_games(match)
        
        # 2. 休息時間
        weight += self._compute_weight_for_resting_time(match)
        
        return weight
    
    def _compute_weight_for_remaining_games(self, match):
        """計算基於剩餘比賽的權重"""
        weight = 0
        
        # 獲取所有選手
        players = self._get_match_players(match)
        
        # 計算每個選手的剩餘比賽
        for player in players:
            remaining_games = self._get_remaining_games_for_player(player)
            weight += remaining_games * 10
        
        return weight
    
    def _get_match_players(self, match):
        """獲取比賽中的所有選手"""
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
        """獲取選手的剩餘比賽數量"""
        remaining = 0
        
        for match in self.all_matches:
            if match.status != 'ended':
                players = self._get_match_players(match)
                if player_name in players:
                    remaining += 1
        
        return remaining
    
    def _compute_weight_for_resting_time(self, match):
        """計算基於休息時間的權重（基於 batch）"""
        penalty = 0
        
        # 獲取當前比賽的選手
        current_players = self._get_match_players(match)
        
        # 檢查選手是否在之前的 batch 中出現過
        for player in current_players:
            if player in self._get_players_from_previous_batches():
                penalty -= 100  # 大幅懲罰連續比賽的選手
        
        return penalty

    def _get_players_from_previous_batches(self):
        """獲取之前 batch 中的所有選手"""
        players = set()
        
        # 從已安排的比賽中獲取選手
        for match in self.scheduled_matches:
            match_players = self._get_match_players(match)
            players.update(match_players)
        
        return players

    def _update_candidate_matches_for_round(self, candidate_matches, round_matches):
        """更新該輪的候選集"""
        for match in round_matches:
            if match not in self.scheduled_matches and self._can_schedule_match(match):
                candidate_matches.add(match)

    def _fill_remaining_matches(self):
        """填入剩餘的比賽，最小化影響人數"""
        # 獲取所有未安排的比賽
        scheduled_match_ids = {match.id for match in self.scheduled_matches}
        remaining_matches = [match for match in self.all_matches if match.id not in scheduled_match_ids]
        
        if not remaining_matches:
            return
        
        print(f"Found {len(remaining_matches)} remaining matches to schedule")
        
        # 按輪次排序剩餘比賽
        remaining_matches.sort(key=lambda x: (x.round or 1, x.match_number or 1))
        
        # 嘗試填入不滿的 batch
        self._fill_incomplete_batches(remaining_matches)
        
        # 如果還有剩餘，創建新的 batch
        remaining_match_ids = {match.id for match in remaining_matches}
        still_remaining = [match for match in self.all_matches if match.id in remaining_match_ids]
        
        if still_remaining:
            print(f"Creating new batches for {len(still_remaining)} remaining matches")
            self._create_new_batches_for_remaining(still_remaining)
        
        # 最終檢查
        final_remaining = [match for match in self.all_matches if match not in self.scheduled_matches]
        if final_remaining:
            print(f"Warning: {len(final_remaining)} matches still not scheduled")
            for match in final_remaining:
                print(f"  - Match {match.id}: {match.player1_name} vs {match.player2_name} (Round {match.round})")

    def _fill_incomplete_batches(self, remaining_matches):
        """填入不滿的 batch"""
        # 重新組織已安排的比賽成 batches
        batches = self._organize_matches_into_batches()
        
        for batch_idx, batch in enumerate(batches):
            if len(batch) < self.total_court:
                # 這個 batch 不滿，嘗試填入比賽
                self._fill_batch_with_remaining(batch_idx, batch, remaining_matches)

    def _fill_batch_with_remaining(self, batch_idx, batch, remaining_matches):
        """填入特定 batch 的剩餘比賽"""
        batch_players = set()
        for match in batch:
            match_players = self._get_match_players(match)
            batch_players.update(match_players)
        
        # 尋找可以填入的比賽
        fillable_matches = []
        for match in remaining_matches:
            if self._can_fill_match_in_batch(match, batch_players):
                fillable_matches.append(match)
        
        # 按權重排序可填入的比賽
        weighted_fillable = []
        for match in fillable_matches:
            weight = self._calculate_fill_weight(match, batch_idx)
            weighted_fillable.append((match, weight))
        
        weighted_fillable.sort(key=lambda x: x[1], reverse=True)
        
        # 填入比賽
        for match, weight in weighted_fillable:
            if len(batch) >= self.total_court:
                break
            
            match_players = self._get_match_players(match)
            if not (match_players & batch_players):
                # 將比賽插入到正確的位置
                self._insert_match_into_batch(match, batch_idx)
                batch_players.update(match_players)
                # 從剩餘比賽中移除
                remaining_matches.remove(match)

    def _can_fill_match_in_batch(self, match, batch_players):
        """檢查比賽是否可以填入 batch"""
        # 檢查選手衝突
        match_players = self._get_match_players(match)
        if match_players & batch_players:
            return False
        
        # 檢查依賴關係
        if not self._can_schedule_match(match):
            return False
        
        return True

    def _calculate_fill_weight(self, match, batch_idx):
        """計算填入比賽的權重"""
        weight = 0
        
        # 基礎權重
        weight += self._calculate_weight(match)
        
        # 額外考慮：與該 batch 的選手衝突懲罰
        batch_players = self._get_batch_players(batch_idx)
        match_players = self._get_match_players(match)
        
        if match_players & batch_players:
            weight -= 1000
        
        return weight

    def _insert_match_into_batch(self, match, batch_idx):
        """將比賽插入到指定的 batch"""
        # 計算插入位置
        insert_position = batch_idx * self.total_court + len(self._get_batch_matches(batch_idx))
        
        # 插入到 scheduled_matches 的正確位置
        self.scheduled_matches.insert(insert_position, match)

    def _get_batch_matches(self, batch_idx):
        """獲取指定 batch 的比賽"""
        start_idx = batch_idx * self.total_court
        end_idx = start_idx + self.total_court
        return self.scheduled_matches[start_idx:end_idx]

    def _get_batch_players(self, batch_idx):
        """獲取指定 batch 的選手"""
        batch_matches = self._get_batch_matches(batch_idx)
        players = set()
        
        for match in batch_matches:
            match_players = self._get_match_players(match)
            players.update(match_players)
        
        return players

    def _write_schedule(self, filename):
        """寫入賽程表到 Excel 文件，包含顏色標記和統計"""
        rows = []
        all_consecutive_players = []
        
        # 將 scheduled_matches 重新組織成 batches
        batches = self._organize_matches_into_batches()
        
        for batch_idx, batch in enumerate(batches, 1):
            batch_rows = []
            
            # 添加實際的比賽
            for court_idx, match in enumerate(batch, 1):
                # 獲取比賽信息（使用 Match 對象的屬性）
                category = match.event_type
                group = Group.query.filter_by(id=match.group_id).first()
                flight = group.name if group else ''
                
                # 獲取選手信息
                if match.event_type in ['MD', 'WD', 'XD']:
                    player1s = f"{match.team1_player1_name} / {match.team1_player2_name}" if match.team1_player1_name and match.team1_player2_name else ''
                    player2s = f"{match.team2_player1_name} / {match.team2_player2_name}" if match.team2_player1_name and match.team2_player2_name else ''
                    match_type = "Double"
                else:
                    player1s = match.player1_name or ''
                    player2s = match.player2_name or ''
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
            
            # 填充空行以達到 total_court 數量
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
            
            # 將這個 batch 的所有行添加到總行列表
            rows.extend(batch_rows)

        # 計算受影響選手統計
        player_counts = Counter(all_consecutive_players)
        total_affected_players = len(player_counts)
        
        # 添加統計信息行
        rows.append({})  # 空行
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
        
        # 添加受影響人數總計
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
        
        # 添加每個受影響選手的次數
        for player, count in player_counts.most_common():  # 按次數降序排列
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

        # 寫入 Excel 文件
        import pandas as pd
        df = pd.DataFrame(rows)
        df.to_excel(filename, index=False, sheet_name='MatchSchedule')

        # 使用 openpyxl 添加顏色標記
        wb = load_workbook(filename)
        ws = wb['MatchSchedule']
        
        # 黃色標記連續出場的選手
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        
        # 綠色標記有比賽的行
        green_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
        
        # 藍色標記統計信息行
        blue_fill = PatternFill(start_color="87CEEB", end_color="87CEEB", fill_type="solid")
        
        # 紅色標記受影響選手統計
        red_fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
        
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column), 2):
            consecutive_cell = row[7]  # Consecutive_Players 欄位
            category_cell = row[3]     # Category 欄位
            batch_cell = row[0]        # Round 欄位
            
            # 檢查是否為統計信息行
            if batch_cell.value == 'Stats':
                for cell in row:
                    cell.fill = blue_fill
            elif batch_cell.value == 'Total Affected Players':
                for cell in row:
                    cell.fill = red_fill
            elif batch_cell.value == '' and row[5].value and 'Consecutive' in str(row[11].value or ''):
                # 受影響選手詳細統計行
                for cell in row:
                    cell.fill = red_fill
            elif consecutive_cell.value:  # 有連續出場選手
                for cell in row:
                    cell.fill = yellow_fill
            elif category_cell.value:   # 有比賽但無連續出場
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
        """檢查是否為晉級比賽（包含 Winner of Match）"""
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