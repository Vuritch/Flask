from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/fondok?charset=utf8mb4'
    app.config['SECRET_KEY'] = '123456789'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message = 'Please login to access the booking page.'
    login_manager.login_message_category = 'warning'

    from .models import User  # استدعاء بعد db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .main.routes import main
    from .admin.routes import admin
    from .users.routes import users
    from .bookings.routes import bookings

    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(users)
    app.register_blueprint(bookings)

    return app
