from datetime import datetime
from flask_login import UserMixin
from Resort import db  # ✅ استخدم نفس db من Resort/__init__.py
from werkzeug.security import generate_password_hash, check_password_hash





class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='guest')

    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RoomType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    base_price = db.Column(db.Float, nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    main_image = db.Column(db.String(255))
    gallery_images = db.Column(db.Text)  # Comma-separated
    features = db.Column(db.Text)  # Comma-separated
    is_luxury = db.Column(db.Boolean, default=False)
    luxury_label = db.Column(db.String(50))

    rooms = db.relationship('Room', backref='room_type', lazy=True)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    floor = db.Column(db.Integer)
    notes = db.Column(db.Text)

    bookings = db.relationship('Booking', backref='room', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.guest_id'), nullable=True)
    num_adults = db.Column(db.Integer, nullable=False, default=1)
    num_children = db.Column(db.Integer, nullable=False, default=0)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    bed_preference = db.Column(db.String(50))
    dining_package = db.Column(db.String(50))
    room_rate = db.Column(db.Float, default=0)
    taxes_and_fees = db.Column(db.Float, default=0)
    dining_total = db.Column(db.Float, default=0)
    services_total = db.Column(db.Float, default=0)
    total_price = db.Column(db.Float, nullable=False)
    special_requests = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)

    extra_services = db.relationship('BookingExtraService', backref='booking', lazy=True)

class ExtraService(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(50), nullable=False)
    description  = db.Column(db.Text)
    price        = db.Column(db.Float, nullable=False)
    type         = db.Column(db.String(50), nullable=False)  # 'dining','service','bed'
    per_adult    = db.Column(db.Boolean, nullable=False, default=False)   # ← NEW

    bookings     = db.relationship('BookingExtraService', backref='extra_service', lazy=True)


class GuestOption(db.Model):
    __tablename__ = 'guest_option'
    id = db.Column(db.Integer, primary_key=True)
    adult_count = db.Column(db.Integer, nullable=False)
    child_count = db.Column(db.Integer, nullable=False, default=0)
    label       = db.Column(db.String(50), nullable=False)
    
class BookingExtraService(db.Model):
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), primary_key=True)
    extra_service_id = db.Column(db.Integer, db.ForeignKey('extra_service.id'), primary_key=True)
    quantity = db.Column(db.Integer, default=1)
class Guest(db.Model):
    guest_id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(80), nullable=False)
    guest_age=db.Column(db.Integer, nullable=False)
    guest_email = db.Column(db.String(50), nullable=False)
    guest_address = db.Column(db.String(120), nullable=False)
    guest_phone = db.Column(db.String(11))
    guest_nationality=db.Column(db.String(100), nullable=False)
    
    booking_guest = db.relationship('Booking', backref='guest', lazy=True)