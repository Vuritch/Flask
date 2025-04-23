from Blogger import app, db
from Blogger.models import User, Blog

with app.app_context():
    db.create_all()
    print("Database tables created.")