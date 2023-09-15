#!/usr/bin/python3
"""
flask model
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash, get_flashed_messages, Response
from flask_login import login_required
from werkzeug.utils import secure_filename
from models import storage
from models.user import User
from models.vehicle import Vehicle
from models.rental import Rental
app = Flask(__name__)
import secrets
import re
import os
import base64
storage.all()

app.secret_key = secrets.token_hex(16)

app.config['UPLOAD_FOLDER'] = 'zdatabase' 
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.teardown_appcontext
def teardown_data(self):
    """
        refresh data
    """

    storage.close()

def is_user_authenticated():
    """
        Check if the user is authenticated.
    """

    return session.get('user_authenticated', False)

@app.context_processor
def inject_is_user_authenticated():
    """
    Context processor for injecting the 'is_user_authenticated' function into the template context.

    This function allows the 'is_user_authenticated' function to be available in templates for checking
    if a user is authenticated.

    Returns:
        dict: A dictionary containing the 'is_user_authenticated' function.
    """
    
    return dict(is_user_authenticated=is_user_authenticated)

@app.route('/', strict_slashes=False)
def index():
    """
        template path
    """

    vehicles = storage.all(Vehicle).values()
    return render_template('index.html', vehicles=vehicles)

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    """
        Sing Up route user can able to sign up by entering the required information
        It check if the email already exists in the database and fullfill other relevant requirements
            to create a user
    """

    msg = ''
    
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        phone_no = request.form['phone_no']
        role = 0
        
        users = storage.all(User).values()
        
        if not firstname or not lastname or not password or not email or not phone_no:
            flash("Please fill out the form !", "error")
        elif any(user.email == email for user in users):
            flash("Account already exists !", "warning")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address !", "warning")
        elif not re.match(r'[A-Za-z0-9]+', firstname):
            flash("Firstname must contain only characters and numbers !", "warning")
        elif not re.match(r'[A-Za-z0-9]+', lastname):
            flash("Lastname must contain only characters and numbers !", "warning")
        else:
            user = User(role=role, first_name=firstname, last_name=lastname, email=email, password=password, phone_no=phone_no)
            user.save()
            flash("Account created successfully!", "success")

    return render_template('signup.html')

@app.route('/signin', methods=('POST', 'GET'))
def signin():
    """
        Existing user can able to sign in by entering his own email and password
    """

    email = request.form['email']
    password = request.form['password']
    users = storage.all(User).values()
    vehicles = storage.all(Vehicle).values()

    for user in users:
        if user.email == email and user.password == password:
            session['user_authenticated'] = True
            session['user_id'] = user.id
            flash("You have successfully logged in", "success")
            if user.role == 1:
                return render_template('admin_base.html')
            else:
                return render_template('index.html', vehicles=vehicles)
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Your logout logic here
    # For example, clear the user session

    session['user_authenticated'] = False
    vehicles = storage.all(Vehicle).values()
    return render_template('index.html', vehicles=vehicles)

@app.route('/book', methods=['POST', 'GET'])
def book():
    # Your logout logic here
    # For example, clear the user session

    vehicle_types = request.form['vehicle_type']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    values = vehicle_types.split(',')
    vehicle_type = values[0]
    vehicle_brand = values[1]
    vehicle_capacity = values[2]
    vehicle_price_per_day = values[3]

    vehicles = storage.all(Vehicle).values()
    for vehicle in vehicles:
        if vehicle.brand == vehicle_brand and vehicle.capacity == vehicle_capacity:
            user_id = session.get("user_id")
            vehicle_id = vehicle.id
            rental = Rental(start_date=start_date, end_date=end_date, user_id=user_id, vehicle_id=vehicle_id, total_cost=12)
            rental.save()
    
    return render_template('index.html', vehicles=vehicles)

@app.route('/booking')
def booking():
    if is_user_authenticated():
        vehicles = storage.all(Vehicle).values()
        return render_template('booking.html', vehicles=vehicles)
    else:
        return render_template('signup.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    # SQL queries to count records in each table

    car_count = storage.count(Vehicle)
    customer_count = storage.count(User)
    booking_count = storage.count(Rental)

    # Render the dashboard template and pass counts as context
    return render_template('admin_dashboard.html',
                           car_count=car_count,
                           customer_count=customer_count,
                           booking_count=booking_count)

# Customer index page
@app.route('/customer_index')
def customer_index():
    customers = storage.all(User).values()
    print(customers)
    return render_template('customer_index.html', customers=customers)

@app.route('/<string:id>/customer_delete', methods=('POST', 'DELETE',))
def customer_delete(id):
    users = storage.all(User).values()
    for user in users:
        if id == user.id:
            storage.delete(user)
        storage.save()

    return redirect(url_for('customer_index'))

# Booking index page(The logged in user can see his reservation)
@app.route('/booking_index')
def booking_index():
    bookings = storage.all(Rental).values()
    return render_template('booking_index.html', bookings=bookings)

@app.route('/<string:id>/booking_delete', methods=('POST',))
def booking_delete(id):
    rentals = storage.all(Rental).values()
    for rental in rentals:
        if id == rental.id:
            storage.delete(rental)
        storage.save()

    return redirect(url_for('booking_index'))

# Car list
@app.route('/car_index')
def car_index():
    cars = storage.all(Vehicle).values()
    return render_template('car_index.html', cars=cars)

@app.route('/car_create', methods=['GET', 'POST'])
def car_create():
    """
        It retrieve the information from the Admin user and 
        Securely save the uploaded image to the upload folder
        Create a new Vehicle instance and save it to the database
    """

    if request.method == 'POST':
        type = request.form['type']
        brand = request.form['brand']
        capacity = request.form['capacity']
        price_per_day = request.form['price_per_day']
        image = request.files['image']

        error = None

        if not type:
            error = 'Type is required.'
        elif not brand:
            error = 'Brand is required.'
        elif not capacity:
            error = 'Capacity is required.'
        elif not price_per_day:
            error = 'Price Per Day is required.'
        elif not image:
            error = 'Image is required.'
        elif not allowed_file(image.filename):
            error = 'Invalid file type for the image.'

        if error is not None:
            flash(error)
        else:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_data = image.read()

            vehicle = Vehicle(type=type, brand=brand, capacity=capacity, price_per_day=price_per_day, image_data=image_data)
            vehicle.save()

            return redirect(url_for('car_index'))

    return render_template('car_create.html')

@app.route('/<vehicle_id>/uploaded_image')
def uploaded_image(vehicle_id):
    """ 
        Fetch the Vehicle image from the database and 
        return vehicle image if it is found else return not found
    """

    vehicle = storage.get(Vehicle, vehicle_id)

    if vehicle is not None:
        image_data = vehicle.image_data 

        image_format = "jpeg"  # Assuming JPEG for demonstration.
        mime_type = f"image/{image_format}"

        return Response(image_data, content_type=mime_type)
    else:
        return "Vehicle not found", 404
    

@app.route('/<string:id>/car_delete', methods=('POST',))
def car_delete(id):
    """
        Deletes the car with a given id from the database
    """

    cars = storage.all(Vehicle).values()
    for car in cars:
        if id == car.id:
            storage.delete(car)
        storage.save()
    return redirect(url_for('car_index'))

@app.route('/<id>/car_update', methods=('GET', 'POST'))
def car_update(id):
    """
        Admin can update car details
    """

    car = storage.get(Vehicle, id)

    if request.method == 'POST':
        type = request.form['type']
        brand = request.form['brand']
        capacity = request.form['capacity']
        price_per_day = request.form['price_per_day']
        image = request.files['image']

        error = None

        if not type:
            error = 'Type is required.'
        elif not brand:
            error = 'Brand is required.'
        elif not capacity:
            error = 'Capacity is required.'
        elif not price_per_day:
            error = 'Price Per Day is required.'
        elif not image:
            error = 'Image is required.'
        elif not allowed_file(image.filename):
            error = 'Invalid file type for the image.'

        if error is not None:
            flash(error)
        else:
            if car.type != type:
                car.type = type
            if car.capacity != capacity:
                car.capacity = capacity
            if car.brand != brand:
                car.brand = brand
            if car.price_per_day != price_per_day:
                car.price_per_day = price_per_day


            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_data = image.read()
            if car.image_data != image_data:
                car.image_data = image_data
            
            car.save()    

            return redirect(url_for('car_index'))
    return render_template('car_update.html', car=car)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


