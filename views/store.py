import random

from flask import render_template, redirect, url_for, session, make_response
from flask_restx import Resource, Namespace

from dao.model.models import Product, Order, OrderItem
from setup_db import db
from views.forms import AddToCart, Checkout

store_ns = Namespace('store')


def handle_cart():
    products = []
    cart_summary = {'grand_total': 0, 'grand_total_plus_shipping': 0, 'taxes': 0}
    ind = 0

    for item in session.get('cart', []):
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


@store_ns.route('/product/<pid>')
class ProductItem(Resource):
    def get(self, pid):
        product_ = db.session.query(Product).filter_by(id=pid).first()

        form = AddToCart()

        return make_response(render_template('view-product.html', product=product_, form=form), 200)


@store_ns.route('/quick-add/<int:qid>')
class QuickAdd(Resource):
    def get(self, qid):
        if 'cart' not in session:
            session['cart'] = []

        for item in session['cart']:
            if qid == int(item['id']):
                item['quantity'] += 1
                session.modified = True
                return redirect(url_for('store_index'))

        session['cart'].append({'id': qid, 'quantity': 1})
        session.modified = True
        return redirect(url_for('index'))


@store_ns.route('/add-to-cart')
class AddInCart(Resource):
    def post(self):
        if 'cart' not in session:
            session['cart'] = []

        form = AddToCart()

        if form.validate_on_submit():
            for item in session['cart']:
                print(item)
                if form.id.data == item['id']:
                    item['quantity'] += form.quantity.data
                    session.modified = True
                    return redirect(url_for('index'))

            session['cart'].append({'id': form.id.data, 'quantity': form.quantity.data})
            session.modified = True

        return redirect(url_for('index'))


@store_ns.route('/cart')
class Cart(Resource):
    def get(self):
        products, cart_summary = handle_cart()
        return make_response(render_template('cart.html', products=products, cart_summary=cart_summary), 200)


@store_ns.route('/remove-from-cart/<int:ind>')
class RemoveFromCart(Resource):
    def get(self, ind):
        del session['cart'][ind]
        session.modified = True

        return redirect(url_for('store_cart'))


@store_ns.route('/checkout')
class CheckoutForm(Resource):
    def get(self):
        form = Checkout()
        products, cart_summary = handle_cart()
        return make_response(render_template('checkout.html', form=form, cart_summary=cart_summary), 200)

    def post(self):
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


