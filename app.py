from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1234@localhost/channelx"
db = SQLAlchemy(app)

from models import User

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['inputUsername']
        password = request.form['inputPassword']

        queryUser = User.query.filter_by(username=username).first()
        newhash = queryUser.createHash(queryUser.salt, password)
        if newhash == queryUser.hashed:
            return redirect(url_for('panel'))
        else:
            return redirect(url_for('home'))
        
        

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['inputName']
        email = request.form['inputEmail']
        phone = request.form['inputPhone']
        username = request.form['inputUsername']
        password = request.form['inputPassword']

        user = User(username, email, phone, name, password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home'))

    
    return render_template('signup.html')

@app.route('/panel', methods=['GET'])
def panel():
    return render_template('panel.html')

if __name__ == '__main__':
    port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)
