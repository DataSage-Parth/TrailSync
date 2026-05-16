"""
SQLAlchemy ORM models for the Trekking Management Application.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), default="")
    role = db.Column(db.String(10), nullable=False, default="user")  # admin, staff, user
    status = db.Column(db.String(15), nullable=False, default="active")  # active, blacklisted
    bio = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship("Booking", backref="user", lazy=True)
    assigned_treks = db.relationship("Trek", backref="staff", lazy=True, foreign_keys="Trek.assigned_staff_id")

    def __repr__(self):
        return f"<User {self.username}>"


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)  # Easy, Moderate, Hard
    duration_days = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(db.String(15), nullable=False, default="Pending")  # Pending, Approved, Open, Closed, Completed
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Float, default=0)
    altitude = db.Column(db.String(50), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship("Booking", backref="trek", lazy=True)

    def __repr__(self):
        return f"<Trek {self.name}>"


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(15), nullable=False, default="Booked")  # Booked, Cancelled, Completed
    notes = db.Column(db.Text, default="")

    def __repr__(self):
        return f"<Booking {self.id}>"
