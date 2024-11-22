from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import os


app = Flask(__name__)

app.secret_key = os.urandom(24)
app.secret_key = 'SDA'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)


#pehlay wala db model...

# class Order(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     customer_name = db.Column(db.String(50), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     delivery_location = db.Column(db.String(100), nullable=False)
#     sale_price = db.Column(db.Float, nullable=False)

#     def __repr__(self):
#         return f"Order {self.id}: {self.customer_name}, {self.date}"

#pehlay wlaa DB model ends



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



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/brand')
def brand():
    return render_template('brand.html')

# @app.route('/orders')
# def orders():
#     all_orders = Order.query.all()  # Fetch all orders from the database
#     return render_template('orders.html', orders=all_orders)


# @app.route('/orders', methods=['GET'])
# def orders():
#     orders = Order.query.options(db.joinedload(Order.items)).all()  # Fetch orders with related items
#     return render_template('orders.html', orders=orders)

@app.route('/orders', methods=['GET'])
def orders():
    page = request.args.get('page', 1, type=int)  # Get the current page number, default is 1
    per_page = 5  # Number of orders per page
    orders_paginated = Order.query.paginate(page=page, per_page=per_page)

    return render_template('orders.html', orders=orders_paginated.items, pagination=orders_paginated)


@app.route('/order/<int:order_id>', methods=['GET'])
def order_details(order_id):
    # Fetch the specific order using its ID
    order = Order.query.get_or_404(order_id)
    return render_template('order_details.html', order=order)



@app.route('/vehicle')
def vehicle():
    return render_template('vehicle.html')

@app.route('/salesman')
def salesman():
    return render_template('salesman.html')

#pehlay wala approute starts....

# @app.route('/add_order', methods=['GET', 'POST'])
# def add_order():
#     if request.method == 'POST':
#         # Get form data
#         customer_name = request.form['customer_name']
#         date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()  # Convert string to date
#         delivery_location = request.form['delivery_location']
#         sale_price = float(request.form['sale_price'])

#         # Create a new Order object
#         new_order = Order(customer_name=customer_name, date=date, delivery_location=delivery_location, sale_price=sale_price)

#         # Add the new order to the database
#         db.session.add(new_order)
#         db.session.commit()

#         # Redirect to the orders page after adding the new order
#         return redirect(url_for('orders'))

#     return render_template('add_order.html')
#pehlay wala app route ends.....

@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        try:
            # Extract customer and transportation details
            customer_name = request.form['customer_name']
            contact = request.form['contact']
            address = request.form['address']
            vehicle_reg_number = request.form['vehicle_reg_number']
            vehicle_rent = float(request.form['vehicle_rent'])
            labor_cost = float(request.form['labor_cost'])
            salesman_name = request.form['salesman_name']

            # Create a new Order object
            new_order = Order(
                customer_name=customer_name,
                contact=contact,
                address=address,
                vehicle_reg_number=vehicle_reg_number,
                vehicle_rent=vehicle_rent,
                labor_cost=labor_cost,
                salesman_name=salesman_name,
                date=datetime.now()  # Assuming you want to save the order date as now
            )

            # Add the order to the session but don't commit yet
            db.session.add(new_order)
            db.session.flush()  # Flush to get the order ID

            # Process all item details
            items_count = len(request.form.getlist('brick_type'))
            for i in range(items_count):
                brick_type = request.form.getlist('brick_type')[i]
                brand = request.form.getlist('brand')[i]
                quantity = int(request.form.getlist('quantity')[i])
                price = float(request.form.getlist('price')[i])

                # Create a new Item object
                new_item = Item(
                    order_id=new_order.id,  # Use the new_order's ID
                    brick_type=brick_type,
                    brand=brand,
                    quantity=quantity,
                    price=price
                )

                # Add the item to the session
                db.session.add(new_item)

            # Commit all changes
            db.session.commit()
            flash("Order and items added successfully!", "success")
            return redirect(url_for('orders'))

        except Exception as e:
            db.session.rollback()  # Roll back if any error occurs
            flash(f"An error occurred: {e}", "danger")
            return render_template('add_order.html')

    # Render the form on GET request
    return render_template('add_order.html')





@app.route('/signin', methods=['POST'])
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
    


@app.route('/order_list_buttons', methods=['POST'])
def orders_list_buttons():
    button_pressed = request.form['button']
    if button_pressed == 'add_order':
        return redirect(url_for('add_order'))
    else:
        return redirect(url_for('orders'))
    



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
