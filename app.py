from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

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
    
    if request.method == 'POST':
        name = request.form['inputName']
        email = request.form['inputEmail']
        phone = request.form['inputPhone']
        username = request.form['inputUsername']
        password = request.form['inputPassword']

        if name is "" or email is "" or phone is "" or username is "" or password is "":
            return render_template('signup.html', message='All fields are required!')

        try:
            user = User(username, email, phone, name, password)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return render_template('signup.html', message='Already signed up!')
            
        return redirect(url_for('home'))

    
    return render_template('signup.html')

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

if __name__ == '__main__':
    port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)
