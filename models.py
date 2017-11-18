from app import db
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
        
    '''
class Channels(db.Model):    
    __tablename__ = 'channels'

    name = db.Column(db.String(100), nullable = False, primary_key=True)
    creator = db.Column(db.String(100), nullable = False, db.ForeignKey('users.username') )
    description = db.Column(db.String(200),nullable = False)
    start = db.Column(db.DateTime, nullable = True)
    end = db.Column(db.DateTime, nullable = True)
    creation_date = db.Column(db.DateTime, nullable = False)
    member_limit = db.Column(db.Integer, nullable = True)
    password = db.Column(db.Text, nullable = True)

    def __init__(self, name, creator, description, start, end, member_limit):
        self.name = name
     #   self.creator = 