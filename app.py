from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_, not_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from forms import SignUpForm
import os
import smtplib
import hashlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import argparse
import petname
import random
from random import randint
import datetime
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
    membership = db.session.query(Member.channelName).filter(Member.memberName==current_user.get_id())
    return render_template('panel.html', username=current_user.get_id(), channels=channels, membership=membership)

@app.route('/search', methods=['POST'])
@login_required
def search():
    if request.method == 'POST':
        req = request.form.get('req', None)
        print(req)
        membership = db.session.query(Member.channelName).filter(Member.memberName==current_user.get_id()).all()
        print(membership)
        channels = db.session.query(Channel).order_by(Channel.name).filter(and_(Channel.name.like("%" + req + "%"), Channel.creator!=current_user.get_id(), not_(Channel.name.in_(membership))))
        print(channels)
        return render_template('search.html', search=req, channels=channels)
    
@app.route('/_channeli', methods=['GET'])
@login_required
def channel_info_json():
    channel_name = request.args.get('chname')
    queryChannel = Channel.query.filter_by(name=channel_name).first()

    if queryChannel:
        protected = False
        if queryChannel.hashed is not None:
            protected = True

        startdate = None
        if queryChannel.start is not None:
            startdate = queryChannel.start.strftime('%Y-%m-%d')

        enddate = None
        if queryChannel.end is not None:
            enddate = queryChannel.end.strftime('%Y-%m-%d')
            
        result = {'chname': queryChannel.name, 'chcreatedate': queryChannel.creation_date.strftime('%Y-%m-%d'),'chdescription': queryChannel.description, 'chstart': startdate, 'chend': enddate, 'chlimit': queryChannel.member_limit, 'chprotected': protected}
        print(result)
        return jsonify(result)
    else:
        return redirect(url_for('panel'))

@app.route('/_channeld', methods=['GET'])
@login_required
def channel_remove_json():
    channel_name = request.args.get('chname')
    try:
        Channel.query.filter_by(name=channel_name, creator=current_user.get_id()).delete()
        db.session.commit()
        result = {'result': 200}
    except:
        result = {'result': 404}

    return jsonify(result)

@app.route('/channelc', methods=['POST'])
@login_required
def create_channel():
    word_count = randint(1,4)
    generated_name = petname.Generate(int(word_count))
    content = request.form['inputCreateDescription']
    creator = current_user.get_id()
    # ismin olup olmadigini kontrol et!
    while db.session.query(Channel.name).filter(Channel.name==generated_name).count() is not 0:
        word_count = randint(1,4)
        generated_name = petname.Generate(int(word_count))
    
    channel = Channel(generated_name, creator, content)
    db.session.add(channel)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/channel/<chname>/<memname>', methods=['GET'])
@login_required
def kick_user(chname, memname):
    queryChannel = Channel.query.filter_by(name=chname, creator=current_user.get_id()).first()
    if queryChannel is None:
        # FLASH not admin of channel
        if current_user.get_id() == memname:
            isMember = Member.query.filter_by(channelName=chname, memberName=memname).first()
            if isMember is None:
                return redirect(url_for('panel'))
            Member.query.filter_by(channelName=chname, memberName=memname).delete()
            db.session.commit()
            return redirect(url_for('panel'))

    try:
        Member.query.filter_by(channelName=chname, memberName=memname).delete()
        db.session.commit()
    except:
        # FLASH non member of channel
        return redirect(url_for('panel'))

    return redirect(url_for('channel_entry', chname=chname))

@app.route('/channel/<chname>', methods=['POST', 'GET'])
@login_required
def channel_entry(chname):
    print(chname)
    if request.method == 'GET':
        queryChannel = Channel.query.filter_by(name=chname, creator=current_user.get_id()).first()
        if queryChannel is not None:
            # user is creator of the channel show the member list
            members = Member.query.filter_by(channelName=chname)
            return render_template('channel.html', name=chname, members=members)
        else:
            # user is not creator of channel
            isMember = Member.query.filter_by(channelName=chname, memberName=current_user.get_id()).first()
            queryChannel = Channel.query.filter_by(name=chname).first()
            if isMember is not None:
                # FLASH user already member of channel
                return render_template('channel.html', name=chname, alreadymember=True, membership=isMember, description=queryChannel.description)
                
            
            if queryChannel is None:
                # FLASH channel not exists
                return redirect(url_for('panel'))

            if queryChannel.start is not None:
                currentDate = datetime.datetime.now().date()
                if queryChannel.start > currentDate or queryChannel.end < currentDate:
                    # FLASH channel deadline
                    return redirect(url_for('panel'))

            if queryChannel.member_limit is not None:
                member_count = db.session.query(Member).filter_by(channelName=queryChannel.name).count()
                #member_count = Member.query(Member.memberName).filter_by(channelName=queryChannel.name).count()
                if member_count == queryChannel.member_limit:
                    #FLASH too many users
                    return redirect(url_for('panel'))

            passrequired = False
            if queryChannel.hashed is not None:
                passrequired = True
                        
            return render_template('channel.html', name=chname, passrequired=passrequired, description=queryChannel.description)

    if request.method == 'POST':
        print("in post method")
        queryChannel = Channel.query.filter_by(name=chname, creator=current_user.get_id()).first()
        if queryChannel is not None:
            print("creator of channel")
            return redirect(url_for('panel'))
        else:
            print("not creator")
            isMember = Member.query.filter_by(channelName=chname, memberName=current_user.get_id()).first()
            if isMember is not None:
                print("already member")
                # FLASH user already member of channel
                isMember.prefersEmail = request.form.get('inputPreferEmail', False)
                isMember.prefersPhone = request.form.get('inputPreferSms', False)
                db.session.commit()
                return redirect(url_for('channel_entry', chname=chname))
            else:
                print("not member")
                queryChannel = Channel.query.filter_by(name=chname).first()
                if queryChannel is None:
                    # FLASH channel not exists
                    print("channel not exists")
                    return redirect(url_for('panel'))

                passwordGet = request.form.get('inputPassword', None)
                preferEmail = request.form.get('inputPreferEmail', False)
                preferSms = request.form.get('inputPreferSms', False)

                if preferEmail is False and preferSms is False:
                    print("select at least one")
                    # FLASH user should pick at least one
                    return redirect(url_for('channel_entry', chname=chname))
                
                if queryChannel.hashed is not None and passwordGet is None:
                    # FLASH password required
                    print("pass required")
                    return redirect(url_for('channel_entry', chname=chname))
                currentDate = datetime.datetime.now().date()
                if queryChannel.start is not None:
                    
                    if queryChannel.start > currentDate or queryChannel.end < currentDate:
                        # FLASH channel deadline
                        print("deadline")
                        return redirect(url_for('panel'))

                
                if queryChannel.member_limit is not None:
                    member_count = db.session.query(Member).filter_by(channelName=queryChannel.name).count()
                    # member_count = Member.query(Member.memberName).filter_by(channelName=queryChannel.name).count()
                    if member_count == queryChannel.member_limit:
                        #FLASH too many users
                        return redirect(url_for('panel'))

                if queryChannel.hashed is None:
                    print("No need for pass")
                    # no need for password
                    member = Member(chname, current_user.get_id(), currentDate, preferEmail, preferSms)
                    db.session.add(member)
                    db.session.commit()
                else:
                    print("need for pass")
                    newhash = queryChannel.createHash(queryChannel.salt, passwordGet)
                    if newhash == queryChannel.hashed:
                        print("correct pass")
                        member = Member(chname, current_user.get_id(), currentDate, preferEmail, preferSms)
                        db.session.add(member)
                        db.session.commit()
                    else:
                        print("wrong pass")
                        # FLASH wrong password
                        return redirect(url_for('channel_entry', chname=chname))
                return redirect(url_for('panel'))
    return render_template('channel.html', name=chname)

@app.route('/channelu', methods=['POST'])
@login_required
def update_channel():
    chname = request.form['channelName']
    channel = Channel.query.filter_by(name=chname, creator=current_user.get_id()).first()

    if channel is None:
        return redirect(url_for('panel'))

    if request.form.get('descriptioncheck', False):
        channel.description = request.form.get('inputDescription', channel.description)

    if request.form.get('passwordcheck', False):
        channel.setPassword(request.form.get('inputPassword', None))
    else:
        channel.hashed = None
        channel.salt = None

    
    if request.form.get('timecheck', False):
        channel.start = request.form.get('inputStartDate', None)
        channel.end = request.form.get('inputEndDate', None)
    else:
        channel.start = None
        channel.end = None

    if request.form.get('limitcheck', False):
        channel.member_limit = request.form.get('inputLimit', None)
    else:
        channel.member_limit = None
            

    db.session.commit()

    return redirect(url_for('panel'))
        

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

	user = User.query.filter_by(username=current_user.get_id()).first()
	if not user:
		return redirect(url_for('home'))
        
	if request.method == 'GET':
		return render_template('profile.html', user=user)
        
@app.route('/profileu', methods=['POST'])
@login_required
def update_profile():   
	user = User.query.filter_by(username=current_user.get_id()).first()
	if not user:
		return redirect(url_for('home'))
	
	user.name = request.form.get('inputName', user.name)
	
	userPassword = request.form.get('inputPassword', None)
	
	confirmPassword = request.form.get('inputConfirm', None)
	
	if userPassword == confirmPassword and userPassword != "":
		user.setPassword(userPassword)
	else:
		print("no pass given or passwords don't match")
		
	db.session.commit() 
	return redirect(url_for('login'))    

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


class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    hashed = db.Column(db.Text, nullable=False)
    salt = db.Column(db.Text, nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, email, phone, name, password):
        self.username = username
        self.email = email
        self.phone = phone
        self.name = name
        self.salt = self.createSalt()
        self.hashed = self.createHash(self.salt, password)

    def createSalt(self):
        ABECE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars = []
        for i in range(16):
            chars.append(random.choice(ABECE))
        
        real_salt = "".join(chars)
        return real_salt

    def createHash(self, salt, password):
        salted_password = password.join(salt)
        h = hashlib.md5(salted_password.encode())
        return h.hexdigest()

    def is_authenticated(self):
        return True

    
    def is_active(self):
        if self.email_verified:
            print("True")
        else:
            print("False")
            
        return self.email_verified

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username
    
    def setPassword(self, password):
        if password is not None:
            self.salt = self.createSalt()
            self.hashed = self.createHash(self.salt, password)

class Channel(db.Model):    
    __tablename__ = 'channels'
    # TODO: Add setter and getter to other columns
    name = db.Column(db.Text, nullable = False, primary_key=True)
    creator = db.Column(db.String(100), db.ForeignKey('users.username'), nullable = False)
    description = db.Column(db.String(200),nullable = False)
    start = db.Column(db.Date, nullable = True)
    end = db.Column(db.Date, nullable = True)
    creation_date = db.Column(db.Date, nullable = False)
    member_limit = db.Column(db.Integer, nullable = True)
    hashed = db.Column(db.Text, nullable=True)
    salt = db.Column(db.Text, nullable=True)
    # password = db.Column(db.Text, nullable = True)

    def __init__(self, name, creator, description):
        self.name = name
        self.creator = creator
        self.description = description
        self.creation_date = datetime.datetime.now()

    def setPassword(self, password):
        if password is not None:
            self.salt = self.createSalt()
            self.hashed = self.createHash(self.salt, password)
        

    def createSalt(self):
        ABECE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars = []
        for i in range(16):
            chars.append(random.choice(ABECE))
        
        real_salt = "".join(chars)
        return real_salt

    def createHash(self, salt, password):
        salted_password = password.join(salt)
        h = hashlib.md5(salted_password.encode())
        return h.hexdigest()


class Message(db.Model):
    __tablename__ = 'messages'

    messageID = db.Column(db.String(10), primary_key=True)
    messageItself = db.Column(db.String(500), nullable=False)
    fromWho = db.Column(db.String(100), db.ForeignKey('users.username'), unique=True, nullable=False)
    toWho = db.Column(db.String(30), db.ForeignKey('channels.name'), unique=True, nullable=False)
    messageDate = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean, nullable=False)

    def __init__(self, messageID, fromWho, toWho, messageDate, sent):
        self.messageID = messageID
        self.fromWho = fromWho
        self.toWho = toWho
        self.messageDate = messageDate
        self.sent = self.sent

    def get_message(self):
        return self.messageItself

class Member(db.Model):
    __tablename__ = 'members'

    channelName = db.Column(db.Text, db.ForeignKey('channels.name'), primary_key=True)
    memberName = db.Column(db.String(100), db.ForeignKey('users.username'), primary_key=True)
    entryDate = db.Column(db.Date, nullable=False)
    prefersEmail = db.Column(db.Boolean, nullable=False)
    prefersPhone = db.Column(db.Boolean, nullable=False)
    

    def __init__(self, channelName, memberName, entryDate, prefersEmail, prefersPhone):
        self.channelName = channelName
        self.memberName = memberName
        self.entryDate = entryDate
        self.prefersEmail = prefersEmail
        self.prefersPhone = prefersPhone
    
        

    


    
    
    
    
        
    

