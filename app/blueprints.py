from flask import Blueprint

home_blueprint = Blueprint('home_blueprint', __name__, template_folder='templates')
scoreboard_blueprint = Blueprint('scoreboard_blueprint', __name__, template_folder='templates')
umpire_blueprint = Blueprint('umpire_blueprint', __name__, template_folder='templates')
admin_blueprint = Blueprint('admin_blueprint', __name__, template_folder='templates')
users_blueprint = Blueprint('users_blueprint', __name__, template_folder='templates')
match_blueprint = Blueprint('match_blueprint', __name__, template_folder='templates')
manage_match_blueprint = Blueprint('manage_match_blueprint', __name__, template_folder='templates')
create_match_blueprint = Blueprint('create_match_blueprint', __name__, template_folder='templates')
clear_all_match_blueprint = Blueprint('clear_all_match_blueprint', __name__, template_folder='templates')