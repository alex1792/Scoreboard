from ..models import Match, User, Event, db, ScheduleItem
from ..utils import get_match_data
from flask_jwt_extended import jwt_required

class MatchService:
    """
    Match service related to matches
    - get_all_matches: return all matches in the database
    - get_match_by_id: return a match by match.id
    - create_match: create a new match
    - assign_umpire: assign an umpire to a match by match.id and umpire.id
    - update_score: update the score of a specific match
    - update_match_status: update the status of a match
    - clear_all_matches: clear all matches in the database
    - delete_match: delete a match by match.id
    """
    
    @staticmethod
    def get_all_matches():
        """get all matches"""
        matches = Match.query.all()
        return [get_match_data(match) for match in matches]

    @staticmethod
    def get_match_by_id(match_id):
        """get a match by match.id"""
        match = Match.query.get(match_id)
        if not match:
            return None
        return get_match_data(match)

    @staticmethod
    def create_match(match_data):
        """create a new match"""
        new_match = Match(**match_data)
        db.session.add(new_match)
        db.session.commit()
        return get_match_data(new_match)

    @staticmethod
    def assign_umpire(match_id, umpire_id):
        """assign an umpire to a match"""
        match = Match.query.get(match_id)
        umpire = User.query.get(umpire_id)
        
        if not match:
            raise ValueError("Match not found")
        if not umpire:
            raise ValueError("Umpire not found")
        
        match.umpire_id = umpire.id
        db.session.commit()
        return get_match_data(match)

    @staticmethod
    def update_score(match_id, player, score):
        """update the score of a match"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError("Match not found")
        
        if player == 'Player1':
            match.player1_score += score
        else:
            match.player2_score += score
        
        db.session.commit()
        return get_match_data(match)

    @staticmethod
    def update_match_status(match_id, new_status):
        """update the status of a match (Scheduled, Ongoing, Finished)"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError("Match not found")

        old_status = match.status
        next_match_data = None  # 追蹤下一輪比賽的數據
        
        # 如果從 Scheduled 變為 Ongoing，重置分數
        if old_status == 'Scheduled' and new_status == 'Ongoing':
            match.player1_score = 0
            match.player2_score = 0
            match.current_game = 1
            match.player1_game_won = 0
            match.player2_game_won = 0
            # 重置各局分數
            match.game1_score1 = 0
            match.game1_score2 = 0
            match.game2_score1 = 0
            match.game2_score2 = 0
            match.game3_score1 = 0
            match.game3_score2 = 0
        
        # 如果從 Ongoing 變為 Finished，需要計算當前局的勝負
        elif old_status == 'Ongoing' and new_status == 'Finished':
            # 先計算當前局的勝負
            MatchService._calculate_current_game_winner(match)
            # 再保存當前局的分數
            MatchService._save_current_game_score(match)
        
        # 情況1: Finished -> Scheduled (重新開始比賽)
        elif old_status == 'Finished' and new_status == 'Scheduled':
            # 完全重置比賽狀態
            match.player1_score = 0
            match.player2_score = 0
            match.current_game = 1
            match.player1_game_won = 0
            match.player2_game_won = 0
            # 重置各局分數
            match.game1_score1 = 0
            match.game1_score2 = 0
            match.game2_score1 = 0
            match.game2_score2 = 0
            match.game3_score1 = 0
            match.game3_score2 = 0
            # 清除勝者信息
            match.winner1_id = None
            match.winner2_id = None
            match.loser1_id = None
            match.loser2_id = None
            match.winner_name = None
            match.loser_name = None
            
            # 重要：需要撤銷對下一輪比賽的更新
            if match.next_match_id:
                next_match_data = MatchService._undo_next_round_update(match_id)
        
        # 情況2: Finished -> Ongoing (撤銷 end_match，保留分數)
        elif old_status == 'Finished' and new_status == 'Ongoing':
            # 保留當前分數和進度，但撤銷勝者判斷
            # 撤銷最後一局的勝負計算
            MatchService._undo_last_game_winner(match)
            # 清除勝者信息
            match.winner1_id = None
            match.winner2_id = None
            match.loser1_id = None
            match.loser2_id = None
            match.winner_name = None
            match.loser_name = None
            
            # 重要：需要撤銷對下一輪比賽的更新
            if match.next_match_id:
                next_match_data = MatchService._undo_next_round_update(match_id)
        
        # 更新狀態
        match.status = new_status
        
        # 如果狀態是 Finished，確定最終勝者
        if new_status == 'Finished':
            try:
                winner_info = MatchService.determine_winner(match_id)
                print(f"Winner determined: {winner_info}")  # add debug info
            except ValueError as e:
                raise ValueError(f"Cannot finish match: {str(e)}")
        
        db.session.commit()
        
        # 返回當前比賽數據和下一輪比賽數據（如果有的話）
        return {
            'match_data': get_match_data(match),
            'next_match_data': next_match_data
        }

    @staticmethod
    def clear_all_matches():
        """clear all matches"""
        Match.query.delete()
        db.session.commit()

    @staticmethod
    def delete_match(match_id):
        """delete a specific match"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError("Match not found")
        
        # delete the related ScheduleItem
        schedule_items = ScheduleItem.query.filter_by(match_id=match_id).all()
        for item in schedule_items:
            db.session.delete(item)
        
        # delete the match
        db.session.delete(match)
        db.session.commit()

    @staticmethod
    def delete_all_matches_by_tournament_id(tournament_id):
        matches = Match.query.filter_by(tournament_id=tournament_id).all()
        for match in matches:
            schedule_items = ScheduleItem.query.filter_by(match_id=match.id).all()
            for item in schedule_items:
                db.session.delete(item)
            db.session.delete(match)
        db.session.commit()
    
    @staticmethod
    def get_matches_by_umpire(umpire_id):
        """get the matches that the umpire is responsible for"""
        match = Match.query.filter_by(umpire_id=umpire_id).first()
        if not match:
            return None
        return get_match_data(match)

    @staticmethod
    def get_matches_by_tournament(tournament_id):
        matches = [get_match_data(match) for match in Match.query.filter_by(tournament_id=tournament_id).all()]
        if not matches:
            return None
        return matches

    @staticmethod
    def get_raw_matches_by_tournament(tournament_id):
        """get the raw matches of a tournament (not processed by get_match_data)"""
        matches = Match.query.filter_by(tournament_id=tournament_id).all()
        return matches if matches else []

    @staticmethod
    def update_match_winner(match_id, winner_name):
        """update the winner of a match and chain update the next matches"""
        match = Match.query.get(match_id)
        if not match:
            return False
        
        # update the winner of the current match
        # ... update logic
        
        # find and update the next matches
        next_matches = Match.query.filter(
            (Match.prev_match1_id == match_id) | 
            (Match.prev_match2_id == match_id)
        ).all()
        
        for next_match in next_matches:
            if next_match.player1_from_match == match_id:
                next_match.player1_name = winner_name
            elif next_match.player2_from_match == match_id:
                next_match.player2_name = winner_name
            
            # if both players are determined, start the match
            if next_match.player1_name and next_match.player2_name:
                next_match.status = 'Scheduled'
        
        db.session.commit()
        return True

    @staticmethod
    def determine_winner(match_id):
        """Once the match is finished, determine the winner"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError("Match not found")

        # check match.player1_game_won and match.player2_game_won
        if match.player1_game_won == match.player2_game_won:
            return ValueError("Match is a draw")

        if match.player1_game_won > match.player2_game_won:
            """Player 1 wins the match"""
            if match.event_type in ['MS', 'WS']:
                print(f"Single match - Player 1 wins")
                print(f"Setting winner1_id = {match.player1_id}")
                print(f"Setting loser1_id = {match.player2_id}")
                
                match.winner1_id = match.player1_id
                match.winner2_id = None
                match.loser1_id = match.player2_id
                match.loser2_id = None
                winner_name = match.player1_name
                loser_name = match.player2_name
            # double matches
            else:
                print(f"Double match - Team 1 wins")
                print(f"Setting winner1_id = {match.team1_player1_id}")
                print(f"Setting winner2_id = {match.team1_player2_id}")
                print(f"Setting loser1_id = {match.team2_player1_id}")
                print(f"Setting loser2_id = {match.team2_player2_id}")
                
                match.winner1_id = match.team1_player1_id
                match.winner2_id = match.team1_player2_id
                match.loser1_id = match.team2_player1_id
                match.loser2_id = match.team2_player2_id
                winner_name = f"{match.team1_player1_name} / {match.team1_player2_name}"
                loser_name = f"{match.team2_player1_name} / {match.team2_player2_name}"
        else:
            """Player 2 wins the match"""
            # single match
            if match.event_type in ['MS', 'WS']:
                print(f"Single match - Player 2 wins")
                print(f"Setting winner1_id = {match.player2_id}")
                print(f"Setting loser1_id = {match.player1_id}")
                
                match.winner1_id = match.player2_id
                match.winner2_id = None
                match.loser1_id = match.player1_id
                match.loser2_id = None
                winner_name = match.player2_name
                loser_name = match.player1_name
            # double matches
            else:
                print(f"Double match - Team 2 wins")
                print(f"Setting winner1_id = {match.team2_player1_id}")
                print(f"Setting winner2_id = {match.team2_player2_id}")
                print(f"Setting loser1_id = {match.team1_player1_id}")
                print(f"Setting loser2_id = {match.team1_player2_id}")
                
                match.winner1_id = match.team2_player1_id
                match.winner2_id = match.team2_player2_id
                match.loser1_id = match.team1_player1_id
                match.loser2_id = match.team1_player2_id
                winner_name = f"{match.team2_player1_name} / {match.team2_player2_name}"
                loser_name = f"{match.team1_player1_name} / {match.team1_player2_name}"
        
        match.winner_name = winner_name
        match.loser_name = loser_name
        
        
        db.session.commit()

        print(f"Match next_match_id: {match.next_match_id}")

        if match.next_match_id:
            print(f"Updating next round match: {match.next_match_id}")
            MatchService.update_next_round_match(match_id)

        
        return {'winner_name': winner_name, 'loser_name': loser_name}
        
    @staticmethod
    def _save_current_game_score(match):
        """保存當前局的分數"""
        if match.current_game == 1:
            match.game1_score1 = match.player1_score
            match.game1_score2 = match.player2_score
        elif match.current_game == 2:
            match.game2_score1 = match.player1_score
            match.game2_score2 = match.player2_score
        elif match.current_game == 3:
            match.game3_score1 = match.player1_score
            match.game3_score2 = match.player2_score

    @staticmethod
    def _calculate_current_game_winner(match):
        """計算當前局的勝負"""
        # 直接根據當前的 player1_score 和 player2_score 計算勝負
        if match.player1_score > match.player2_score:
            match.player1_game_won += 1
        elif match.player1_score < match.player2_score:
            match.player2_game_won += 1
        elif match.player1_score == 0 and match.player2_score == 0:
            pass  # 雙方都是0分，不計算勝負
        else:
            raise ValueError("Game is a draw")

    @staticmethod
    def next_game(match_id):
        """Set the match to next game"""
        match = Match.query.get(match_id)
        if not match:
            return ValueError("Match not found")
        
        if match.current_game >= 3:
            return ValueError("Can only support 3 games")
        
        # 1. 先計算當前局的勝負
        MatchService._calculate_current_game_winner(match)
        
        # 2. 再保存當前局的分數
        MatchService._save_current_game_score(match)
        
        # 3. 重置分數並進入下一局
        match.player1_score = 0
        match.player2_score = 0
        match.current_game += 1
        
        db.session.commit()
        return get_match_data(match)

    @staticmethod
    def end_match(match_id):
        """
        End the match, and summarize the score, determine the winner
        Return the match data
        """
        match = Match.query.get(match_id)
        if not match:
            return ValueError("Match not found")

        # 1. 先計算當前局的勝負
        MatchService._calculate_current_game_winner(match)
        
        # 2. 再保存當前局的分數
        MatchService._save_current_game_score(match)
        
        # 3. 設置比賽狀態為完成
        match.status = 'Finished'
        
        # 4. 確定最終勝者
        MatchService.determine_winner(match_id)
        
        # 5. 更新下一輪比賽（如果是淘汰賽）
        if match.next_match_id:
            MatchService.update_next_round_match(match_id)

        db.session.commit()
        return get_match_data(match)

    @staticmethod
    def update_next_round_match(match_id):
        """For elimination matches, once the winner is determined, update the next round"""
        match = Match.query.get(match_id)
        if not match:
            return ValueError("Match not found")

        if not match.next_match_id:
            return  # no next match, return

        next_match = Match.query.get(match.next_match_id)
        if not next_match:
            return ValueError("Next match not found")

        # determine the winner name
        winner_name = ""
        if match.winner1_id is not None or match.winner2_id is not None:
            # winner id exists
            if match.event_type in ['MS', 'WS']:
                # single match: only one winner
                winner_id = match.winner1_id if match.winner1_id is not None else match.winner2_id
                winner = User.query.get(winner_id)
                if winner:
                    winner_name = winner.get_full_name()
            else:
                # double match: two winners
                winner1 = User.query.get(match.winner1_id)
                winner2 = User.query.get(match.winner2_id)
                if winner1 and winner2:
                    winner_name = f"{winner1.get_full_name()} / {winner2.get_full_name()}"
        else:
            # winner id does not exist, use winner_name
            winner_name = match.winner_name

        print(f"winner name: {winner_name}")
        # update the next match
        if next_match.prev_match1_id == match_id:
            if match.event_type in ['MS', 'WS']:
                next_match.player1_name = winner_name
            else:
                names = winner_name.split(' / ')
                next_match.team1_player1_name = names[0].strip()
                next_match.team1_player2_name = names[1].strip() if len(names) > 1 else ""
        elif next_match.prev_match2_id == match_id:
            if match.event_type in ['MS', 'WS']:
                next_match.player2_name = winner_name
            else:
                names = winner_name.split(' / ')
                next_match.team2_player1_name = names[0].strip()
                next_match.team2_player2_name = names[1].strip() if len(names) > 1 else ""
        db.session.commit()
        
        print(f"next match player1_name: {next_match.player1_name}")
        print(f"next match player2_name: {next_match.player2_name}")
        print(f"next match team1_player1_name: {next_match.team1_player1_name}")
        print(f"next match team1_player2_name: {next_match.team1_player2_name}")
        print(f"next match team2_player1_name: {next_match.team2_player1_name}")
        print(f"next match team2_player2_name: {next_match.team2_player2_name}")

        
        return get_match_data(next_match)  

    @staticmethod
    def _undo_last_game_winner(match):
        """撤銷最後一局的勝負計算"""
        # 撤銷最後一局的 game_won 計算
        if match.current_game == 1:
            if match.game1_score1 > match.game1_score2:
                match.player1_game_won -= 1
            elif match.game1_score1 < match.game1_score2:
                match.player2_game_won -= 1
        elif match.current_game == 2:
            if match.game2_score1 > match.game2_score2:
                match.player1_game_won -= 1
            elif match.game2_score1 < match.game2_score2:
                match.player2_game_won -= 1
        elif match.current_game == 3:
            if match.game3_score1 > match.game3_score2:
                match.player1_game_won -= 1
            elif match.game3_score1 < match.game3_score2:
                match.player2_game_won -= 1

    @staticmethod
    def _undo_next_round_update(match_id):
        """撤銷對下一輪比賽的更新"""
        match = Match.query.get(match_id)
        if not match or not match.next_match_id:
            return None  # 返回 None 表示沒有下一輪比賽需要更新
        
        next_match = Match.query.get(match.next_match_id)
        if not next_match:
            return None
        
        # 恢復下一輪比賽的原始參賽者信息
        if next_match.prev_match1_id == match_id:
            if match.event_type in ['MS', 'WS']:
                next_match.player1_name = f"Winner of Match #{match_id}"
            else:
                next_match.team1_player1_name = f"Winner of Match #{match_id}"
                next_match.team1_player2_name = None
        elif next_match.prev_match2_id == match_id:
            if match.event_type in ['MS', 'WS']:
                next_match.player2_name = f"Winner of Match #{match_id}"
            else:
                next_match.team2_player1_name = f"Winner of Match #{match_id}"
                next_match.team2_player2_name = None
        
        # 提交更改
        db.session.commit()
        
        # 返回下一輪比賽的數據，讓 Controller 層處理 WebSocket 發送
        return get_match_data(next_match) 