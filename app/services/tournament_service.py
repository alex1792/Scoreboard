from ..models import Tournament, Event, Group, Format, db, Registration, Match
from datetime import datetime
import random

class TournamentService:
    """錦標賽相關的業務邏輯服務"""
    
    @staticmethod
    def get_all_tournaments():
        """獲取所有錦標賽"""
        tournaments = Tournament.query.all()
        if not tournaments:
            return []
        
        tournaments_data = []
        for tournament in tournaments:
            tournament_data = {
                'id': tournament.id,
                'name': tournament.name,
                'start_date': tournament.start_date.isoformat() if tournament.start_date else None,
                'end_date': tournament.end_date.isoformat() if tournament.end_date else None,
                'location': tournament.location,
                'status': tournament.status,
                'event_count': len(tournament.events)
            }
            tournaments_data.append(tournament_data)
        
        return tournaments_data

    @staticmethod
    def get_tournament_by_id(tournament_id):
        """根據ID獲取錦標賽詳情"""
        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            return None

        events = []
        for event in tournament.events:
            groups = []
            for group in event.groups:
                format = Format.query.get(group.format_id)
                group_data = {
                    'id': group.id,
                    'name': group.name,
                    'type': format.type if format else 'N/A'
                }
                groups.append(group_data)
            
            event_data = {
                'id': event.id,
                'name': event.name,
                'category': event.category,
                'groups': groups
            }
            events.append(event_data)

        tournament_data = {
            'id': tournament.id,
            'name': tournament.name,
            'start_date': tournament.start_date.isoformat() if tournament.start_date else None,
            'end_date': tournament.end_date.isoformat() if tournament.end_date else None,
            'location': tournament.location,
            'status': tournament.status,
            'events': events
        }
        
        return tournament_data

    @staticmethod
    def create_tournament(tournament_info, events_info):
        """創建新錦標賽"""
        try:
            # Convert date strings to datetime objects
            if 'start_date' in tournament_info and tournament_info['start_date']:
                tournament_info['start_date'] = datetime.fromisoformat(tournament_info['start_date'])
            
            if 'end_date' in tournament_info and tournament_info['end_date']:
                tournament_info['end_date'] = datetime.fromisoformat(tournament_info['end_date'])
            
            # Create tournament
            tournament = Tournament(**tournament_info)
            db.session.add(tournament)
            db.session.flush()

            # Create events
            for event_info in events_info:
                # Map event names to categories
                category_mapping = {
                    "Men's Single": 'MS',
                    "Women's Single": 'WS',
                    "Men's Doubles": 'MD',
                    "Women's Doubles": 'WD',
                    "Mixed Doubles": 'XD'
                }
                
                event_info['category'] = category_mapping.get(event_info['name'], 'MS')

                event = Event()
                event.name = event_info['name']
                event.category = event_info['category']
                event.tournament_id = tournament.id
                db.session.add(event)
                db.session.flush()

                # Create groups for each event
                for group_info in event_info['groups']:
                    format_exist = Format.query.filter_by(type=group_info['format']).first()
                    if not format_exist:
                        raise ValueError(f"Format '{group_info['format']}' not found")
                    
                    group = Group()
                    group.name = group_info['name']
                    group.event_id = event.id
                    group.format_id = format_exist.id
                    db.session.add(group)
            
            db.session.commit()
            return tournament
            
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def generate_matches_by_registration(tournament_id):
        """
        根據報名記錄生成對戰組合
        
        Args:
            tournament_id: 錦標賽ID
        
        Returns:
            list: 生成的比賽列表
        """
        try:
            # 1. 獲取錦標賽的所有報名記錄
            registrations = Registration.query.filter_by(tournament_id=tournament_id).all()
            # print(registrations)
            
            if not registrations:
                raise ValueError("No registrations found for this tournament")
            
            # 2. 按 event 和 group 分組
            event_group_players = TournamentService._group_registrations_by_event_group(registrations)
            
            # 3. 為每個 event-group 組合生成對戰
            all_matches = []
            for (event_id, group_id), players_data in event_group_players.items():
                event = Event.query.get(event_id)
                group = Group.query.get(group_id)
                if not group:
                    continue

                format = Format.query.get(group.format_id)
                if not format:
                    continue
                
                if not event or not group or not format:
                    continue
                
                # 生成對戰組合
                matches = TournamentService._generate_matches_for_group(
                    players_data, event, group, format
                )
                print(matches)
                
                # 創建 Match 記錄
                for match_data in matches:
                    match = TournamentService._create_match_record(match_data, tournament_id)
                    if match:
                        all_matches.append(match)
            
            return all_matches
            
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def _group_registrations_by_event_group(registrations):
        """
        將報名記錄按 event 和 group 分組
        
        Returns:
            dict: {(event_id, group_id): [player_data, ...]}
        """
        event_group_players = {}
        
        for registration in registrations:
            event_id = registration.event_id
            group_id = registration.group_id
            key = (event_id, group_id)
            
            if key not in event_group_players:
                event_group_players[key] = []
            
            # 處理選手資料
            player_data = {
                'user_id': registration.user_id,
                'user_name': registration.user.get_full_name(),
                'partner_id': registration.partner_id,
                'partner_name': None
            }
            
            # 處理雙打搭檔
            if registration.partner_id:
                player_data['partner_name'] = registration.partner.get_full_name()
            elif registration.partner_first_name and registration.partner_last_name:
                player_data['partner_name'] = f"{registration.partner_first_name} {registration.partner_last_name}"
            
            event_group_players[key].append(player_data)
        
        return event_group_players

    @staticmethod
    def _generate_matches_for_group(players_data, event, group, format):
        """
        為特定 group 生成對戰組合
        
        Args:
            players_data: 選手資料列表
            event: Event 物件
            group: Group 物件
            format: Format 物件
        
        Returns:
            list: 對戰組合列表
        """
        if len(players_data) < 2:
            return []
        
        # 根據比賽類型生成對戰
        if format.type == 'round_robin':
            return TournamentService._generate_round_robin_matches(players_data, event, group)
        elif format.type == 'elimination':
            return TournamentService._generate_elimination_matches(players_data, event, group)
        else:
            return []

    @staticmethod
    def _generate_round_robin_matches(players_data, event, group):
        """生成輪迴賽對戰組合"""
        matches = []
        
        # 分組（如果需要）
        group_size = getattr(group, 'group_size', 4) or 4
        groups = TournamentService._group_players(players_data, group_size)
        
        for group_idx, player_group in enumerate(groups):
            # 為每個小組生成輪迴賽
            for i in range(len(player_group)):
                for j in range(i + 1, len(player_group)):
                    player1 = player_group[i]
                    player2 = player_group[j]
                    
                    match_data = {
                        'event_id': event.id,
                        'group_id': group.id,
                        'event_type': event.category,
                        'player1_data': player1,
                        'player2_data': player2
                    }
                    matches.append(match_data)
        
        return matches

    @staticmethod
    def _generate_elimination_matches(players_data, event, group):
        """生成淘汰賽對戰組合"""
        matches = []
        
        # 計算需要的總槽位數
        total_slots = TournamentService._next_power_of_two(len(players_data))
        num_byes = total_slots - len(players_data)
        
        # 隨機分配 bye
        players_copy = players_data.copy()
        random.shuffle(players_copy)
        byes = players_copy[:num_byes]
        
        # 重新洗牌
        random.shuffle(players_copy)
        
        round_number = 1
        current_round = []
        
        # 第一輪
        idx = 0
        while idx < len(players_copy) - 1:
            if players_copy[idx] in byes:
                # BYE 比賽
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': players_copy[idx],
                    'player2_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None}
                }
                idx += 1
            else:
                # 正常比賽
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': players_copy[idx],
                    'player2_data': players_copy[idx + 1]
                }
                idx += 2
            
            current_round.append(match_data)
            matches.append(match_data)
        
        # 後續輪次
        while len(current_round) > 1:
            round_number += 1
            next_round = []
            
            for i in range(0, len(current_round), 2):
                if i + 1 >= len(current_round):
                    # 處理奇數選手
                    last_match = current_round[i]
                    match_data = {
                        'event_id': event.id,
                        'group_id': group.id,
                        'event_type': event.category,
                        'player1_data': {'user_id': None, 'user_name': f"Winner of {last_match['round']}-{i+1}", 'partner_name': None},
                        'player2_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None}
                    }
                    next_round.append(match_data)
                    matches.append(match_data)
                    break
                
                # 正常比賽
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': {'user_id': None, 'user_name': f"Winner of {current_round[i]['round']}-{i+1}", 'partner_name': None},
                    'player2_data': {'user_id': None, 'user_name': f"Winner of {current_round[i+1]['round']}-{i+2}", 'partner_name': None}
                }
                next_round.append(match_data)
                matches.append(match_data)
            
            current_round = next_round
        
        return matches

    @staticmethod
    def _group_players(players_data, group_size):
        """將選手分組"""
        players_copy = players_data.copy()
        random.shuffle(players_copy)
        
        groups = []
        while len(players_copy) >= group_size:
            group = players_copy[:group_size]
            groups.append(group)
            players_copy = players_copy[group_size:]
        
        if len(players_copy) > 0:
            groups.append(players_copy)
        
        return groups

    @staticmethod
    def _next_power_of_two(n):
        """計算大於等於 n 的最小 2 的冪"""
        if n < 1:
            return 1
        power = 1
        while power < n:
            power *= 2
        return power

    @staticmethod
    def _create_match_record(match_data, tournament_id):
        """創建 Match 記錄"""
        try:
            # 根據比賽類型創建 Match
            if match_data['event_type'] in ['MS', 'WS']:  # 單打
                match_dict = {
                    'tournament_id': tournament_id,
                    'event_id': match_data['event_id'],
                    'group_id': match_data['group_id'],
                    'event_type': match_data['event_type'],
                    'player1_id': match_data['player1_data']['user_id'],
                    'player2_id': match_data['player2_data']['user_id'],
                    'player1_score': 0,
                    'player2_score': 0,
                    'status': 'Scheduled',
                    # 為雙打欄位設置預設值（因為它們是 NOT NULL）
                    'team1_player1_id': match_data['player1_data']['user_id'],
                    'team1_player2_id': match_data['player1_data']['user_id'],  # 單打時設為同一個人
                    'team2_player1_id': match_data['player2_data']['user_id'],
                    'team2_player2_id': match_data['player2_data']['user_id']   # 單打時設為同一個人
                }
            else:  # 雙打
                # 處理雙打選手
                p1_data = match_data['player1_data']
                p2_data = match_data['player2_data']
                
                # 如果是 BYE 比賽，特殊處理
                if p1_data['user_name'] == 'BYE' or p2_data['user_name'] == 'BYE':
                    # 對於 BYE 比賽，我們需要特殊處理
                    bye_user_id = 0  # 或者創建一個特殊的 BYE 用戶
                    match_dict = {
                        'tournament_id': tournament_id,
                        'event_id': match_data['event_id'],
                        'group_id': match_data['group_id'],
                        'event_type': match_data['event_type'],
                        'player1_id': p1_data['user_id'] or bye_user_id,
                        'player2_id': p2_data['user_id'] or bye_user_id,
                        'player1_score': 0,
                        'player2_score': 0,
                        'status': 'Scheduled',
                        'team1_player1_id': p1_data['user_id'] or bye_user_id,
                        'team1_player2_id': p1_data['partner_id'] or bye_user_id,
                        'team2_player1_id': p2_data['user_id'] or bye_user_id,
                        'team2_player2_id': p2_data['partner_id'] or bye_user_id
                    }
                else:
                    # 正常雙打比賽
                    match_dict = {
                        'tournament_id': tournament_id,
                        'event_id': match_data['event_id'],
                        'group_id': match_data['group_id'],
                        'event_type': match_data['event_type'],
                        'player1_id': p1_data['user_id'],  # 主要選手
                        'player2_id': p2_data['user_id'],  # 主要選手
                        'player1_score': 0,
                        'player2_score': 0,
                        'status': 'Scheduled',
                        'team1_player1_id': p1_data['user_id'],
                        'team1_player2_id': p1_data['partner_id'] or p1_data['user_id'],  # 如果沒有搭檔，設為自己
                        'team2_player1_id': p2_data['user_id'],
                        'team2_player2_id': p2_data['partner_id'] or p2_data['user_id']   # 如果沒有搭檔，設為自己
                    }
            
            match = Match(**match_dict)
            db.session.add(match)
            db.session.commit()
            
            return match
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating match record: {e}")
            print(f"Match data: {match_data}")  # 加入除錯資訊
            return None