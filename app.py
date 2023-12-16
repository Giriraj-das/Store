from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField, SelectField
from flask_wtf.file import FileField, FileAllowed
import random

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/ALL/PythonProjects/Store_App/store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'mysecret'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
configure_uploads(app, photos)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    description = db.Column(db.String(500))
    image = db.Column(db.String(100))

    orders = db.relationship('OrderItem', backref='product', lazy=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(5))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(50))
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    district = db.Column(db.String(20))
    country = db.Column(db.String(20))
    status = db.Column(db.String(10))
    payment_type = db.Column(db.String(10))

    items = db.relationship('OrderItem', backref='order', lazy=True)

    def order_total(self):
        return db.session.query(
            db.func.sum(OrderItem.quantity * Product.price)
        ).join(Product).filter(OrderItem.order_id == self.id).scalar() + 5

    def quantity_total(self):
        return db.session.query(
            db.func.sum(OrderItem.quantity)
        ).filter(OrderItem.order_id == self.id).scalar()


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)


class AddProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')
    stock = IntegerField('Stock')
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])


class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity')
    id = HiddenField('ID')


class Checkout(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone_number = StringField('Number')
    email = StringField('Email')
    address = StringField('Address')
    city = StringField('City')
    district = SelectField('Region', choices=['Kyiv', 'Dnipro', 'Odesa', 'Lviv', 'Kharkiv', 'Chișinău',
                                              'Warsaw', 'Istambul', 'Ankara'])
    country = SelectField('Country', choices=[('UA', 'Ukraine'), ('PL', 'Poland'), ('MD', 'Moldova'), ('TR', 'Türkiye')])
    payment_type = SelectField('Payment Type', choices=['Pay on Delivery', 'Pay by Card'])


def handle_cart():
    products = []
    cart_summary = {'grand_total': 0, 'grand_total_plus_shipping': 0, 'taxes': 0}
    ind = 0

    for item in session['cart']:
        product_ = db.session.query(Product).filter_by(id=item['id']).first()
        quantity = int(item['quantity'])

        total = quantity * product_.price
        cart_summary['grand_total'] += total

        products.append({'id': product_.id,
                         'name': product_.name,
                         'price': product_.price,
                         'image': product_.image,
                         'quantity': quantity,
                         'total': total,
                         'index': ind})
        ind += 1

    cart_summary['grand_total_plus_shipping'] = cart_summary['grand_total'] + 5

    return products, cart_summary


@app.route('/')
def index():
    products = db.session.query(Product).all()
    return render_template('index.html', products=products)


@app.route('/product/<pid>')
def product(pid):
    product_ = db.session.query(Product).filter_by(id=pid).first()

    form = AddToCart()

    return render_template('view-product.html', product=product_, form=form)


@app.route('/quick-add/<qid>')
def quick_add(qid):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({'id': qid, 'quantity': 1})
    session.modified = True

    return redirect(url_for('index'))


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    form = AddToCart()

    if form.validate_on_submit():
        session['cart'].append({'id': form.id.data, 'quantity': form.quantity.data})
        session.modified = True

    return redirect(url_for('index'))


@app.context_processor
def utility_processor():
    count = 0
    for item in session['cart']:
        count += item['quantity']

    return dict(count=count)


@app.route('/cart')
def cart():
    products, cart_summary = handle_cart()
    return render_template('cart.html', products=products, cart_summary=cart_summary)


@app.route('/remove-from-cart/<int:ind>')
def remove_from_cart(ind):
    del session['cart'][ind]
    session.modified = True

    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = Checkout()
    products, cart_summary = handle_cart()

    if form.validate_on_submit():
        order_ = Order()
        form.populate_obj(order_)
        order_.reference = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') for _ in range(8))
        order_.status = 'PENDING'

        for product_ in products:
            order_item = OrderItem(product_id=product_['id'], quantity=product_['quantity'])
            order_.items.append(order_item)

            db.session.query(Product).filter_by(id=product_['id']).update({'stock': Product.stock - product_['quantity']})
            # product_by_id = db.session.get(Product, product_['id'])
            # product_by_id.stock = product_by_id.stock - product_['quantity']
            # db.session.add(product_by_id)
            # db.session.commit()

        db.session.add(order_)
        db.session.commit()

        session['cart'] = []
        session.modified = True

        return redirect(url_for('index'))

    return render_template('checkout.html', form=form, cart_summary=cart_summary)


@app.route('/admin')
def admin():
    products = db.session.query(Product).all()
    products_in_stock = db.session.query(Product).filter(Product.stock > 0).count()

    orders = db.session.query(Order).all()

    return render_template('admin/index.html',
                           admin=True,
                           products=products,
                           products_in_stock=products_in_stock,
                           orders=orders)


@app.route('/admin/add', methods=['GET', 'POST'])
def add():
    form = AddProduct()
    if form.validate_on_submit():
        image_url = photos.url(photos.save(form.image.data))
        new_product = Product(name=form.name.data,
                              price=form.price.data,
                              stock=form.stock.data,
                              description=form.description.data,
                              image=image_url)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('admin/add-product.html', admin=True, form=form)


@app.route('/admin/order/<order_id>')
def order(order_id):
    admin_order = db.session.query(Order).filter(Order.id == order_id).first()

    return render_template('admin/view-order.html', order=admin_order, admin=True)


if __name__ == '__main__':
    app.run()
