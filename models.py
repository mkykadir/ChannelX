from app import db
from sqlalchemy.orm import relationship
import hashlib
import random
import datetime

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
    toWho = db.Column(db.String(30), db.ForeignKey('channels.channelname'), unique=True, nullable=False)
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

    channelName = db.Column(db.Text, db.ForeignKey('channels.channelname'), primary_key=True)
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
    
        

    


    
    
    
    
        
    
