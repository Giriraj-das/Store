import os

DATABASE_PATH = os.path.join(os.getcwd(), 'store.db')


class Config(object):
    UPLOADED_PHOTOS_DEST = 'images'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'mysecret'
    DEBUG = True
