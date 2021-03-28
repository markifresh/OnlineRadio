from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class SignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

    email = StringField('Email', validators=[Length(min=6),
                                             Email(message='Enter a valid email.'),
                                             DataRequired()])

    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=6, message='Select a stronger password.')])

    confirm = PasswordField('Confirm Your Password', validators=[DataRequired(),
                                                                 EqualTo('password', message='Passwords must match.')])

    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),
                                             Email(message='Enter a valid email.')])

    password = PasswordField('Password', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')