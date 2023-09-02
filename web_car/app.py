#!/usr/bin/python3
"""
flask model

"""
from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import storage
from models.user import User
from models.vehicle import Vehicle
from models.rental import Rental
app = Flask(__name__)
import secrets
import re
storage.all()

app.secret_key = secrets.token_hex(16)

@app.teardown_appcontext
def teardown_data(self):
    """
        refrech data
    """
    storage.close()

def is_user_authenticated():
    return session.get('user_authenticated', False)

@app.context_processor
def inject_is_user_authenticated():
    return dict(is_user_authenticated=is_user_authenticated)

@app.route('/', strict_slashes=False)
def index():
    """
        template path
    """

    vehicles = storage.all(Vehicle).values()
    print(vehicles)
    return render_template('index.html', vehicles=vehicles)

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    # Your code here

    msg = ''
    
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        phone_no = request.form['phone_no']
        
        users = storage.all(User).values()
        
        # Check if the email already exists in the database
        if any(user.email == email for user in users):
            msg = "Account already exists!"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', firstname):
            msg = 'Firstname must contain only characters and numbers !'
        elif not re.match(r'[A-Za-z0-9]+', lastname):
            msg = 'Lastname must contain only characters and numbers !'
        elif not firstname or not lastname or not password or not email or not phone_no:
            msg = 'Please fill out the form !'
        else:
            user = User(first_name=firstname, last_name=lastname, email=email, password=password, phone_no=phone_no)
            user.save()
            msg = "Account created successfully!"

        flash(msg)
    
    return render_template('signup.html')

@app.route('/signin', methods=('POST', 'GET'))
def signin():
    # Your sign-in logic here
    email = request.form['email']
    password = request.form['password']
    users = storage.all(User).values()
    vehicles = storage.all(Vehicle).values()

    for user in users:
        if user.email == email and user.password == password:
            session['user_authenticated'] = True
            return render_template('index.html', vehicles=vehicles)
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Your logout logic here
    # For example, clear the user session

    session['user_authenticated'] = False
    vehicles = storage.all(Vehicle).values()
    return render_template('index.html', vehicles=vehicles)

@app.route('/booking')
def booking():
    if is_user_authenticated():
        vehicles = storage.all(Vehicle).values()
        return render_template('booking.html', vehicles=vehicles)
    else:
        return render_template('signup.html')
    



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


