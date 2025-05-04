from datetime import datetime
from flask_login import UserMixin
from Resort import db  # ✅ استخدم نفس db من Resort/__init__.py

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f"User({self.name}, {self.email})"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_type = db.Column(db.String(100), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.String(50), nullable=False)
    child_ages = db.Column(db.String(100))  # Stored as comma-separated values
    bed_preference = db.Column(db.String(20))  # Made nullable
    dining_package = db.Column(db.String(20))
    airport_transfer = db.Column(db.Boolean, default=False)
    spa_package = db.Column(db.Boolean, default=False)
    romantic_package = db.Column(db.Boolean, default=False)
    room_rate = db.Column(db.Float, nullable=False)
    taxes_and_fees = db.Column(db.Float, nullable=False)
    dining_total = db.Column(db.Float, default=0.0)
    services_total = db.Column(db.Float, default=0.0)
    total_price = db.Column(db.Float, nullable=False)   
    special_requests = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)   
    user = db.relationship('User', backref='bookings')

    def __repr__(self):
        return f"Booking('{self.room_type}', '{self.check_in}' to '{self.check_out}')"
