from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired

class ScoreForm(FlaskForm):
    score1 = IntegerField('Score 1', validators=[DataRequired()])
    score2 = IntegerField('Score 2', validators=[DataRequired()])
    submit = SubmitField('Update Scores')