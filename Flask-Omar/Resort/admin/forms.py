from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import  FloatField, IntegerField, SelectField, StringField, PasswordField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import InputRequired, Email, EqualTo, Length, DataRequired, Regexp,Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired, MultipleFileField

from Resort import db ,ALLOWED_EXTENSIONS



class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('guest','Guest'),('admin','Admin')], validators=[DataRequired()])
    submit = SubmitField('Save')

class RoomTypeForm(FlaskForm):
    name           = StringField('Name', validators=[DataRequired(), Length(max=50)])
    description    = TextAreaField('Description', validators=[Optional()])
    base_price     = FloatField('Base Price', validators=[DataRequired(), NumberRange(min=0)])
    max_guests     = IntegerField('Max Guests', validators=[DataRequired(), NumberRange(min=1)])
    # ←— file‐upload fields:
    main_image     = FileField(
        'Main Image',
        validators=[
            FileRequired(),
            FileAllowed(ALLOWED_EXTENSIONS, 'Only images!')
        ]
    )
    gallery_images = MultipleFileField(
        'Gallery Images',
        validators=[FileAllowed(ALLOWED_EXTENSIONS, 'Only images!')]
    )
    features       = StringField('Features (comma-separated)', validators=[Optional()])
    is_luxury      = BooleanField('Luxury?')
    luxury_label   = StringField('Luxury Label', validators=[Optional(), Length(max=50)])
    submit         = SubmitField('Save')

class ExtraServiceForm(FlaskForm):
    name        = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    price       = FloatField('Price', validators=[DataRequired()])
    type        = SelectField('Type', choices=[
                      ('dining','Dining'),
                      ('service','Service'),
                      ('bed','Bed')
                   ], validators=[DataRequired()])
    per_adult   = BooleanField('Charge per adult?')    # ← NEW
    submit      = SubmitField('Save')

class GuestOptionForm(FlaskForm):
    adult_count = IntegerField('Number of Adults', validators=[
        DataRequired(), NumberRange(min=1)
    ])
    
    child_count = IntegerField('Number of Children', validators=[
        Optional(), NumberRange(min=0)
    ])
    
    label = StringField('Label', validators=[
        DataRequired(), Length(max=50)
    ])
    
    submit = SubmitField('Save')
class RoomForm(FlaskForm):
    room_number   = StringField('Room Number', validators=[DataRequired(), Length(max=10)])
    floor         = IntegerField('Floor',       validators=[DataRequired()])
    room_type_id  = SelectField('Room Type', coerce=int, validators=[DataRequired()])
    is_available  = BooleanField('Available', default=True)
    notes         = TextAreaField('Notes',      validators=[Optional(), Length(max=200)])
    submit        = SubmitField('Save')
