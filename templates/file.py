@app.route('/add_brand', methods=['GET', 'POST'])
def add_brand():
    if request.method == 'POST':  # If the form is submitted (POST request)
        try:
            # Get form data for the new brand
            brand_name = request.form['brand_name']
            location = request.form['location']
            principal_contact = request.form['principal_contact']
            contact_no = request.form['contact_no']
            brick_types = request.form.getlist('brick_types')  # Get selected brick types

            # Create a new Brand instance with the provided data
            new_brand = Brand(
                name=brand_name,
                location=location,
                principal_contact=principal_contact,
                contact_no=contact_no
            )

            # Add the brand to the database and commit the transaction
            db.session.add(new_brand)
            db.session.commit()

            # Print for debugging purposes
            print(f"New Brand ID: {new_brand.id}")
            print(f"Brick Types Received: {brick_types}")

            # Now add the brick types (if any)
            for brick_type in brick_types:
                if brick_type.strip():  # Ensure the brick type is not empty
                    new_brick_type = BrickType(
                        type_name=brick_type.strip(),  # Trim whitespace
                        brand_id=new_brand.id  # Associate this brick type with the brand
                    )
                    db.session.add(new_brick_type)

            db.session.commit()

            # Flash a success message and redirect
            flash("Brand and brick types added successfully!", "success")
            return redirect(url_for('brand'))  # Redirect to the brand list page

        except Exception as e:  # If there's an error while adding the brand
            db.session.rollback()  # Rollback the database transaction
            flash(f"Error adding brand: {e}", "danger")  # Flash an error message
            return render_template('add_brand.html')  # Return the add brand form with error message

    return render_template('add_brand.html')  # Render the form to add a brand (GET request)
