from flask import render_template, redirect, flash, request, session, url_for
from forms import RegisterForm, ProductForm, LoginForm
from ext import app, db
from models import Product, Comment, User
from flask_login import login_user, logout_user, login_required, current_user
import os
from collections import Counter

@app.route('/')
def home():
    category = request.args.get('category')
    print("FILTERING CATEGORY:", category)
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()

    role = getattr(current_user, 'role', None) if current_user.is_authenticated else None
    return render_template('home.html', products=products, role=role, cart_items=session.get('cart_items', []))

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart_items', [])
    products = Product.query.filter(Product.id.in_(cart_items)).all() if cart_items else []
    return render_template('cart.html', products=products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    action = request.form.get('action')

    product = Product.query.get_or_404(product_id)

    if 'cart_items' not in session:
        session['cart_items'] = []

    cart = session['cart_items']

    if action == 'add_to_cart':

        if product_id not in cart:
            cart.append(product_id)
        session['cart_items'] = cart
        flash(f"{product.name} კალათაში დამატებულია", "success")
        return redirect(url_for('home'))

    elif action == 'buy':

        if product_id not in cart:
            cart.append(product_id)
            session['cart_items'] = cart
        return redirect(url_for('cart'))


    return redirect(url_for('home'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart_items', [])
    if product_id in cart:
        cart.remove(product_id)
        session['cart_items'] = cart
        flash("პროდუქტი წაშლილია", "success")
    return redirect(url_for('cart'))


@app.route('/checkout')
def checkout():
    cart = session.get('cart_items', [])

    counter = Counter(cart)

    cart_items = []

    for product_id, quantity in counter.items():
        product = Product.query.get(product_id)
        if product:
            cart_items.append({
                'name': product.name,
                'price': product.price,
                'quantity': quantity
            })

    return render_template('checkout.html', cart_items=cart_items)

@app.route('/category/<category>')
def category_filter(category):
    category = request.args.get("category")
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()
    return render_template('category.html', category=category, products=products)

@app.route("/profile")
@login_required
def profile():
    products = Product.query.all()
    return render_template("profile.html", products=products, user=current_user)

@app.route("/detailed/<int:product_id>")
def detailed(product_id):
    detailed_product = Product.query.get_or_404(product_id)
    comment = Comment.query.filter_by(product_id=product_id).all()
    return render_template("detailed.html", product=detailed_product, comments=comment)

@app.route("/create_product", methods=["GET", "POST"])
@login_required
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(name=form.name.data, price=form.price.data, category=form.category.data)
        image = form.img.data
        directory = os.path.join(app.root_path, "static", "images", image.filename)
        image.save(directory)
        new_product.img = image.filename

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("create_product.html", form=form)


@app.route('/product/<int:product_id>/comment', methods=['POST'])
@login_required
def add_comment(product_id):
    comment_text = request.form.get('comment')
    if not comment_text:
        flash('Please enter a comment.', 'warning')
        return redirect(url_for('detailed', product_id=product_id))
    

    new_comment = Comment(text=comment_text, product_id=product_id, user_id=current_user.id)
    db.session.add(new_comment)
    db.session.commit()
    flash('Comment added successfully.', 'success')
    return redirect(url_for('detailed', product_id=product_id))
@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data

        image = form.img.data
        if image:
            filename = image.filename
            path = os.path.join(app.root_path, "static", "images", filename)
            image.save(path)
            product.img = filename

        db.session.commit()
        flash("პროდუქტი განახლდა", "success")
        return redirect(url_for("home"))

    return render_template("create_product.html", form=form)

@app.route("/delete_product/<int:product_id>",  methods=["POST", "GET"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("პროდუქტი წაიშალა", "warning")
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("თქვენ წარმატებით გაიარეთ ავტორიზაცია", "success")
            return redirect(url_for("home"))
        else:
            flash("მომხმარებელი ან პაროლი არასწორია", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash("თქვენ გამოხვედით სისტემიდან", "info")
    return redirect(url_for("home"))
from werkzeug.utils import secure_filename

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        new_user = User(
            username=form.username.data,
            password=form.password.data,
            birthday=form.birthday.data
        )


        image = form.profile_img.data
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.root_path, 'static', 'images', filename)
            image.save(image_path)
            new_user.profile_img = filename


        db.session.add(new_user)
        db.session.commit()

        flash("რეგისტრაცია წარმატებით დასრულდა", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)
