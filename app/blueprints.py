from flask import Blueprint

home_blueprint = Blueprint('home_blueprint', __name__, template_folder='templates')
scoreboard_blueprint = Blueprint('scoreboard_blueprint', __name__, template_folder='templates')
umpire_blueprint = Blueprint('umpire_blueprint', __name__, template_folder='templates')