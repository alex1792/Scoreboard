from sqlalchemy import false, or_

from app import tournament
from ..models import Tournament, Event, Group, Format, db, Registration, Match, Schedule
from datetime import datetime
import random
from ..utils import get_match_data

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from flask import send_file
from io import BytesIO


class TournamentService:
    """Tournament related business logic services"""
    
    @staticmethod
    def get_all_tournaments():
        """return a list of all dictionaries of tournaments data"""
        tournaments = Tournament.query.all()
        if not tournaments:
            return []
        
        tournaments_data = []
        for tournament in tournaments:
            tournament_data = {
                'id': tournament.id,
                'name': tournament.name,
                'description': tournament.description,
                'start_date': tournament.start_date.isoformat() if tournament.start_date else None,
                'end_date': tournament.end_date.isoformat() if tournament.end_date else None,
                'location': tournament.location,
                'status': tournament.status,
                'event_count': len(tournament.events),
                'host_id': tournament.host_id
            }
            tournaments_data.append(tournament_data)
        
        return tournaments_data

    @staticmethod
    def get_tournament_by_id(tournament_id):
        """return a dictionary of tournament data according to tournament_id"""
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
            'description': tournament.description,
            'start_date': tournament.start_date.isoformat() if tournament.start_date else None,
            'end_date': tournament.end_date.isoformat() if tournament.end_date else None,
            'location': tournament.location,
            'status': tournament.status,
            'host_id': tournament.host_id,
            'events': events
        }
        
        return tournament_data

    @staticmethod
    def create_tournament(tournament_info, events_info):
        """Create a new tournament
        Args:
            tournament_info: a dictionary of tournament data
            events_info: a list of dictionaries of event data
        Returns:
            tournament: a dictionary of tournament data
        """
        try:
            # print(f"=== Creating tournament ===")
            # print(f"Tournament info: {tournament_info}")
            # print(f"Events info: {events_info}")
            
            # Convert date strings to datetime objects
            if 'start_date' in tournament_info and tournament_info['start_date']:
                tournament_info['start_date'] = datetime.fromisoformat(tournament_info['start_date'])
            
            if 'end_date' in tournament_info and tournament_info['end_date']:
                tournament_info['end_date'] = datetime.fromisoformat(tournament_info['end_date'])

            # # convert time strings to time objects
            # if 'start_time' in tournament_info and tournament_info['start_time']:
            #     tournament_info['start_time'] = datetime.strptime(tournament_info['start_time'], '%H:%M').time()
            
            # if 'end_time' in tournament_info and tournament_info['end_time']:
            #     tournament_info['end_time'] = datetime.strptime(tournament_info['end_time'], '%H:%M').time()
            
            # # convert match_duration to integer
            # if 'match_duration' in tournament_info:
            #     tournament_info['match_duration'] = int(tournament_info['match_duration'])
            
            # Create tournament
            tournament = Tournament(**tournament_info)
            db.session.add(tournament)
            db.session.flush()
            # print(f"Created tournament with ID: {tournament.id}")

            # Create events
            for event_info in events_info:
                # print(f"=== Creating event ===")
                # print(f"Event info: {event_info}")
                
                # Map event names to categories
                category_mapping = {
                    "Men's Single": 'MS',
                    "Women's Single": 'WS',
                    "Men's Doubles": 'MD',
                    "Women's Doubles": 'WD',
                    "Mixed Doubles": 'XD'
                }
                
                event_info['category'] = category_mapping.get(event_info['name'], 'MS')
                # print(f"Mapped category: {event_info['category']}")

                event = Event()
                event.name = event_info['name']
                event.category = event_info['category']
                event.tournament_id = tournament.id
                db.session.add(event)
                db.session.flush()
                # print(f"Created event: {event.name} (ID: {event.id})")

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
                    db.session.flush()
            
            db.session.commit()
            return tournament
            
        except Exception as e:
            db.session.rollback()
            # print(f"Error in create_tournament: {e}")
            raise e

    @staticmethod
    def delete_tournament(tournament_id):
        """delete a tournament according to tournament_id"""
        try:
            tournament = Tournament.query.get(tournament_id)
            if not tournament:
                raise ValueError(f"Tournament with ID {tournament_id} not found")
            
            db.session.delete(tournament)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            # print(f"Error in delete_tournament: {e}")
            raise e
            return False
                
    @staticmethod
    def generate_matches_by_registration(tournament_id):
        """
        Generate matches based on tournament id and registration data stored in the database
        
        Args:
            tournament_id: tournament id
        
        Returns:
            list: generated matches
        """
        try:
            # 1. get all registrations for the tournament
            registrations = Registration.query.filter_by(tournament_id=tournament_id).all()
            # print(f"Found {len(registrations)} registrations for tournament {tournament_id}")
            
            if not registrations:
                raise ValueError("No registrations found for this tournament")
            
            # 2. group registrations by event and group
            event_group_players = TournamentService._group_registrations_by_event_group(registrations)
            
            # 3. generate matches for each event-group combination
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
                
                
                # generate matches for the group
                matches = TournamentService._generate_matches_for_group(players_data, event, group, format)
                
                # create match records
                created_matches = {}  # key: (round, match_number)
                
                for match_data in matches:
                    # if the match is not the first round, set the prev_match_id
                    if match_data.get('round', 1) > 1:
                        # calculate the prev_match_id
                        prev_round = match_data['round'] - 1
                        prev_match1_number = (match_data['match_number'] - 1) * 2 + 1
                        prev_match2_number = prev_match1_number + 1
                        
                        # get the prev_match_id from the created matches
                        prev_match1_key = (prev_round, prev_match1_number)
                        prev_match2_key = (prev_round, prev_match2_number)
                        
                        if prev_match1_key in created_matches:
                            match_data['prev_match1_id'] = created_matches[prev_match1_key].id
                        if prev_match2_key in created_matches:
                            match_data['prev_match2_id'] = created_matches[prev_match2_key].id
                    
                    match = TournamentService._create_match_record(match_data, tournament_id)
                    if match:
                        # store the created matches
                        all_matches.append(match)
                        created_matches[(match_data['round'], match_data['match_number'])] = match
                    else:
                        print(f"Failed to create match for data: {match_data}")
            
            # print(f"Total matches created: {len(all_matches)}")
            return all_matches
            
        except Exception as e:
            db.session.rollback()
            # print(f"Error in generate_matches_by_registration: {e}")
            raise e

    @staticmethod
    def get_schedule_data(schedule_id):
        """return a dictionary of schedule data according to schedule_id"""
        
        # get the dchedule from database according to schedule_id
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return None
        
        def get_player_names(match):
            """get the player names according to the match type"""
            if match.event_type in ['MS', 'WS']:  # single
                player1 = match.player1_name or 'TBD'
                player2 = match.player2_name or 'TBD'
                
                # handle the winner of elimination match
                if 'Winner of Match' in player1:
                    player1 = f"Winner of {player1}"
                if 'Winner of Match' in player2:
                    player2 = f"Winner of {player2}"
                    
            else:  # Double (MD, WD, XD) team1 vs team2
                # team1
                team1_p1 = match.team1_player1_name or ''
                team1_p2 = match.team1_player2_name or ''
                
                # team2
                team2_p1 = match.team2_player1_name or ''
                team2_p2 = match.team2_player2_name or ''
                
                # check if the player name incluedes 'winner of the match
                if 'Winner of Match' in team1_p1:
                    player1 = f"Winner of {team1_p1}"
                elif team1_p1 and team1_p2:
                    player1 = f"{team1_p1} / {team1_p2}"
                else:
                    player1 = 'TBD'
                
                if 'Winner of Match' in team2_p1:
                    player2 = f"Winner of {team2_p1}"
                elif team2_p1 and team2_p2:
                    player2 = f"{team2_p1} / {team2_p2}"
                else:
                    player2 = 'TBD'
            
            return player1, player2
        
        # group the matches by date and batch
        schedule_by_date = {}
        for item in schedule.schedule_items:
            date_str = item.scheduled_date.strftime('%Y-%m-%d')
            
            if date_str not in schedule_by_date:
                schedule_by_date[date_str] = {}
            
            batch_num = item.batch_number
            if batch_num not in schedule_by_date[date_str]:
                schedule_by_date[date_str][batch_num] = []
            
            match = item.match
            
            # get the player names
            player1, player2 = get_player_names(match)
            
            match_info = {
                'court': item.court_number,
                'time': f"{item.scheduled_start_time.strftime('%H:%M')} - {item.scheduled_end_time.strftime('%H:%M')}",
                'category': match.event_type,
                'player1': player1,
                'player2': player2,
                'status': item.status,
                'round': match.round,
                'match_number': match.match_number
            }
            
            schedule_by_date[date_str][batch_num].append(match_info)
        
        return {
            'schedule_id': schedule.id,
            'total_matches': schedule.total_matches,
            'schedule_by_date': schedule_by_date
        }
    
    @staticmethod
    def get_schedule_by_tournament(tournament_id):
        """Get the tournament's schedule data"""
        # get the latest schedule for the tournament
        schedule = Schedule.query.filter_by(tournament_id=tournament_id).order_by(Schedule.created_at.desc()).first()
        if not schedule:
            return None
        
        # call the get_schedule_data method
        return TournamentService.get_schedule_data(schedule.id)

    @staticmethod
    def _group_registrations_by_event_group(registrations):
        """
        Group the registration by event and group to avoid duplicate players
        
        Returns:
            dict: {(event_id, group_id): [player_data, ...]}
        """
        event_group_players = {}
        processed_players = {}  # to handle the duplicate players
        
        for registration in registrations:
            event_id = registration.event_id
            group_id = registration.group_id
            key = (event_id, group_id)
            
            if key not in event_group_players:
                event_group_players[key] = []
                processed_players[key] = set()
            
            # handle the player info
            if registration.user:
                user_name = registration.user.get_full_name()
                user_id = registration.user_id
            else:
                user_name = f"{registration.player_first_name} {registration.player_last_name}"
                user_id = registration.user_id
            
            # check if the registration is a doubles match
            is_doubles = bool(registration.partner_id or (registration.partner_first_name and registration.partner_last_name))
            
            if is_doubles:
                # handle the doubles match partner info
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
                    # standardize the partner name (sort by alphabet)
                    if user_name < partner_name:
                        pair_key = f"{user_name}|{partner_name}"
                    else:
                        pair_key = f"{partner_name}|{user_name}"
                    
                    # check if the pair has been processed
                    if pair_key not in processed_players[key]:
                        processed_players[key].add(pair_key)
                        
                        # create the doubles player data
                        player_data = {
                            'user_id': user_id,
                            'user_name': user_name,
                            'partner_id': partner_id,
                            'partner_name': partner_name,
                            'is_doubles': True
                        }

                        # add the player data to the event_group_players
                        event_group_players[key].append(player_data)
            else:
                # single player - check if the player has been processed
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
                    # add the player data into the event_group_players
                    event_group_players[key].append(player_data)
        
        return event_group_players

    @staticmethod
    def _generate_matches_for_group(players_data, event, group, format):
        """
       generate matches for specific group
        
        Args:
            players_data: a list of player data
            event: Event object
            group: Group object
            format: Format object
        
        Returns:
            list: a list of match data
        """
        # print(f"Generating matches for {len(players_data)} players")
        # print(f"Format type: {format.type}")
        
        if len(players_data) < 2:
            # print(f"Not enough players ({len(players_data)}) to generate matches")
            return []
        
        # generate matches according to the format type
        if format.type == 'round_robin':
            matches = TournamentService._generate_round_robin_matches(players_data, event, group)
            # print(f"Generated {len(matches)} round-robin matches")
            return matches
        elif format.type == 'elimination':
            matches = TournamentService._generate_elimination_matches(players_data, event, group, event.tournament_id)
            # print(f"Generated {len(matches)} elimination matches")
            return matches
        else:
            # print(f"Unknown format type: {format.type}")
            return []

    @staticmethod
    def _generate_round_robin_matches(players_data, event, group):
        """generate pure round robin matches - all players have to play against each other"""
        matches = []
        match_number = 1
        
        # print(f"=== Generating pure round robin matches ===")
        # print(f"Total players: {len(players_data)}")
        # print(f"Players: {[p['user_name'] for p in players_data]}")
        
        # generate the matches according to the number of players
        for i in range(len(players_data)):
            for j in range(i + 1, len(players_data)):
                player1 = players_data[i]
                player2 = players_data[j]
                
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': player1,
                    'player2_data': player2,
                    'round': 1,  # round robin is always the first round
                    'match_number': match_number,
                    'prev_match1_id': None,
                    'prev_match2_id': None,
                    'player1_from_match': None,
                    'player2_from_match': None
                }
                matches.append(match_data)
                match_number += 1
                print(f"Created match {match_number-1}: {player1['user_name']} vs {player2['user_name']}")
        
        # verify the number of matches: C(n,2) = n * (n-1) / 2
        expected_matches = len(players_data) * (len(players_data) - 1) // 2
        # print(f"Total matches created: {len(matches)}")
        # print(f"Expected matches (C({len(players_data)},2)): {expected_matches}")
        
        if len(matches) != expected_matches:
            print(f"WARNING: Created {len(matches)} matches, expected {expected_matches}")
        
        return matches

    @staticmethod
    def _generate_elimination_matches(players_data, event, group, tournament_id):
        """Generate elimination matches"""
        all_matches = []  # to store all the matches
        
        if len(players_data) < 2:
            # print("Not enough players for elimination")
            return all_matches
        
        # calculate the total number of slots
        total_slots = TournamentService._next_power_of_two(len(players_data))
        num_byes = total_slots - len(players_data)
        # print(f"Total slots: {total_slots}, Byes: {num_byes}")
        
        # 確保第一輪有正確數量的比賽
        first_round_matches = total_slots // 2
        # print(f"First round should have {first_round_matches} matches")
        
        # randomly assign bye to players in the first round if needed
        players_copy = players_data.copy()
        random.shuffle(players_copy)
        byes = players_copy[:num_byes]
        # print(f"Bye players: {[p['user_name'] for p in byes]}")
        
        # re-shuffle the players
        random.shuffle(players_copy)
        
        round_number = 1
        current_round = []
        match_number = 1
        
        # First Round - 確保生成正確數量的比賽
        idx = 0
        while len(current_round) < first_round_matches:
            if idx >= len(players_copy):
                # 如果玩家不夠，添加 BYE vs BYE 比賽
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None},
                    'player2_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None},
                    'round': round_number,
                    'match_number': match_number,
                    'prev_match1_id': None,
                    'prev_match2_id': None,
                    'player1_from_match': None,
                    'player2_from_match': None
                }
                # print(f"Created BYE vs BYE match")
            elif idx == len(players_copy) - 1:
                # last player, his opponent is BYE
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': players_copy[idx],
                    'player2_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None},
                    'round': round_number,
                    'match_number': match_number,
                    'prev_match1_id': None,
                    'prev_match2_id': None,
                    'player1_from_match': None,
                    'player2_from_match': None
                }
                # print(f"Created BYE match for last player: {players_copy[idx]['user_name']}")
                idx += 1
            elif players_copy[idx] in byes:
                # BYE Match
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': players_copy[idx],
                    'player2_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None},
                    'round': round_number,
                    'match_number': match_number,
                    'prev_match1_id': None,
                    'prev_match2_id': None,
                    'player1_from_match': None,
                    'player2_from_match': None
                }
                # print(f"Created BYE match for: {players_copy[idx]['user_name']}")
                idx += 1
            else:
                # Regular Match
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': players_copy[idx],
                    'player2_data': players_copy[idx + 1],
                    'round': round_number,
                    'match_number': match_number,
                    'prev_match1_id': None,
                    'prev_match2_id': None,
                    'player1_from_match': None,
                    'player2_from_match': None
                }
                # print(f"Created normal match: {players_copy[idx]['user_name']} vs {players_copy[idx + 1]['user_name']}")
                idx += 2
            
            current_round.append(match_data)
            match_number += 1
        
        # print(f"First round matches: {len(current_round)}")
        
        # 繼續生成後續輪次...
        # next rounds - need to save the previous round matches
        while len(current_round) > 1:
            round_number += 1
            next_round = []
            match_number = 1
            
            # don't save the matches to the database immediately, only create match_data
            for i in range(0, len(current_round), 2):
                if i + 1 >= len(current_round):
                    # handle the odd player
                    prev_match_data = current_round[i]
                    match_data = {
                        'event_id': event.id,
                        'group_id': group.id,
                        'event_type': event.category,
                        'player1_data': {'user_id': None, 'user_name': f"Winner of Match {prev_match_data['match_number']}", 'partner_name': None},
                        'player2_data': {'user_id': None, 'user_name': 'BYE', 'partner_name': None},
                        'round': round_number,
                        'match_number': match_number,
                        'prev_match1_id': prev_match_data.get('id'),  # use the actual id
                        'prev_match2_id': None,
                        'player1_from_match': prev_match_data.get('id'),
                        'player2_from_match': None
                    }
                    # print(f"Created BYE match for odd player in round {round_number}")
                    next_round.append(match_data)
                    match_number += 1
                    break
                
                # regular match
                prev_match1_data = current_round[i]
                prev_match2_data = current_round[i+1]
                
                match_data = {
                    'event_id': event.id,
                    'group_id': group.id,
                    'event_type': event.category,
                    'player1_data': {'user_id': None, 'user_name': f"Winner of Match {prev_match1_data['match_number']}", 'partner_name': None},
                    'player2_data': {'user_id': None, 'user_name': f"Winner of Match {prev_match2_data['match_number']}", 'partner_name': None},
                    'round': round_number,
                    'match_number': match_number,
                    'prev_match1_id': prev_match1_data.get('id'),  # use the actual id
                    'prev_match2_id': prev_match2_data.get('id'),  # use the actual id
                    'player1_from_match': prev_match1_data.get('id'),
                    'player2_from_match': prev_match2_data.get('id')
                }
                # print(f"Created next round match: Winner of Match {prev_match1_data['match_number']} vs Winner of Match {prev_match2_data['match_number']}")
                next_round.append(match_data)
                match_number += 1
            
            # add the current round matches to all_matches
            all_matches.extend(current_round)
            
            # update current_round to the next round
            current_round = next_round
            # print(f"Round {round_number} matches: {len(next_round)}")
            
        # add the last round matches to all_matches (final match)
        all_matches.extend(current_round)
        
        # print(f"Total elimination matches: {len(all_matches)}")
        return all_matches

    @staticmethod
    def _group_players(players_data, group_size):
        """group the players into groups"""
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
        """calculate the smallest power of 2 greater than or equal to n"""
        if n < 1:
            return 1
        power = 1
        while power < n:
            power *= 2
        return power

    @staticmethod
    def _create_match_record(match_data, tournament_id):
        """create a match record"""
        try:
            # print(f"=== Creating match record ===")
            
            p1_data = match_data['player1_data']
            p2_data = match_data['player2_data']
            
            # print(f"Player 1: {p1_data}")
            # print(f"Player 2: {p2_data}")
            
            # check if the match is a bye match
            is_bye_match = (p1_data['user_name'] == 'BYE' or p2_data['user_name'] == 'BYE')
            # print(f"Is BYE match: {is_bye_match}")
            
            # check if the match is a doubles match
            is_doubles = (match_data['event_type'] in ['MD', 'WD', 'XD'] or 
                         p1_data.get('is_doubles', False) or 
                         p2_data.get('is_doubles', False))
            # print(f"Is doubles: {is_doubles}")
            
            # basic match data
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
            
            # elimination match related fields
            if 'round' in match_data:
                match_dict.update({
                    'round': match_data['round'],
                    'match_number': match_data['match_number'],
                    'prev_match1_id': match_data.get('prev_match1_id'),
                    'prev_match2_id': match_data.get('prev_match2_id'),
                    'next_match_id': match_data.get('next_match_id'),
                    'player1_from_match': match_data.get('player1_from_match'),
                    'player2_from_match': match_data.get('player2_from_match')
                })
            else:
                match_dict.update({'round': None, 'match_number': None})
            
            if is_doubles:
                # doubles match - add doubles related fields
                if 'Winner of Match' in p1_data['user_name'] or 'Winner of Match' in p2_data['user_name']:
                    # winner of the match - only set the first player name
                    match_dict.update({
                        'team1_player1_id': p1_data['user_id'],
                        'team1_player2_id': None,
                        'team2_player1_id': p2_data['user_id'],
                        'team2_player2_id': None,
                        'team1_player1_name': p1_data['user_name'],
                        'team1_player2_name': None,
                        'team2_player1_name': p2_data['user_name'],
                        'team2_player2_name': None
                    })
                else:
                    # first round match - set the doubles players
                    match_dict.update({
                        'team1_player1_id': p1_data['user_id'],
                        'team1_player2_id': p1_data.get('partner_id'),
                        'team2_player1_id': p2_data['user_id'],
                        'team2_player2_id': p2_data.get('partner_id'),
                        'team1_player1_name': p1_data['user_name'],
                        'team1_player2_name': p1_data.get('partner_name'),
                        'team2_player1_name': p2_data['user_name'],
                        'team2_player2_name': p2_data.get('partner_name')
                    })
        
            # handle the bye match - automatically set the winner
            if is_bye_match:
                # determine which one is the bye, which one is the actual player
                if p1_data['user_name'] == 'BYE':
                    actual_player = p2_data
                    bye_player = p1_data
                else:
                    actual_player = p1_data
                    bye_player = p2_data
                
                # set the winner info
                if is_doubles:
                    match_dict.update({
                        'winner1_id': actual_player['user_id'],
                        'winner2_id': actual_player.get('partner_id'),
                        'loser1_id': bye_player['user_id'],
                        'loser2_id': None,
                        'winner_name': f"{actual_player['user_name']} / {actual_player.get('partner_name', '')}",
                        'loser_name': 'BYE',
                        'status': 'Finished',  # bye match is automatically finished
                    })
                else:
                    match_dict.update({
                        'winner1_id': actual_player['user_id'],
                        'winner2_id': None,
                        'loser1_id': bye_player['user_id'],
                        'loser2_id': None,
                        'winner_name': actual_player['user_name'],
                        'loser_name': 'BYE',
                        'status': 'Finished',  # bye match is automatically finished
                    })
        
            match = Match(**match_dict)
            db.session.add(match)
            db.session.flush()  # get the match.id
            
            # update the next_match_id of the previous round matches
            if match_data.get('prev_match1_id'):
                prev_match1 = Match.query.get(match_data['prev_match1_id'])
                if prev_match1:
                    prev_match1.next_match_id = match.id
            
            if match_data.get('prev_match2_id'):
                prev_match2 = Match.query.get(match_data['prev_match2_id'])
                if prev_match2:
                    prev_match2.next_match_id = match.id
            
            db.session.commit()
            
            # print(f"Successfully created match {match.id}")
            return match
            
        except Exception as e:
            db.session.rollback()
            # print(f"Error creating match record: {e}")
            return None

    @staticmethod
    def process_bye_matches_after_schedule(tournament_id):
        """
        after creating schedule, we need to process the bye matches
        and update the next match's players
        """
        try:
            # get all elimination matches
            elimination_matches = Match.query.join(Event).join(Group).join(Format).filter(
                Match.tournament_id == tournament_id,
                Format.type == 'elimination'
            ).order_by(Match.round, Match.match_number).all()
            
            # print(f"Processing BYE matches for tournament {tournament_id}")
            # print(f"Found {len(elimination_matches)} elimination matches")
            
            # group by round
            matches_by_round = {}
            for match in elimination_matches:
                round_num = match.round or 1
                if round_num not in matches_by_round:
                    matches_by_round[round_num] = []
                matches_by_round[round_num].append(match)
            
            # start from the first round
            for round_num in sorted(matches_by_round.keys()):
                # print(f"Processing Round {round_num}")
                round_matches = matches_by_round[round_num]
                
                for match in round_matches:
                    # check if the match is a bye match
                    if TournamentService._is_bye_match(match):
                        # print(f"Found BYE match: {match.id}")
                        
                        # determine which one is the bye, which one is the actual player
                        bye_player, actual_player = TournamentService._identify_bye_and_actual_player(match)
                        
                        if actual_player:
                            # automatically set the winner
                            TournamentService._set_bye_match_winner(match, actual_player)
                            
                            # update the next match
                            TournamentService._update_next_match_after_bye(match, actual_player)
                            
                            # print(f"BYE match {match.id} processed: {actual_player} advances")
            
            db.session.commit()
            # print("BYE matches processing completed")
            return True
            
        except Exception as e:
            db.session.rollback()
            # print(f"Error processing BYE matches: {e}")
            raise e

    @staticmethod
    def _is_bye_match(match):
        """check if the match is a bye match"""
        return (
            match.player1_name == 'BYE' or match.player2_name == 'BYE' or
            match.team1_player1_name == 'BYE' or match.team1_player2_name == 'BYE' or
            match.team2_player1_name == 'BYE' or match.team2_player2_name == 'BYE'
        )

    @staticmethod
    def _identify_bye_and_actual_player(match):
        """identify the bye and actual player"""
        if match.event_type in ['MD', 'WD', 'XD']:
            # doubles match
            if match.team1_player1_name == 'BYE' or match.team1_player2_name == 'BYE':
                # Team 1 has BYE, Team 2 advances
                if match.team2_player1_name and match.team2_player2_name:
                    return 'BYE', f"{match.team2_player1_name} / {match.team2_player2_name}"
            elif match.team2_player1_name == 'BYE' or match.team2_player2_name == 'BYE':
                # Team 2 has BYE, Team 1 advances
                if match.team1_player1_name and match.team1_player2_name:
                    return 'BYE', f"{match.team1_player1_name} / {match.team1_player2_name}"
        else:
            # singles match
            if match.player1_name == 'BYE':
                return 'BYE', match.player2_name
            elif match.player2_name == 'BYE':
                return 'BYE', match.player1_name
        
        return None, None

    @staticmethod
    def _set_bye_match_winner(match, actual_player):
        """set the winner of the bye match"""
        if match.event_type in ['MD', 'WD', 'XD']:
            # doubles match
            names = actual_player.split(' / ')
            if len(names) == 2:
                match.winner_name = actual_player
                match.status = 'Finished'
                # here we can set winner1_id and winner2_id if needed
        else:
            # singles match
            match.winner_name = actual_player
            match.status = 'Finished'
            # here we can set winner1_id if needed

    @staticmethod
    def _update_next_match_after_bye(match, actual_player):
        """update the next match after the bye match"""
        if not match.next_match_id:
            return
        
        next_match = Match.query.get(match.next_match_id)
        if not next_match:
            return
        
        # print(f"Updating next match {next_match.id} after BYE")
        
        # determine which position the bye match corresponds to in next_match
        if next_match.prev_match1_id == match.id:
            # update player1 position
            if next_match.event_type in ['MD', 'WD', 'XD']:
                names = actual_player.split(' / ')
                if len(names) == 2:
                    next_match.team1_player1_name = names[0].strip()
                    next_match.team1_player2_name = names[1].strip()
            else:
                next_match.player1_name = actual_player
        elif next_match.prev_match2_id == match.id:
            # update player2 position
            if next_match.event_type in ['MD', 'WD', 'XD']:
                names = actual_player.split(' / ')
                if len(names) == 2:
                    next_match.team2_player1_name = names[0].strip()
                    next_match.team2_player2_name = names[1].strip()
            else:
                next_match.player2_name = actual_player

    @staticmethod
    def query_players_history(player_name, tournament_id):
        """查詢選手的比賽歷史"""
        try:
            # 查詢該選手在指定 tournament 中的所有比賽
            matches = Match.query.filter(
                Match.tournament_id == tournament_id,
                db.or_(
                    # 單打比賽
                    Match.player1_name == player_name,
                    Match.player2_name == player_name,
                    # 雙打比賽
                    Match.team1_player1_name == player_name,
                    Match.team1_player2_name == player_name,
                    Match.team2_player1_name == player_name,
                    Match.team2_player2_name == player_name
                )
            ).all()

            # 使用 get_match_data 獲取完整的 match 資料
            match_history = [get_match_data(match) for match in matches]
            
            # 計算統計資料
            total_matches = len(match_history)
            completed_matches = len([m for m in match_history if m['status'] == 'Finished'])
            wins = len([m for m in match_history if m.get('winner') and player_name in m.get('winner', '')])
            losses = completed_matches - wins
            win_rate = (wins / completed_matches * 100) if completed_matches > 0 else 0
            
            return {
                'status': 'success',
                'message': f'Found {total_matches} matches for player {player_name}',
                'data': {
                    'player_name': player_name,
                    'tournament_id': tournament_id,
                    'statistics': {
                        'total_matches': total_matches,
                        'completed_matches': completed_matches,
                        'wins': wins,
                        'losses': losses,
                        'win_rate': round(win_rate, 1)
                    },
                    'match_history': match_history  # 現在是完整的 get_match_data 格式
                }
            }
            
        except Exception as e:
            # print(f"Error querying players history: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    @staticmethod
    def export_tournament_results_to_excel(tournament_id):
        """導出比賽結果到 Excel - 使用與 schedule 相同的方式
        
        Args:
            tournament_id: 比賽ID
        
        Returns:
            str: 生成的文件路徑
        """
        try:
            import pandas as pd
            import os
            from flask import current_app
            
            # 獲取比賽數據
            matches = Match.query.filter_by(tournament_id=tournament_id).all()
            
            if not matches:
                raise ValueError("No matches found for this tournament")
            
            print(f"Found {len(matches)} matches for tournament {tournament_id}")
            
            # 準備數據行
            rows = []
            
            # 獲取比賽信息
            tournament = Tournament.query.get(tournament_id)
            
            for match in matches:
                try:
                    # 獲取 Event 和 Group 信息
                    event = Event.query.get(match.event_id) if match.event_id else None
                    group = Group.query.get(match.group_id) if match.group_id else None
                    
                    # 處理玩家名稱
                    if match.event_type in ['MD', 'WD', 'XD']:
                        # 雙打
                        player1_name = f"{match.team1_player1_name or 'TBD'} / {match.team1_player2_name or 'TBD'}"
                        player2_name = f"{match.team2_player1_name or 'TBD'} / {match.team2_player2_name or 'TBD'}"
                        match_type = "Double"
                    else:
                        # 單打
                        player1_name = str(match.player1_name or 'TBD')
                        player2_name = str(match.player2_name or 'TBD')
                        match_type = "Single"
                    
                    # 處理分數 - 顯示每一局的具體分數
                    game_scores = []
                    
                    # Game 1
                    if match.game1_score1 > 0 or match.game1_score2 > 0:
                        game_scores.append(f"{match.game1_score1}-{match.game1_score2}")
                    
                    # Game 2
                    if match.game2_score1 > 0 or match.game2_score2 > 0:
                        game_scores.append(f"{match.game2_score1}-{match.game2_score2}")
                    
                    # Game 3
                    if match.game3_score1 > 0 or match.game3_score2 > 0:
                        game_scores.append(f"{match.game3_score1}-{match.game3_score2}")
                    
                    # 如果沒有分數，顯示 "No Score"
                    if not game_scores:
                        score = "No Score"
                    else:
                        score = ", ".join(game_scores)
                    
                    # 處理勝者
                    winner = str(match.winner_name or 'TBD')
                    
                    # 創建數據行 - 確保所有值都是字符串
                    row_data = {
                        'Event': str(event.name if event else match.event_type or 'N/A'),
                        'Group': str(group.name if group else 'N/A'),
                        'Player/Team 1': str(player1_name),
                        'Player/Team 2': str(player2_name),
                        'Match Type': str(match_type),
                        'Score': str(score),
                        'Winner': str(winner),
                        'Status': str(match.status or 'Scheduled'),
                        'Round': str(match.round or 'N/A'),
                        'Match Number': str(match.match_number or 'N/A')
                    }
                    
                    rows.append(row_data)
                    
                except Exception as e:
                    print(f"Error processing match {match.id}: {e}")
                    continue
            
            print(f"Processed {len(rows)} matches successfully")
            
            # 如果沒有數據，創建一個基本的行
            if not rows:
                rows.append({
                    'Event': 'No Data',
                    'Group': 'Available',
                    'Player/Team 1': 'Please',
                    'Player/Team 2': 'Check',
                    'Match Type': 'Database',
                    'Score': 'For',
                    'Winner': 'Matches',
                    'Status': 'In',
                    'Round': 'This',
                    'Match Number': 'Tournament'
                })
            
            # 創建輸出檔案路徑 - 使用絕對路徑
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            instance_path = os.path.join(base_dir, 'instance')
            
            print(f"Base directory: {base_dir}")
            print(f"Instance path: {instance_path}")
            
            # 檢查 instance_path 是否存在
            if not os.path.exists(instance_path):
                print(f"Creating instance directory: {instance_path}")
                os.makedirs(instance_path, exist_ok=True)
            else:
                print(f"Instance directory exists: {instance_path}")
            
            # 檢查目錄權限
            if os.access(instance_path, os.W_OK):
                print(f"Directory is writable: {instance_path}")
            else:
                print(f"Directory is NOT writable: {instance_path}")
                raise Exception(f"Cannot write to directory: {instance_path}")
            
            output_filename = f"tournament_{tournament_id}_results.xlsx"
            output_path = os.path.join(instance_path, output_filename)
            
            print(f"Full output path: {output_path}")
            print(f"Absolute output path: {os.path.abspath(output_path)}")
            
            # 使用 pandas 創建 DataFrame 並寫入 Excel
            df = pd.DataFrame(rows)
            print(f"DataFrame shape: {df.shape}")
            print(f"DataFrame columns: {df.columns.tolist()}")
            
            # 確保所有數據都是字符串類型
            for col in df.columns:
                df[col] = df[col].astype(str)
            
            print("Attempting to write Excel file...")
            
            # 寫入 Excel 文件 - 使用更明確的參數
            with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, sheet_name='Tournament Results', index=False)
            
            print("Excel file written successfully")
            
            # 檢查文件是否存在
            if not os.path.exists(output_path):
                raise Exception("Failed to create Excel file")
            
            file_size = os.path.getsize(output_path)
            print(f"Excel file created: {output_path}")
            print(f"File size: {file_size} bytes")
            print(f"File permissions: {oct(os.stat(output_path).st_mode)}")
            
            if file_size == 0:
                raise Exception("Generated Excel file is empty")
            
            # 驗證文件是否可讀
            try:
                test_df = pd.read_excel(output_path, sheet_name='Tournament Results')
                print(f"File verification successful, read {len(test_df)} rows")
            except Exception as e:
                print(f"File verification failed: {e}")
                raise Exception(f"Generated file is corrupted: {e}")
            
            return output_path
            
        except Exception as e:
            print(f"Error in export_tournament_results_to_excel: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error exporting tournament results: {str(e)}")

    @staticmethod
    def remove_all_registrations(tournament_id):
        """remove all the registrations of the tournament"""
        try:
            registrations = Registration.query.filter_by(tournament_id=tournament_id).all()
            for registration in registrations:
                db.session.delete(registration)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False