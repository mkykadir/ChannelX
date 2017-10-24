# ChannelX
This project is created for the Software Engineering course of İstanbul Technical University. More details will be added.

# Project Members

(Please commit yourself into this file)

* 150140119 Muhammed Kadir Yücel
* 040140003 Burak Mert Gonultas
* 150140021 Utku Öner
* 150140034 Kubilay Yazoğlu

# How to Test?

Make sure you have installed

* [PostgreSQL 10](https://www.postgresql.org)
* [Python 3.x](https://www.python.org/)
* [Flask](http://flask.pocoo.org/) - pip install Flask
* [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org) - pip install Flask-SQLAlchemy
* [Psycopg2](http://initd.org/psycopg/) - pip install psycopg2

Make sure you have follow requirements before running for debug purposes

* PostgreSQL server port is 5432 (Default)
* PostgreSQL admin username is **postgres**
* PostgreSQL **channelx** named database created
* PostgreSQL admin password is **1234**

Before running project, this needs to be executed if models.py is changed, i.e. new tables added

* Open terminal or command prompt inside project folder
* Open Python program by wiritng 'python'

    from app import db
    db.create_all()
    
## Windows Systems

Open project folder in command prompt

    set FLASK_APP=app.py
    flask run

## Unix-like Systems

Linux and Max OS systems are examples of Unix-like systems. Open terminal inside project folder

    export FLASK_APP=app.py
    flask run
