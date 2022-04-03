from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length


class NewLocationForm(FlaskForm):
    lookup_address = StringField('Search address')

    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])

    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])                    

    submit = SubmitField('Search')