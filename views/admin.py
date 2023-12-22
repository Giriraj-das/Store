from flask import render_template, redirect, url_for, make_response
from flask_restx import Resource, Namespace

from dao.model.models import Product, Order
from setup_db import db
from views.forms import AddProduct, photos

admin_ns = Namespace('admin')


@admin_ns.route('/')
class Admin(Resource):
    def get(self):
        products = db.session.query(Product).all()
        products_in_stock = db.session.query(Product).filter(Product.stock > 0).count()

        orders = db.session.query(Order).all()

        return make_response(render_template('admin/index.html',
                                             admin=True,
                                             products=products,
                                             products_in_stock=products_in_stock,
                                             orders=orders), 200)


@admin_ns.route('/add')
class Add(Resource):
    def get(self):
        form = AddProduct()
        return make_response(render_template('admin/add-product.html', admin=True, form=form), 200)

    def post(self):
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
        return redirect(url_for('admin_admin'))


@admin_ns.route('/order/<order_id>')
class OrderItem(Resource):
    def get(self, order_id):
        admin_order = db.session.query(Order).filter(Order.id == order_id).first()

        return make_response(render_template('admin/view-order.html', order=admin_order, admin=True), 200)
