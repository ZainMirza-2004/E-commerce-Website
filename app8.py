from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, class_mapper
from models import Technology, User
from werkzeug.security import generate_password_hash, check_password_hash
from forms import OpinionForm, PaymentForm, RegistrationForm, LoginForm

app = Flask(__name__)
app.static_folder = 'static'
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "top secret password don't tell anyone this"

# SQLite database file path
DATABASE_URI = 'sqlite:///products.db'
USERS_DATABASE_URI = 'sqlite:///users.db'

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
db_session = Session()

engine = create_engine(USERS_DATABASE_URI)
Session = sessionmaker(bind=engine)
db_session_users = Session()

@app.route('/')
def galleryPage():
    sort_by = request.args.get('sort', 'name')  # Default sorting by name if no sort option provided
    if sort_by == 'price_asc':
        distinct_tech_ids = db_session.query(func.min(Technology.id)).group_by(Technology.name).order_by(Technology.price.asc()).all()
    elif sort_by == 'price_desc':
        distinct_tech_ids = db_session.query(func.min(Technology.id)).group_by(Technology.name).order_by(Technology.price.desc()).all()
    elif sort_by == 'carbon':
        distinct_tech_ids = db_session.query(func.min(Technology.id)).group_by(Technology.name).order_by(Technology.carbon).all()
    else:
        sort_by = 'name'  # Default sorting by name
        distinct_tech_ids = db_session.query(func.min(Technology.id)).group_by(Technology.name).order_by(Technology.name).all()

    distinct_technologies = [db_session.query(Technology).get(tech_id) for tech_id, in distinct_tech_ids]
    
    return render_template('index copy.html', technologies=distinct_technologies, current_sort=sort_by)


@app.route('/get-description', methods=['GET'])
def get_description():
    product_id = request.args.get('id')
    # Query the database to get the description of the product with the given ID
    technology = db_session.query(Technology).get(product_id)
    if technology:
        description = technology.description
        return jsonify(description=description)  # Returning description as JSON
    else:
        # If the product with the given ID is not found, return a 404 error
        return jsonify(error='Product not found'), 404



@app.route('/tech/<int:techId>', methods=['GET', 'POST'])
def singleProductPage(techId):
    form = OpinionForm()
    technology = db_session.query(Technology).get(techId)

    if form.validate_on_submit():
        quantity = int(form.opinion.data)

        # Update basket quantity in the Flask session
        if 'basket' not in session:
            session['basket'] = {}

        # Convert techId to string for session storage
        techId_str = str(techId)

        if techId_str in session['basket']:
            session['basket'][techId_str] += quantity
        else:
            session['basket'][techId_str] = quantity

        session.modified = True  # Mark the session as modified

        print("Item added to basket:", techId, quantity)  # Add this line

        return render_template('SingleTechOpinion.html', technology=technology, opinion=quantity)
    else:
        return render_template('SingleTech copy.html', technology=technology, form=form)

@app.route('/quantity/<int:techId>', methods=['GET', 'POST'])
def quantityPage(techId):
    form = OpinionForm()
    technology = db_session.query(Technology).get(techId)

    if form.validate_on_submit():
        quantity = int(form.opinion.data)

        # Update basket quantity in the Flask session
        if 'basket' not in session:
            session['basket'] = {}

        # Convert techId to string for session storage
        techId_str = str(techId)

        if techId_str in session['basket']:
            session['basket'][techId_str] += quantity
        else:
            session['basket'][techId_str] = quantity

        session.modified = True  # Mark the session as modified

        return redirect(url_for('basketPage'))

    return render_template('quantity_form.html', technology=technology, form=form)

@app.route('/basket')
def basketPage():
    basket_contents = session.get('basket', {})
    technologies_in_basket = []
    total_price = 0

    for tech_id, quantity in basket_contents.items():
        technology = db_session.query(Technology).get(int(tech_id))
        technologies_in_basket.append({'technology': technology, 'quantity': quantity})
        total_price += technology.price * quantity

    return render_template('basket_page.html', technologies_in_basket=technologies_in_basket, total_price=total_price)

@app.route('/remove-from-basket/<int:techId>')
def removeFromBasket(techId):
    techId_str = str(techId)
    if 'basket' in session and techId_str in session['basket']:
        # Reduce the quantity by 1
        session['basket'][techId_str] -= 1
        # If the quantity becomes 0, remove the item from the basket
        if session['basket'][techId_str] <= 0:
            del session['basket'][techId_str]
        session.modified = True
    return redirect(url_for('basketPage'))



@app.route('/checkout', methods=['GET', 'POST'])
def checkoutPage():
    form = PaymentForm()
    if form.validate_on_submit():
        # Retrieve the items from the basket
        basket_contents = session.get('basket', {})
        purchased_items = []

        for tech_id, quantity in basket_contents.items():
            technology = db_session.query(Technology).get(int(tech_id))
            # Serialize the necessary information from the Technology object
            serialized_technology = {
                'id': technology.id,
                'name': technology.name,
                'price': technology.price,
                'quantity': quantity
            }
            purchased_items.append(serialized_technology)

        # Store purchased items and address in session
        session['purchased_items'] = purchased_items
        session['address'] = {
            'street_address': request.form['street_address'],
            'city': request.form['city'],
            'state': request.form['state'],
            'postal_code': request.form['postal_code']
        }

        # Form validation successful, proceed to success page
        return render_template('checkout_success.html', form=form)
    
    # If form validation fails or initial visit to the page, render the checkout form
    return render_template('checkout_page.html', form=form)

@app.route('/purchase-details')
def purchaseDetailsPage():
    purchased_items = session.get('purchased_items', [])
    total_price = sum(item['price'] * item['quantity'] for item in purchased_items)
    recipient_name = session.get('username', 'Guest')  # Default to 'Guest' if not signed in
    recipient_address = session.get('address', {})  # Retrieve the address from the session
    
    # Render shipping label and invoice templates
    shipping_label_html = render_template('shipping_label.html', recipient_name=recipient_name, recipient_address=recipient_address)
    invoice_html = render_template('invoice.html', purchased_items=purchased_items, total_price=total_price)
    
    return shipping_label_html + invoice_html


@app.route('/clear-basket', methods=['POST'])
def clearBasket():
    if 'basket' in session:
        session.pop('basket')  # Remove the entire basket from the session
        session.modified = True
    return redirect(url_for('basketPage'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if the username already exists
        existing_user = db_session.query(User).filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # If username is unique, create a new user
        new_user = User(username=username, password=hashed_password)
        db_session.add(new_user)
        db_session.commit()
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Retrieve the user by username
        user = db_session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = username
            flash('You are already logged in!', 'success')
            return redirect(url_for('galleryPage'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # Remove the 'logged_in' and 'username' keys from the session
    session.pop('logged_in', None)
    session.pop('username', None)
    # Redirect the user to the gallery page or any other page you desire
    return redirect(url_for('galleryPage'))



if __name__ == '__main__':
    app.run(debug=True)