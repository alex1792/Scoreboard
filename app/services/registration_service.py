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
            print(f"Excel data: {excel_data}")

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

            # 取得所有 group（透過 event_id）
            event_ids = [event.id for event in events]
            groups = Group.query.filter(Group.event_id.in_(event_ids)).all()
            group_map = {group.name: group.id for group in groups}

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
                    if group_name not in group_map:
                        errors.append(f"Row {row_num}: Group '{group_name}' not found in tournament")
                        continue

                    user = get_user_by_name(first_name, last_name)
                    partner = get_user_by_name(partner_first_name, partner_last_name) if partner_first_name and partner_last_name else None

                    registration_data = {
                        'tournament_id': tournament_id,
                        'user_id': user.id if user else None,
                        'event_id': event_map[event_name],
                        'group_id': group_map[group_name],
                        'status': 'confirmed',
                        'player_first_name': first_name,
                        'player_last_name': last_name,
                        'player_email': email,
                        'partner_id': partner.id if partner else None,
                        'partner_first_name': partner_first_name or None,
                        'partner_last_name': partner_last_name or None
                    }

                    existing_registration = Registration.query.filter_by(
                        tournament_id=tournament_id,
                        event_id=registration_data['event_id'],
                        group_id=registration_data['group_id'],
                        player_first_name=first_name,
                        player_last_name=last_name
                    ).first()
                    if existing_registration:
                        # errors.append(f"Row {int(index)+2}: Registration already exists for {first_name} {last_name}")
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