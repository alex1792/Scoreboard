from ..models import Registration, User, Tournament, Event, Group, db
from ..utils import get_user_by_name, check_repeated_registration
from datetime import datetime

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
                'user_id': registration.user_id,
                'user_name': registration.user.get_full_name(),
                'status': registration.status,
                'partner_id': registration.partner_id,
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