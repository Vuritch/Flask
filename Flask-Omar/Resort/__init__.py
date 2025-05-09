# Resort/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
    app.config['SECRET_KEY'] = '123456789'

    # Upload folder setup
    UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message = 'Please login to access the booking page.'
    login_manager.login_message_category = 'warning'

    from .models import User  # Needed after db.init_app

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from .main.routes import main
    from .admin.routes import admin
    from .users.routes import users
    from .bookings.routes import bookings

    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(users)
    app.register_blueprint(bookings)

    return app

__all__ = [
    'db',
    'login_manager',
    'allowed_file',
    'ALLOWED_EXTENSIONS'
]