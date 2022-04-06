from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length


class NewLocationForm(FlaskForm):
    lookup_address = StringField('', render_kw={"placeholder": "Search address"})

    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])

    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])                    

    submit = SubmitField('Search')

class NewPharmacyForm(FlaskForm):
    name = StringField('Name')

    price = StringField('Price') 

    address = StringField('Address')

    imageurl = StringField('Image Url') 

    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])

    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])                    

    submit = SubmitField('Create')