from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, ValidationError


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity.'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short.'),
        ProfanityFree()])
    article_id = HiddenField("Article id")
    submit = SubmitField('Submit')


