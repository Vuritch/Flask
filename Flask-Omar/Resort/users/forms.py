from flask_wtf import FlaskForm
from wtforms import  FloatField, IntegerField, SelectField, StringField, PasswordField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import InputRequired, Email, EqualTo, Length, DataRequired, Regexp,NumberRange,Optional
from Resort.models import User



class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(3, 120)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp(r'^(?=.*[A-Z])(?=.*\d).+$',
               message='Password must contain at least one uppercase letter and one number.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



class ProfileForm(FlaskForm):
    name  = StringField('Name',  validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit_profile = SubmitField('Save Profile')



class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(),
            Regexp(
                r'(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}',
                message="Must be ≥8 chars, 1 uppercase & 1 digit"
            )
        ]
    )
    confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match')
        ]
    )
    submit_password = SubmitField('Change Password')
    






