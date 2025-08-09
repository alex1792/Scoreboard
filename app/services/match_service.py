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

        # update the status of the match
        match.status = new_status
        
        # if the status is Finished, determine the winner
        if new_status == 'Finished':
            try:
                winner_info = MatchService.determine_winner(match_id)
                print(f"Winner determined: {winner_info}")  # add debug info
            except ValueError as e:
                raise ValueError(f"Cannot finish match: {str(e)}")
        
        db.session.commit()
        return get_match_data(match)

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
        # match.current_game += 1
        
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
        elif match.player1_score == 0 and match.player2_score == 0:
            pass
        else:
            return ValueError("Game is a draw")
        
        # set match.status to finished
        match.status = 'Finished'

        # determine the winner
        MatchService.determine_winner(match_id)

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