from ..models import Match, User, Event, db
from ..utils import get_match_data

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
        """獲取所有比賽"""
        matches = Match.query.all()
        return [get_match_data(match) for match in matches]

    @staticmethod
    def get_match_by_id(match_id):
        """根據ID獲取比賽"""
        match = Match.query.get(match_id)
        if not match:
            return None
        return get_match_data(match)

    @staticmethod
    def create_match(match_data):
        """創建新比賽"""
        new_match = Match(**match_data)
        db.session.add(new_match)
        db.session.commit()
        return get_match_data(new_match)

    @staticmethod
    def assign_umpire(match_id, umpire_id):
        """分配裁判給比賽"""
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
        """更新比賽分數"""
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
        """更新比賽狀態"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError("Match not found")

        # 先更新狀態
        match.status = new_status
        
        # 如果狀態是 Finished，則確定勝者
        if new_status == 'Finished':
            try:
                winner_info = MatchService.determine_winner(match_id)
                print(f"Winner determined: {winner_info}")  # 添加調試信息
            except ValueError as e:
                raise ValueError(f"Cannot finish match: {str(e)}")
        
        db.session.commit()
        return get_match_data(match)

    @staticmethod
    def clear_all_matches():
        """清除所有比賽"""
        Match.query.delete()
        db.session.commit()

    @staticmethod
    def delete_match(match_id):
        """刪除特定比賽"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError("Match not found")
        
        db.session.delete(match)
        db.session.commit()

    @staticmethod
    def get_matches_by_umpire(umpire_id):
        """獲取裁判負責的比賽"""
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
        """獲取錦標賽的原始 Match 對象（未經 get_match_data 處理）"""
        matches = Match.query.filter_by(tournament_id=tournament_id).all()
        return matches if matches else []

    @staticmethod
    def update_match_winner(match_id, winner_name):
        """更新比賽勝者並連鎖更新後續比賽"""
        match = Match.query.get(match_id)
        if not match:
            return False
        
        # 更新當前比賽的勝者
        # ... 更新邏輯
        
        # 查找並更新後續比賽
        next_matches = Match.query.filter(
            (Match.prev_match1_id == match_id) | 
            (Match.prev_match2_id == match_id)
        ).all()
        
        for next_match in next_matches:
            if next_match.player1_from_match == match_id:
                next_match.player1_name = winner_name
            elif next_match.player2_from_match == match_id:
                next_match.player2_name = winner_name
            
            # 如果兩個選手都確定了，可以開始這場比賽
            if next_match.player1_name and next_match.player2_name:
                next_match.status = 'pending'
        
        db.session.commit()
        return True

    @staticmethod
    def determine_winner(match_id):
        """Once the match is finished, determine the winner"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError("Match not found")

        # 添加詳細的調試信息
        # print(f"=== Match {match_id} Debug Info ===")
        # print(f"Event type: {match.event_type}")
        # print(f"Scores: {match.player1_score} vs {match.player2_score}")
        # print(f"Player1 ID: {match.player1_id}, Player1 Name: {match.player1_name}")
        # print(f"Player2 ID: {match.player2_id}, Player2 Name: {match.player2_name}")
        # print(f"Team1 Player1 ID: {match.team1_player1_id}, Name: {match.team1_player1_name}")
        # print(f"Team1 Player2 ID: {match.team1_player2_id}, Name: {match.team1_player2_name}")
        # print(f"Team2 Player1 ID: {match.team2_player1_id}, Name: {match.team2_player1_name}")
        # print(f"Team2 Player2 ID: {match.team2_player2_id}, Name: {match.team2_player2_name}")

        # invalid score
        # if match.player1_score < 0 or match.player2_score < 0:
        #     raise ValueError('Invalid score. Score cannot be negative.')
        
        # draw
        # if match.player1_score == match.player2_score:
        #     raise ValueError("Match is a draw")

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
        
        # print(f"Before commit - winner1_id: {match.winner1_id}, winner2_id: {match.winner2_id}")
        # print(f"Before commit - loser1_id: {match.loser1_id}, loser2_id: {match.loser2_id}")
        
        db.session.commit()
        
        # print(f"After commit - winner1_id: {match.winner1_id}, winner2_id: {match.winner2_id}")
        # print(f"After commit - loser1_id: {match.loser1_id}, loser2_id: {match.loser2_id}")
        
        return {'winner_name': winner_name, 'loser_name': loser_name}
        
    @staticmethod
    def next_game(match_id):
        """Set the match to next game"""
        match = Match.query.get(match_id)
        if not match:
            return ValueError("Match not found")
        
        if match.current_game >= 3:
            return ValueError("Can only support 3 games")
        
        # save the score of the current game
        if match.current_game == 1:
            match.game1_score1 = match.player1_score
            match.game1_score2 = match.player2_score
            match.current_game += 1
        elif match.current_game == 2:
            match.game2_score1 = match.player1_score
            match.game2_score2 = match.player2_score
            match.current_game += 1
        elif match.current_game == 3:
            match.game3_score1 = match.player1_score
            match.game3_score2 = match.player2_score
            match.current_game += 1
        
        # check which player won the game
        if match.player1_score > match.player2_score:
            match.player1_game_won += 1
        elif match.player1_score < match.player2_score:
            match.player2_game_won += 1
        else:
            return ValueError("Game is a draw")
        
        # go to next game, reset the score and current game must be incremented
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

        # save the score
        if match.current_game == 1:
            match.game1_score1 = match.player1_score
            match.game1_score2 = match.player2_score
        elif match.current_game == 2:
            match.game2_score1 = match.player1_score
            match.game2_score2 = match.player2_score
        elif match.current_game == 3:
            match.game3_score1 = match.player1_score
            match.game3_score2 = match.player2_score
            
        # update player1_game_won and player2_game_won
        if match.player1_score > match.player2_score:
            match.player1_game_won += 1
        elif match.player1_score < match.player2_score:
            match.player2_game_won += 1
        else:
            return ValueError("Game is a draw")
        
        # set match.status to finished
        match.status = 'Finished'

        # determine the winner
        MatchService.determine_winner(match_id)

        db.session.commit()

        return get_match_data(match)