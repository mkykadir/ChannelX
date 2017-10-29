from wtforms import Form, BooleanField, StringField, PasswordField, validators

class SignUpForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()])
    name = StringField('Name', [validators.DataRequired()])
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.DataRequired(), validators.Email()])
    phone = StringField('Phone Number', [validators.Length(min=10, max=13), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords are not matching')
    ])
    confirm = PasswordField('Confirm Your Password')
    accept_terms = BooleanField('I accept the terms', [validators.DataRequired()])
