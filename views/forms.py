from flask_uploads import UploadSet
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, TextAreaField, SelectField, HiddenField

IMAGE_EXTENSIONS = ('jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp')
photos = UploadSet('photos', IMAGE_EXTENSIONS)


class AddProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')
    stock = IntegerField('Stock')
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(IMAGE_EXTENSIONS, 'Only images are accepted.')])


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