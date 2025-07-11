from ..models import Tournament, Event, Group, Format, db
from datetime import datetime

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