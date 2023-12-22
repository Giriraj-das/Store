from setup_db import db


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
