from better_profanity import profanity
from flask_wtf import FlaskForm
from password_validator import PasswordValidator
from wtforms import TextAreaField, HiddenField, SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity.'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class PasswordValid:
    def __init__(self, message=None):
        if not message:
            message = u'Password must at least 8 characters, and contain an upper case letter, a lower case letter and a digit.'
        self.message = message

    def __call__(self, form, field):
        schema = PasswordValidator()
        schema \
            .min(8) \
            .has().uppercase() \
            .has().lowercase() \
            .has().digits()
        if not schema.validate(field.data):
            raise ValidationError(self.message)


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short.'),
        ProfanityFree()])
    article_id = HiddenField("Article id")
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        DataRequired(),
        Length(min=3, message='Your username is too short.')])
    password = PasswordField('Password', [
        DataRequired(),
        PasswordValid()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', [
        DataRequired()])
    password = PasswordField('Password', [
        DataRequired()])
    submit = SubmitField('Login')


