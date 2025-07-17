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
            print(f"=== Creating tournament ===")
            print(f"Tournament info: {tournament_info}")
            print(f"Events info: {events_info}")
            
            # Convert date strings to datetime objects
            if 'start_date' in tournament_info and tournament_info['start_date']:
                tournament_info['start_date'] = datetime.fromisoformat(tournament_info['start_date'])
            
            if 'end_date' in tournament_info and tournament_info['end_date']:
                tournament_info['end_date'] = datetime.fromisoformat(tournament_info['end_date'])
            
            # Create tournament
            tournament = Tournament(**tournament_info)
            db.session.add(tournament)
            db.session.flush()
            print(f"Created tournament with ID: {tournament.id}")

            # Create events
            for event_info in events_info:
                print(f"=== Creating event ===")
                print(f"Event info: {event_info}")
                
                # Map event names to categories
                category_mapping = {
                    "Men's Single": 'MS',
                    "Women's Single": 'WS',
                    "Men's Doubles": 'MD',
                    "Women's Doubles": 'WD',
                    "Mixed Doubles": 'XD'
                }
                
                event_info['category'] = category_mapping.get(event_info['name'], 'MS')
                print(f"Mapped category: {event_info['category']}")

                event = Event()
                event.name = event_info['name']
                event.category = event_info['category']
                event.tournament_id = tournament.id
                db.session.add(event)
                db.session.flush()
                print(f"Created event: {event.name} (ID: {event.id})")

                # Create groups for each event
                for group_info in event_info['groups']:
                    print(f"=== Creating group ===")
                    print(f"Group info: {group_info}")
                    print(f"Event ID: {event.id}")
                    
                    format_exist = Format.query.filter_by(type=group_info['format']).first()
                    if not format_exist:
                        print(f"Format '{group_info['format']}' not found!")
                        raise ValueError(f"Format '{group_info['format']}' not found")
                    
                    print(f"Found format: {format_exist.type} (ID: {format_exist.id})")
                    
                    group = Group()
                    group.name = group_info['name']
                    group.event_id = event.id
                    group.format_id = format_exist.id
                    db.session.add(group)
                    db.session.flush()  # 立即獲取 Group ID
                    print(f"Created group: {group.name} (ID: {group.id}, Event ID: {group.event_id}, Format ID: {group.format_id})")
            
            db.session.commit()
            print(f"=== Tournament creation completed ===")
            return tournament
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in create_tournament: {e}")
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
            print(f"Found {len(registrations)} registrations for tournament {tournament_id}")
            
            if not registrations:
                raise ValueError("No registrations found for this tournament")
            
            # 2. 按 event 和 group 分組
            event_group_players = TournamentService._group_registrations_by_event_group(registrations)
            print(f"Grouped into {len(event_group_players)} event-group combinations")
            print(f"Event-group combinations: {list(event_group_players.keys())}")
            
            # 3. 為每個 event-group 組合生成對戰
            all_matches = []
            for (event_id, group_id), players_data in event_group_players.items():
                print(f"Processing event_id={event_id}, group_id={group_id} with {len(players_data)} players")
                print(f"Players data: {players_data}")
                
                event = Event.query.get(event_id)
                group = Group.query.get(group_id)
                print(f"Event ID: {event_id}, Group ID: {group_id}")
                if not group:
                    print(f"Group {group_id} not found, skipping")
                    continue
                # 這邊會出錯 format應該是elimination, 但卻是round robin
                format = Format.query.get(group.format_id)
                print(f"Format ID: {group.format_id}")
                if not format:
                    print(f"Format for group {group_id} not found, skipping")
                    continue
                
                if not event or not group or not format:
                    print(f"Missing event, group, or format, skipping")
                    continue
                
                print(f"Event: {event.name}, Group: {group.name}, Format: {format.type}")
                
                # 生成對戰組合
                matches = TournamentService._generate_matches_for_group(
                    players_data, event, group, format
                )
                print(f"Generated {len(matches)} matches for this group")
                
                # 創建 Match 記錄
                for match_data in matches:
                    match = TournamentService._create_match_record(match_data, tournament_id)
                    if match:
                        all_matches.append(match)
                        print(f"Created match {match.id}")
                    else:
                        print(f"Failed to create match for data: {match_data}")
            
            print(f"Total matches created: {len(all_matches)}")
            return all_matches
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in generate_matches_by_registration: {e}")
            raise e

    @staticmethod
    def _group_registrations_by_event_group(registrations):
        """
        將報名記錄按 event 和 group 分組，避免重複選手
        
        Returns:
            dict: {(event_id, group_id): [player_data, ...]}
        """
        event_group_players = {}
        processed_players = {}  # 用於追蹤已處理的選手
        
        for registration in registrations:
            event_id = registration.event_id
            group_id = registration.group_id
            key = (event_id, group_id)
            
            if key not in event_group_players:
                event_group_players[key] = []
                processed_players[key] = set()
            
            # 處理選手資料
            if registration.user:
                user_name = registration.user.get_full_name()
                user_id = registration.user_id
            else:
                user_name = f"{registration.player_first_name} {registration.player_last_name}"
                user_id = registration.user_id
            
            # 檢查是否為雙打
            is_doubles = bool(registration.partner_id or (registration.partner_first_name and registration.partner_last_name))
            
            if is_doubles:
                # 處理雙打搭檔
                if registration.partner_id and registration.partner:
                    partner_name = registration.partner.get_full_name()
                    partner_id = registration.partner_id
                elif registration.partner_first_name and registration.partner_last_name:
                    partner_name = f"{registration.partner_first_name} {registration.partner_last_name}"
                    partner_id = registration.partner_id
                else:
                    partner_name = None
                    partner_id = None
                
                if partner_name:
                    # 創建標準化的搭檔組合（按字母順序排序）
                    if user_name < partner_name:
                        pair_key = f"{user_name}|{partner_name}"
                    else:
                        pair_key = f"{partner_name}|{user_name}"
                    
                    # 檢查是否已經處理過這個搭檔組合
                    if pair_key not in processed_players[key]:
                        processed_players[key].add(pair_key)
                        
                        # 創建雙打選手資料
                        player_data = {
                            'user_id': user_id,
                            'user_name': user_name,
                            'partner_id': partner_id,
                            'partner_name': partner_name,
                            'is_doubles': True
                        }
                        event_group_players[key].append(player_data)
            else:
                # 單打選手 - 檢查是否重複
                player_key = f"{user_name}"
                if player_key not in processed_players[key]:
                    processed_players[key].add(player_key)
                    
                    player_data = {
                        'user_id': user_id,
                        'user_name': user_name,
                        'partner_id': None,
                        'partner_name': None,
                        'is_doubles': False
                    }
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
        print(f"Generating matches for {len(players_data)} players")
        print(f"Format type: {format.type}")
        
        if len(players_data) < 2:
            print(f"Not enough players ({len(players_data)}) to generate matches")
            return []
        
        # 根據比賽類型生成對戰
        if format.type == 'round_robin':
            matches = TournamentService._generate_round_robin_matches(players_data, event, group)
            print(f"Generated {len(matches)} round-robin matches")
            return matches
        elif format.type == 'elimination':
            matches = TournamentService._generate_elimination_matches(players_data, event, group)
            print(f"Generated {len(matches)} elimination matches")
            return matches
        else:
            print(f"Unknown format type: {format.type}")
            return []

    @staticmethod
    def _generate_round_robin_matches(players_data, event, group):
        """生成輪迴賽對戰組合"""
        matches = []
        
        # 從 Format 獲取分組大小
        format = Format.query.get(group.format_id)
        group_size = getattr(format, 'group_size', 4) or 4  # 使用 Format 的 group_size
        
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
        print(f"=== Generating elimination matches ===")
        print(f"Players: {[p['user_name'] for p in players_data]}")
        print(f"Total players: {len(players_data)}")
        
        matches = []
        
        if len(players_data) < 2:
            print("Not enough players for elimination")
            return matches
        
        # 計算需要的總槽位數
        total_slots = TournamentService._next_power_of_two(len(players_data))
        num_byes = total_slots - len(players_data)
        print(f"Total slots: {total_slots}, Byes: {num_byes}")
        
        # 隨機分配 bye
        players_copy = players_data.copy()
        random.shuffle(players_copy)
        byes = players_copy[:num_byes]
        print(f"Bye players: {[p['user_name'] for p in byes]}")
        
        # 重新洗牌
        random.shuffle(players_copy)
        
        round_number = 1
        current_round = []
        
        # 第一輪 - 簡化邏輯
        idx = 0
        while idx < len(players_copy):
            if idx == len(players_copy) - 1:
                # 最後一個選手，給他一個 BYE
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': players_copy[idx],
                    'player2_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None},
                    'round': round_number
                }
                print(f"Created BYE match for last player: {players_copy[idx]['user_name']}")
                idx += 1
            elif players_copy[idx] in byes:
                # BYE 比賽
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': players_copy[idx],
                    'player2_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None},
                    'round': round_number
                }
                print(f"Created BYE match for: {players_copy[idx]['user_name']}")
                idx += 1
            else:
                # 正常比賽
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': players_copy[idx],
                    'player2_data': players_copy[idx + 1],
                    'round': round_number
                }
                print(f"Created normal match: {players_copy[idx]['user_name']} vs {players_copy[idx + 1]['user_name']}")
                idx += 2
            
            current_round.append(match_data)
            matches.append(match_data)
        
        print(f"First round matches: {len(matches)}")
        
        # 後續輪次 - 簡化邏輯
        while len(current_round) > 1:
            round_number += 1
            next_round = []
            
            for i in range(0, len(current_round), 2):
                if i + 1 >= len(current_round):
                    # 處理奇數選手
                    match_data = {
                        'event_id': event.id,
                        'group_id': group.id,
                        'event_type': event.category,
                        'player1_data': {'user_id': None, 'user_name': f"Winner of Match {i+1}", 'partner_name': None},
                        'player2_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None},
                        'round': round_number
                    }
                    print(f"Created BYE match for odd player in round {round_number}")
                    next_round.append(match_data)
                    matches.append(match_data)
                    break
                
                # 正常比賽
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': {'user_id': None, 'user_name': f"Winner of Match {i+1}", 'partner_name': None},
                    'player2_data': {'user_id': None, 'user_name': f"Winner of Match {i+2}", 'partner_name': None},
                    'round': round_number
                }
                print(f"Created next round match: Winner of Match {i+1} vs Winner of Match {i+2}")
                next_round.append(match_data)
                matches.append(match_data)
            
            current_round = next_round
            print(f"Round {round_number} matches: {len(next_round)}")
        
        print(f"Total elimination matches: {len(matches)}")
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
            print(f"=== Creating match record ===")
            # print(f"Match data: {match_data}")
            
            p1_data = match_data['player1_data']
            p2_data = match_data['player2_data']
            
            print(f"Player 1: {p1_data}")
            print(f"Player 2: {p2_data}")
            
            # 檢查是否為 BYE 比賽
            is_bye_match = (p1_data['user_name'] == 'BYE' or p2_data['user_name'] == 'BYE')
            print(f"Is BYE match: {is_bye_match}")
            
            # 檢查是否為雙打
            is_doubles = (match_data['event_type'] in ['MD', 'WD', 'XD'] or 
                         p1_data.get('is_doubles', False) or 
                         p2_data.get('is_doubles', False))
            print(f"Is doubles: {is_doubles}")
            
            if is_doubles:
                # 雙打比賽
                if is_bye_match:
                    # BYE 雙打比賽
                    match_dict = {
                        'tournament_id': tournament_id,
                        'event_id': match_data['event_id'],
                        'group_id': match_data['group_id'],
                        'event_type': match_data['event_type'],
                        'player1_id': p1_data['user_id'],
                        'player2_id': p2_data['user_id'],
                        'player1_name': p1_data['user_name'],
                        'player2_name': p2_data['user_name'],
                        'player1_score': 0,
                        'player2_score': 0,
                        'status': 'Scheduled',
                        'team1_player1_id': p1_data['user_id'],
                        'team1_player2_id': p1_data.get('partner_id'),
                        'team2_player1_id': p2_data['user_id'],
                        'team2_player2_id': p2_data.get('partner_id'),
                        'team1_player1_name': p1_data['user_name'],
                        'team1_player2_name': p1_data.get('partner_name'),
                        'team2_player1_name': p2_data['user_name'],
                        'team2_player2_name': p2_data.get('partner_name')
                    }
                else:
                    # 正常雙打比賽
                    match_dict = {
                        'tournament_id': tournament_id,
                        'event_id': match_data['event_id'],
                        'group_id': match_data['group_id'],
                        'event_type': match_data['event_type'],
                        'player1_id': p1_data['user_id'],
                        'player2_id': p2_data['user_id'],
                        'player1_name': p1_data['user_name'],
                        'player2_name': p2_data['user_name'],
                        'player1_score': 0,
                        'player2_score': 0,
                        'status': 'Scheduled',
                        'team1_player1_id': p1_data['user_id'],
                        'team1_player2_id': p1_data.get('partner_id'),
                        'team2_player1_id': p2_data['user_id'],
                        'team2_player2_id': p2_data.get('partner_id'),
                        'team1_player1_name': p1_data['user_name'],
                        'team1_player2_name': p1_data.get('partner_name'),
                        'team2_player1_name': p2_data['user_name'],
                        'team2_player2_name': p2_data.get('partner_name')
                    }
            else:
                # 單打比賽
                if is_bye_match:
                    # BYE 單打比賽
                    match_dict = {
                        'tournament_id': tournament_id,
                        'event_id': match_data['event_id'],
                        'group_id': match_data['group_id'],
                        'event_type': match_data['event_type'],
                        'player1_id': p1_data['user_id'],
                        'player2_id': p2_data['user_id'],
                        'player1_name': p1_data['user_name'],
                        'player2_name': p2_data['user_name'],
                        'player1_score': 0,
                        'player2_score': 0,
                        'status': 'Scheduled'
                    }
                else:
                    # 正常單打比賽
                    match_dict = {
                        'tournament_id': tournament_id,
                        'event_id': match_data['event_id'],
                        'group_id': match_data['group_id'],
                        'event_type': match_data['event_type'],
                        'player1_id': p1_data['user_id'],
                        'player2_id': p2_data['user_id'],
                        'player1_name': p1_data['user_name'],
                        'player2_name': p2_data['user_name'],
                        'player1_score': 0,
                        'player2_score': 0,
                        'status': 'Scheduled'
                    }
            
            match = Match(**match_dict)
            db.session.add(match)
            db.session.commit()
            
            print(f"Successfully created match {match.id}")
            return match
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating match record: {e}")
            # print(f"Match data: {match_data}")
            import traceback
            traceback.print_exc()
            return None