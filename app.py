from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)


app.secret_key = 'SDA'


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)


@app.route('/signin_button', methods=['POST'])
def signin_button():
    # Handle the button click here
    return redirect(url_for('dashboard'))


@app.route('/sidebar_buttons', methods=['POST'])
def sidebar_buttons():
    button_pressed = request.form['button']
    if button_pressed == 'dashboard':
        return redirect(url_for('dashboard'))
    elif button_pressed == 'brand':
        return redirect(url_for('brand'))
    elif button_pressed == 'vehicle':
        return redirect(url_for('vehicle'))
    elif button_pressed == 'orders':
        return redirect(url_for('orders'))
    elif button_pressed == 'salesman':
        return redirect(url_for('salesman'))
    else:
        return redirect(url_for('home'))
    



# Order and Item Models
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(15), nullable=False)  # Customer contact number
    address = db.Column(db.String(150), nullable=False)  # Delivery address
    vehicle_reg_number = db.Column(db.String(20), nullable=True)  # Vehicle registration number
    vehicle_rent = db.Column(db.Float, nullable=True)  # Rent cost of the vehicle
    labor_cost = db.Column(db.Float, nullable=True)  # Cost of labor
    salesman_name = db.Column(db.String(50), nullable=True)  # Salesperson name
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)  # Order date
    items = db.relationship('Item', backref='order', cascade="all, delete-orphan")  # Relationship to Item

    def __repr__(self):
        return f"<Order {self.id}: {self.customer_name} on {self.date}>"

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # Foreign key to Order
    brick_type = db.Column(db.String(50), nullable=False)  # Type of bricks
    brand = db.Column(db.String(50), nullable=False)  # Brand of the bricks
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of bricks
    price = db.Column(db.Float, nullable=False)  # Price of bricks

    def __repr__(self):
        return f"<Item {self.id}: {self.brick_type} - {self.brand} ({self.quantity} @ {self.price})>"

# Vehicle Model
class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    registration_no = db.Column(db.String(20), unique=True, nullable=False)  # Vehicle registration number
    vehicle_type = db.Column(db.String(50), nullable=False)  # Type of vehicle
    capacity = db.Column(db.Integer, nullable=False)  # Capacity in kilograms
    ownership_status = db.Column(db.String(10), nullable=False)  # Ownership status (own/private)

    def __repr__(self):
        return f"<Vehicle {self.registration_no}: {self.vehicle_type}, {self.capacity}kg, {self.ownership_status}>"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/brand')
def brand():
    return render_template('brand.html')

@app.route('/order_list_buttons', methods=['POST'])
def orders_list_buttons():
    button_pressed = request.form['button']
    if button_pressed == 'add_order':
        return redirect(url_for('add_order'))
    else:
        return redirect(url_for('orders'))
    

@app.route('/orders', methods=['GET'])
def orders():
    page = request.args.get('page', 1, type=int)  # Get the current page number, default is 1
    per_page = 5  # Number of orders per page
    orders_paginated = Order.query.paginate(page=page, per_page=per_page)

    return render_template('orders.html', orders=orders_paginated.items, pagination=orders_paginated)

@app.route('/order/<int:order_id>', methods=['GET'])
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_details.html', order=order)

@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        try:
            customer_name = request.form['customer_name']
            contact = request.form['contact']
            address = request.form['address']
            vehicle_reg_number = request.form['vehicle_reg_number']
            vehicle_rent = float(request.form['vehicle_rent'])
            labor_cost = float(request.form['labor_cost'])
            salesman_name = request.form['salesman_name']

            new_order = Order(
                customer_name=customer_name,
                contact=contact,
                address=address,
                vehicle_reg_number=vehicle_reg_number,
                vehicle_rent=vehicle_rent,
                labor_cost=labor_cost,
                salesman_name=salesman_name,
                date=datetime.now()
            )

            db.session.add(new_order)
            db.session.flush()

            items_count = len(request.form.getlist('brick_type'))
            for i in range(items_count):
                brick_type = request.form.getlist('brick_type')[i]
                brand = request.form.getlist('brand')[i]
                quantity = int(request.form.getlist('quantity')[i])
                price = float(request.form.getlist('price')[i])

                new_item = Item(
                    order_id=new_order.id,
                    brick_type=brick_type,
                    brand=brand,
                    quantity=quantity,
                    price=price
                )

                db.session.add(new_item)

            db.session.commit()
            flash("Order and items added successfully!", "success")
            return redirect(url_for('orders'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
            return render_template('add_order.html')

    return render_template('add_order.html')



@app.route('/vehicle_list_buttons', methods=['POST'])
def vehicle_list_buttons():
    button_value = request.form.get('button')
    if button_value == 'add_vehicle':
        return redirect(url_for('add_vehicle'))
    return redirect(url_for('vehicle'))



@app.route('/vehicle', methods=['GET'])
def vehicle():
    page = request.args.get('page', 1, type=int)  # Get the current page number for pagination
    per_page = 5  # Number of vehicles per page
    vehicles_paginated = Vehicle.query.paginate(page=page, per_page=per_page)

    return render_template('vehicle.html', vehicles=vehicles_paginated.items, pagination=vehicles_paginated)

@app.route('/vehicle/<int:vehicle_id>', methods=['GET'])
def vehicle_details(vehicle_id):
    # Fetch the vehicle by ID
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Render a detailed view of the vehicle
    return render_template('vehicle_details.html', vehicle=vehicle)


@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        try:
            registration_no = request.form['vehicle_reg_number']
            vehicle_type = request.form['vehicle_type']
            capacity = int(request.form['vehicle_capacity'])
            ownership_status = request.form['ownership_status']

            new_vehicle = Vehicle(
                registration_no=registration_no,
                vehicle_type=vehicle_type,
                capacity=capacity,
                ownership_status=ownership_status
            )

            db.session.add(new_vehicle)
            db.session.commit()

            flash("Vehicle added successfully!", "success")
            return redirect(url_for('vehicle'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding vehicle: {e}", "danger")
            return render_template('add_vehicle.html')

    return render_template('add_vehicle.html')


@app.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    # Fetch the vehicle or return a 404 error if it doesn't exist
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        try:
            # Update vehicle details from the form
            vehicle.registration_no = request.form['vehicle_reg_number']
            vehicle.vehicle_type = request.form['vehicle_type']
            vehicle.capacity = int(request.form['vehicle_capacity'])
            vehicle.ownership_status = request.form['ownership_status']

            # Save changes to the database
            db.session.commit()

            # Redirect to vehicle details after successful edit
            flash("Vehicle updated successfully!", "success")
            return redirect(url_for('vehicle_details', vehicle_id=vehicle.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating vehicle: {e}", "danger")

    # Render the edit form with the current vehicle data for a GET request
    return render_template('edit_vehicle.html', vehicle=vehicle)




@app.route('/brand_list_buttons', methods=['POST'])
def brand_list_buttons():
    button_value = request.form.get('button')
    if button_value == 'add_brand':
        return redirect(url_for('add_brand'))
    return redirect(url_for('brand'))



@app.route('/add_brand', methods=['GET', 'POST'])
def add_brand():
    return render_template('add_brand.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)




