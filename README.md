# Online Store
Written in Flask.

USED:  
- SQLite database
- Flask-RESTx
- Flask-Migrate
- Flask-Uploads
- Flask-WTF

В venv/lib/site-packages/werkzeug/__init__.py добавить два импорта   

from .utils import secure_filename   
from .datastructures.file_storage import FileStorage
