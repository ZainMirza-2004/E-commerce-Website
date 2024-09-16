from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError


class OpinionForm(FlaskForm):
    opinion = StringField('Quantity: ', validators=[DataRequired(), Length(min=0, max=100)])
    submit = SubmitField('Add to basket')

class PaymentForm(FlaskForm):
    card_number = StringField('Card Number', validators=[DataRequired(), Regexp(r'^(\d{4}[-\s]?){3}\d{4}$', message='Invalid card number')])
    expiry_date = StringField('Expiry Date (MM/YYYY)', validators=[DataRequired(), Length(min=7, max=7, message='Invalid expiry date format')])
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=4, message='Invalid CVV')])
    
    # Address fields
    street_address = StringField('Street Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])

    submit = SubmitField('Submit Payment')
    
def gmail_check(form, field):
    if '@gmail.com' not in field.data:
        raise ValidationError('Invalid Email Address.')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), gmail_check])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), gmail_check])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    submit = SubmitField('Login')