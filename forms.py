from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm):
    name = StringField("Name", [DataRequired("Please enter your name.")])
    email = StringField("Email", [DataRequired("Please enter your email address."), Email("Please enter a valid email address.")])
    subject = StringField("Subject", [DataRequired("Please enter a subject.")])
    message = TextAreaField("Message", [DataRequired("Please enter a message.")])
    submit = SubmitField("Send")
