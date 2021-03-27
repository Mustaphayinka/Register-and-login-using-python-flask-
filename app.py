from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pymysql

from passlib.hash import sha256_crypt
engine = create_engine("mysql+pymysql://root:password1234@localhost/register")
            # (mysql+pymysql://username:password@localhost/databasename)
db = scoped_session(sessionmaker(bind = engine))

# Instantiate flask app
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


# Register form
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        secure_password = sha256_crypt.encrypt(str(password))

        usernamedat = db.execute("SELECT username FROM users WHERE username=:username", { "username": username }).fetchone()

        if usernamedat is not None:
            used_name = request.form.get("username")
            # print(used_name)
            flash("Username {} already in use".format(used_name), "danger")
            return render_template('register.html')
        if password == confirm:
            db.execute("INSERT INTO users(name, username, password) VALUES(:name,:username,:password)",
                                            {"name":name, "username":username, "password":secure_password})
            db.commit()
            flash("You are registered and can login", "success")
            return redirect(url_for('login'))
        else:
            flash ("Password does not match","danger")
            return render_template('register.html')

    return render_template('register.html')


# Login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method =="POST":
        username = request.form.get("username")
        password = request.form.get("password")

        usernamedata = db.execute("SELECT username FROM users WHERE username=:username", { "username": username }).fetchone()
        passwordata = db.execute("SELECT password FROM users WHERE username=:username",{ "username": username}).fetchone()

        if usernamedata is None:
            current_name = request.form.get("username")
            flash("There is no such username as {}".format(current_name),"danger")
            return render_template('login.html')
        else:
            for passwor_data in passwordata:
                if sha256_crypt.verify(password, passwor_data):
                    session["log"] = True
                    flash("You are now login","success")
                    return redirect(url_for('photo'))
                else:
                    flash("incorrect passsword", "danger")
                    return render_template("login.html")
    return render_template("login.html")


# Photo
@app.route('/photo')
def photo():
    return render_template('photo.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.secret_key = "1234567password"
    app.run(debug=True)