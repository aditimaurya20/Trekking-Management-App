from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy for database ORM
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto increment primary key
    custom_id = db.Column(db.String(10), unique=True)  # U10001 or S10001
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / staff / trekker
    is_active = db.Column(db.Boolean, default=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):  # Hash and set password
        self.password = generate_password_hash(password)

    def check_password(self, password):  # Check hashed password
        return check_password_hash(self.password, password)

    def generate_custom_id(self):  # Generate custom ID based on role
        if self.role == 'admin':
            self.custom_id = f'A{10000 + self.id}'
        elif self.role == 'staff':
            self.custom_id = f'S{10000 + self.id}'
        else:
            self.custom_id = f'U{10000 + self.id}'

class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto increment primary key
    custom_id = db.Column(db.String(10), unique=True)  # T10001
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # Easy / Moderate / Hard
    duration = db.Column(db.Integer, nullable=False)  # in days
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending/Approved/Open/Closed/Completed
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bookings = db.relationship('Booking', backref='trek', lazy=True)

    def generate_custom_id(self):  # Generate custom trek ID
        self.custom_id = f'T{10000 + self.id}'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto increment primary key
    custom_id = db.Column(db.String(10), unique=True)  # B10001
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    booking_date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Booked')  # Booked / Cancelled / Completed

    def generate_custom_id(self):  # Generate custom booking ID
        self.custom_id = f'B{10000 + self.id}'

class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto increment primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Active')