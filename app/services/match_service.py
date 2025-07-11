from ..models import Match, User, Event, db
from ..utils import get_match_data

class MatchService:
    """比賽相關的業務邏輯服務"""
    
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
        
        match.status = new_status
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