from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from forms import SignUpForm
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import argparse
import petname
from random import randint
app = Flask(__name__)
# app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['CHANNELX_SQL_SERVER']
mailpassword = os.environ['CHANNELX_MAIL_PASS'] # ask for password
app.secret_key = 'UntitledGroup'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
db.create_all() # create new models automatically

from models import User, Channel

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

@login_manager.unauthorized_handler
def unauthorized():
    flash("You should be logged in!", "warning")
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('panel'))
    
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('panel'))

    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['inputUsername']
        password = request.form['inputPassword']
        rememberme = request.form.get('rememberMe')

        if username is "" or password is "":
            flash("Please fill credentials", "warning")
            return redirect(url_for('login'))
            
        try:
            queryUser = User.query.filter_by(username=username).first()
            newhash = queryUser.createHash(queryUser.salt, password)
            if newhash == queryUser.hashed and queryUser.email_verified is True:
                login_user(queryUser, remember=rememberme)
                return redirect(url_for('panel'))
            else:
                flash("Wrong credentials or non-verified E-Mail address", "danger")
                return redirect(url_for('login'))
        except AttributeError:
            return redirect(url_for('login'))
        

@app.route('/verify', methods=['GET'])
def verify():
    if 'username' in session:
        return redirect(url_for('panel'))

    username = request.args.get('username')
    if not username:
        return redirect(url_for('home'))
    
    user = User.query.filter_by(username=username).first()

    if user:
        if user.email_verified is False:
            user.email_verified = True
            db.session.commit()
            flash("Your E-Mail verified, you can log-in now!", "success")
        else:
            flash("Your E-Mail is already verified, you can log in!", "info")
    else:
        flash("Non-registered user!", "danger")

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

            mailaddress = form.email.data
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login("untitledchannelx", mailpassword)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "ChannelX: Account Verification"
            msg['From'] = "untitledchannelx@gmail.com"
            msg['To'] = mailaddress
            html = """\
                <html>
                  <head></head>
                  <body>
                    <h1>ChannelX</h1>
                    <p>Welcome our family! Please <a href="http://localhost:5000/verify?username=""" + form.username.data + """\
                      ">verify</a> your account.
                    </p>
                  </body>
                </html>
                """
            msg.attach(MIMEText(html, 'html'))
            
            server.sendmail("untitledchannelx@gmail.com", mailaddress, msg.as_string())
            server.close()
        except IntegrityError:
            flash('Already signed up user!', 'warning')
            return render_template('signup.html', form=form)

        flash("Thanks for registering, we've sent email for validation", 'info')
        return redirect(url_for('login'))

    
    return render_template('signup.html', form=form)


@app.route('/logout', methods=['GET'])
@login_required
def logout():   
    logout_user()
    return redirect(url_for('home'))

@app.route('/panel', methods=['GET'])
@login_required
def panel():
    channels = db.session.query(Channel.name).order_by(Channel.creation_date).filter(Channel.creator==current_user.get_id())
    return render_template('panel.html', username=current_user.get_id(), channels=channels)

@app.route('/channelc', methods=['POST'])
@login_required
def create_channel():
    word_count = randint(1,4)
    generated_name = petname.Generate(int(word_count))
    content = request.form['inputDescription']
    creator = current_user.get_id()
    # ismin olup olmadigini kontrol et!
    while db.session.query(Channel.name).filter(Channel.name==generated_name).count() is not 0:
        word_count = randint(1,4)
        generated_name = petname.Generate(int(word_count))
    
    channel = Channel(generated_name, creator, content)
    db.session.add(channel)
    db.session.commit()
    return redirect(url_for('home'))
        

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    user = User.query.filter_by(username=current_user.get_id()).first()
    if not user:
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('profile.html', user=user)
        
    

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
    server.login("untitledchannelx", mailpassword) # ask for password

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
