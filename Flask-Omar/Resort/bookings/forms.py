from flask_wtf import FlaskForm
from wtforms import  IntegerField, StringField ,SubmitField
from wtforms.validators import  Email, Length, DataRequired, Optional, NumberRange




class GuestForm(FlaskForm):
    guest_name = StringField('Guest Name', validators=[DataRequired(), Length(min=2, max=80)])
    guest_age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=100)])
    guest_email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)])
    guest_address = StringField('Address', validators=[DataRequired(), Length(min=5, max=120)])
    guest_phone = StringField('Phone Number', validators=[Optional(), Length(min=11, max=11)])
    guest_nationality = StringField('Nationality', validators=[DataRequired(), Length(min=2, max=100)])

    submit = SubmitField('Save')    