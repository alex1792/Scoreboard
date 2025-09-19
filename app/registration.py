import re
from flask import jsonify, Blueprint
from .models import db, Registration, User
from .utils import check_authorization
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from datetime import datetime
from .utils import get_user_by_name, check_repeated_registration
from .services.registration_service import RegistrationService

registration_bp = Blueprint('registration', __name__, url_prefix='/api/registrations')

"""
This function is used to sign up a tournament. It will create a new registration record in the database.
For each event and group, it will create a registration record.

For example, if a user signed up for MS-A, MD-A, then there will be 2 registration records in the database.
"""
@registration_bp.route('/tournaments/<int:tournament_id>/registrations', methods=['POST'])
@jwt_required()
def sign_up_tournament(tournament_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"status": "error", "message": "Please Login to sign up a tournament"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": "Please Login to sign up a tournament"}), 500
    
    try:
        sign_up_data = request.get_json()
        if not sign_up_data:
            return jsonify({"status": "error", "message": "Player not found, please enter your name correctly"}), 400

        player_info = sign_up_data.get('player_info')
        registrations_info = sign_up_data.get('registrations')

        created_registrations = RegistrationService.create_registration(
            tournament_id, player_info, registrations_info
        )

        return jsonify({"status": "success", "message": "Tournament sign up successful"}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to sign up tournament'}), 500


"""
This funciton is used to get all the registrations of a tournament. It will return all the registraion info
to the frontend. Then, the frontend will show all the sign-up records in the /tournament/<int:tournament_id>/registrations page.

For each event and group, it will return  the registration info.
For example, if a user signed up for MS-A, MD-A, then there will be 2 registration records returned,
which is MS-A and MD-A respectively.
"""
@registration_bp.route('/tournament/<int:tournament_id>/registrations', methods=['GET'])
@jwt_required()
def get_registrations(tournament_id):
    # print(f"Getting registrations for tournament {tournament_id}")
    try:
        auth = check_authorization('host')
        if auth:
            return auth

        registrations = RegistrationService.get_registrations_by_tournament(tournament_id)
        # print(f"Registrations: {registrations}")
        if not registrations:
            return jsonify({"status": "error", "message": "No registrations found"}), 404
        

        registrations_data = []
        for registration in registrations:
            registration_data = {
                'id': registration.get('id'),
                'user_name': registration.get('user_name'),
                'partner_name': registration.get('partner_name') if registration.get('partner_name') != 'nan nan' else None,
                'event_name': registration.get('event_name'),
                'group_name': registration.get('group_name'),
                'status': registration.get('status'),
                'registration_date': registration.get('registration_date')
            }
            registrations_data.append(registration_data)

        return jsonify({
            "status": "success", 
            "message": "Registrations fetched successfully", 
            "data": registrations_data
        }), 200
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get registrations"}), 500


@registration_bp.route('/tournament/<int:tournament_id>/upload', methods=['POST'])
@jwt_required()
def upload_registration_file(tournament_id):
    # print(f"Uploading registration file for tournament {tournament_id}")
    try:
        file = request.files['file']
        if not file:
            return jsonify({"status": "error", "message": "No file uploaded"}), 400
        
        registration_result = RegistrationService.create_registration_from_excel(tournament_id, file)
        # print(f"Registration result: {registration_result}")
        return jsonify({"status": "success", "message": registration_result}), 200
            
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to upload registration file"}), 500


@registration_bp.route('/<int:registration_id>/status', methods=['PUT'])
@jwt_required()
def update_registration_status(registration_id):
    """Update registration.status (pending, confirmed, cancelled)"""
    try:
        auth = check_authorization('host')
        if auth:
            return auth
        
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        new_status = data.get('status')

        if not new_status in ['pending', 'confirmed', 'cancelled']:
            return jsonify({"status": "error", "message": "Invalid status"}), 400
        
        registration = RegistrationService.update_registration_status(registration_id, new_status)
        if not registration:
            return jsonify({"status": "error", "message": "Registration not found"}), 404
        return jsonify({"status": "success", "message": "Registration status updated successfully"}), 200

    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to update registration status"}), 500

