from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from forms import SignUpForm
import os
import smtplib

app = Flask(__name__)
# app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1234@localhost/channelx"
app.secret_key = 'UntitledGroup'
db = SQLAlchemy(app)

from models import User

@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        return redirect(url_for('panel'))
    
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if 'username' in session:
        return redirect(url_for('panel'))
    
    if request.method == 'POST':
        username = request.form['inputUsername']
        password = request.form['inputPassword']

        if username is "" or password is "":
            return redirect(url_for('home'))
            
        try:
            queryUser = User.query.filter_by(username=username).first()
            newhash = queryUser.createHash(queryUser.salt, password)
            if newhash == queryUser.hashed:
                session['username'] = username
                return redirect(url_for('panel'))
            else:
                return redirect(url_for('home'))
        except AttributeError:
            return redirect(url_for('home'))
        

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('panel'))

    form = SignUpForm(request.form)
    
    if request.method == 'POST' and form.validate():
        try:
            user = User(form.username.data, form.email.data, form.phone.data,
                        form.name.data, form.password.data)

            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash('Already signed up user!', 'warning')
            return render_template('signup.html', form=form)

        flash("Thanks for registering, we've sent email for validation", 'info')
        return redirect(url_for('home'))

    
    return render_template('signup.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    if 'username' not in session:
        return redirect(url_for('home'))

    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/panel', methods=['GET'])
def panel():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    return render_template('panel.html')

@app.route('/terms', methods=['GET'])
def terms():
    return render_template('terms.html')

# for email debug
@app.route('/emaildebug', methods=['POST'])
def emaildebug():
    if 'username' not in session:
        return redirect(url_for('home'))

    # START: Email send
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login("untitledchannelx", "***") # ask for password

    mailaddress = request.form['inputEmail']
    if mailaddress == "":
        return redirect(url_for('panel'))
    
    messageTo = "To: ".join(mailaddress)

    msg = "\r\n".join([
        "From: untitledchannelx@gmail.com",
        messageTo,
        "Subject: Test mail from ChannelX",
        "",
        "Welcome to ChannelX! We are Untitled Group team :)"
        ])

    server.sendmail("untitledchannelx@gmail.com", mailaddress, msg)
    server.close()
    # FINISH: Email send
    
    return redirect(url_for('panel'))

if __name__ == '__main__':
    port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)
