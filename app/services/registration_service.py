from sqlalchemy.sql.dml import ReturningInsert
from ..models import Registration, User, Tournament, Event, Group, db
from ..utils import get_user_by_name, check_repeated_registration
from datetime import datetime
import pandas as pd

class RegistrationService:
    """報名相關的業務邏輯服務"""
    
    @staticmethod
    def get_registrations_by_tournament(tournament_id):
        """獲取錦標賽的所有報名"""
        registrations = Registration.query.filter_by(tournament_id=tournament_id).all()
        if not registrations:
            return []
        
        registrations_data = []
        for registration in registrations:
            partner_name = None
            if registration.partner_id:
                partner_name = registration.partner.get_full_name() if registration.partner else None
            elif registration.partner_first_name and registration.partner_last_name:
                partner_name = f"{registration.partner_first_name} {registration.partner_last_name}"
            
            registration_data = {
                'id': registration.id,
                'tournament_id': registration.tournament_id,
                'tournament_name': registration.tournament.name,
                'user_id': registration.user_id if registration.user else None,
                'user_name': registration.user.get_full_name() if registration.user else f"{registration.player_first_name} {registration.player_last_name}",
                'status': registration.status,
                'partner_id': registration.partner_id if registration.partner else None,
                'partner_name': partner_name,
                'event_name': registration.event.name,
                'group_name': registration.group.name,
            }
            registrations_data.append(registration_data)
        
        return registrations_data

    @staticmethod
    def create_registration(tournament_id, player_info, registrations_info):
        """創建報名記錄"""
        player_first_name = player_info.get('firstName')
        player_last_name = player_info.get('lastName')
        player = get_user_by_name(player_first_name, player_last_name)
        
        if not player:
            raise ValueError("Player not found, please register first")
        
        player_id = player.id
        created_registrations = []

        for registration_info in registrations_info:
            event_id = registration_info.get('event_id')
            group_id = registration_info.get('group_id')
            is_doubles = registration_info.get('is_doubles')
            
            if check_repeated_registration(tournament_id, player_id, event_id, group_id):
                continue
            
            if is_doubles:
                partner_info = registration_info.get('partner_info')
                partner_first_name = partner_info.get('firstName')
                partner_last_name = partner_info.get('lastName')
                partner = get_user_by_name(partner_first_name, partner_last_name)
                
                registration_data = {
                    'tournament_id': tournament_id,
                    'user_id': player_id,
                    'event_id': event_id,
                    'group_id': group_id,
                    'status': 'pending',
                    'partner_id': partner.id if partner else None,
                    'partner_first_name': partner_first_name,
                    'partner_last_name': partner_last_name
                }
            else:
                registration_data = {
                    'tournament_id': tournament_id,
                    'user_id': player_id,
                    'event_id': event_id,
                    'group_id': group_id,
                    'status': 'pending',
                    'partner_id': None,
                    'partner_first_name': None,
                    'partner_last_name': None
                }
            
            new_registration = Registration(**registration_data)
            db.session.add(new_registration)
            created_registrations.append(new_registration)
        
        db.session.commit()
        return created_registrations


    @staticmethod
    def create_registration_from_excel(tournament_id, file):
        """從 Excel 資料創建報名記錄"""
        try:
            excel_data = pd.read_excel(file, engine='openpyxl')
            # print(f"Excel data: {excel_data}")

            created_registrations = []
            errors = []

            # 檢查必要欄位
            required_columns = ['First Name', 'Last Name', 'Email', 'Event', 'Group']
            if not all(col in excel_data.columns for col in required_columns):
                missing_columns = [col for col in required_columns if col not in excel_data.columns]
                return {
                    'success': False,
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }

            # 取得 event, group 對應
            tournament = Tournament.query.get(tournament_id)
            if not tournament:
                return {'success': False, 'error': 'Tournament not found'}

            # 取得所有 event
            events = Event.query.filter_by(tournament_id=tournament_id).all()
            event_map = {event.name: event.id for event in events}

            # 修改：使用 (event_name, group_name) 作為 key
            groups = Group.query.join(Event).filter(Event.tournament_id == tournament_id).all()
            group_map = {}
            for group in groups:
                event = Event.query.get(group.event_id)
                if not event:
                    errors.append(f"Event not found for group {group.name}")
                    continue
                key = (event.name, group.name)
                group_map[key] = group.id
                print(f"Group mapping: {event.name}-{group.name} -> Group ID {group.id}")

            # 用於追蹤每個 event-group 組合中已處理的搭檔
            processed_pairs = {}  # {(event_id, group_id): set of player pairs}

            row_num = 2  # Excel 資料從第2列開始
            for _, row in excel_data.iterrows():
                try:
                    first_name = str(row['First Name']).strip()
                    last_name = str(row['Last Name']).strip()
                    email = str(row['Email']).strip()
                    event_name = str(row['Event']).strip()
                    group_name = str(row['Group']).strip()
                    partner_first_name = str(row.get('Partner First Name', '')).strip()
                    partner_last_name = str(row.get('Partner Last Name', '')).strip()

                    if not all([first_name, last_name, email, event_name, group_name]):
                        errors.append(f"Row {row_num}: Missing required information")
                        continue

                    if event_name not in event_map:
                        errors.append(f"Row {row_num}: Event '{event_name}' not found in tournament")
                        continue
                    
                    # 修改：使用 (event_name, group_name) 作為 key
                    group_key = (event_name, group_name)
                    if group_key not in group_map:
                        errors.append(f"Row {row_num}: Group '{group_name}' not found in event '{event_name}'")
                        continue

                    user = get_user_by_name(first_name, last_name)
                    partner = get_user_by_name(partner_first_name, partner_last_name) if partner_first_name and partner_last_name else None

                    event_id = event_map[event_name]
                    group_id = group_map[group_key]  # 使用正確的 group_id

                    print(f"Row {row_num}: {event_name}-{group_name} -> Event ID {event_id}, Group ID {group_id}")

                    # 檢查是否為雙打
                    is_doubles = bool(partner_first_name and partner_last_name)
                    
                    if is_doubles:
                        # 創建標準化的搭檔組合（按字母順序排序，避免 player1,player2 和 player2,player1 重複）
                        player1_name = f"{first_name} {last_name}"
                        player2_name = f"{partner_first_name} {partner_last_name}"
                        
                        # 按字母順序排序，確保相同的搭檔組合只會被記錄一次
                        if player1_name < player2_name:
                            pair_key = f"{player1_name}|{player2_name}"
                        else:
                            pair_key = f"{player2_name}|{player1_name}"
                        
                        # 初始化這個 event-group 組合的已處理搭檔集合
                        if (event_id, group_id) not in processed_pairs:
                            processed_pairs[(event_id, group_id)] = set()
                        
                        # 檢查是否已經處理過這個搭檔組合
                        if pair_key in processed_pairs[(event_id, group_id)]:
                            errors.append(f"Row {row_num}: Duplicate doubles pair {player1_name} and {player2_name} in {event_name} {group_name}")
                            continue
                        
                        # 記錄這個搭檔組合
                        processed_pairs[(event_id, group_id)].add(pair_key)
                    else:
                        # 單打：檢查是否已經有這個選手的註冊
                        player_key = f"{first_name} {last_name}"
                        if (event_id, group_id) not in processed_pairs:
                            processed_pairs[(event_id, group_id)] = set()
                        
                        if player_key in processed_pairs[(event_id, group_id)]:
                            errors.append(f"Row {row_num}: Duplicate singles registration for {player_key} in {event_name} {group_name}")
                            continue
                        
                        processed_pairs[(event_id, group_id)].add(player_key)

                    registration_data = {
                        'tournament_id': tournament_id,
                        'user_id': user.id if user else None,
                        'event_id': event_id,
                        'group_id': group_id,
                        'status': 'confirmed',
                        'player_first_name': first_name,
                        'player_last_name': last_name,
                        'player_email': email,
                        'partner_id': partner.id if partner else None,
                        'partner_first_name': partner_first_name or None,
                        'partner_last_name': partner_last_name or None
                    }

                    # 檢查資料庫中是否已存在相同的註冊
                    existing_registration = Registration.query.filter_by(
                        tournament_id=tournament_id,
                        event_id=registration_data['event_id'],
                        group_id=registration_data['group_id'],
                        player_first_name=first_name,
                        player_last_name=last_name
                    ).first()
                    if existing_registration:
                        errors.append(f"Row {row_num}: Registration already exists in database for {first_name} {last_name}")
                        continue

                    registration = Registration(**registration_data)
                    db.session.add(registration)
                    created_registrations.append(registration)

                except Exception as e:
                    errors.append(f"Row {row_num}: Error processing - {str(e)}")
                row_num += 1

            if created_registrations:
                db.session.commit()

            return {
                'success': True,
                'created_count': len(created_registrations),
                'errors': errors,
                'total_rows': len(excel_data)
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }