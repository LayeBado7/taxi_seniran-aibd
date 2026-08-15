from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="passenger", nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default="offline")
    queue_position = db.Column(db.Integer)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    rating = db.Column(db.Float, default=5.0)
    user = db.relationship("User", backref="driver", uselist=False)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("driver.id"), nullable=False)
    plate = db.Column(db.String(30), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50), default="Jaune")
    active = db.Column(db.Boolean, default=True)
    driver = db.relationship("Driver", backref="vehicle", uselist=False)

class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("driver.id"))
    pickup = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(30), default="requested")
    estimated_fare = db.Column(db.Float, default=0)
    final_fare = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    passenger = db.relationship("User", foreign_keys=[passenger_id])
    driver = db.relationship("Driver", foreign_keys=[driver_id])


class OtpCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(30), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VehicleDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicle.id"), nullable=False)
    document_type = db.Column(db.String(80), nullable=False)
    document_number = db.Column(db.String(120))
    expires_at = db.Column(db.DateTime)
    verified = db.Column(db.Boolean, default=False)
    vehicle = db.relationship("Vehicle", backref="documents")

class SosAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey("ride.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    status = db.Column(db.String(30), default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius_m = db.Column(db.Float, default=1000)
    active = db.Column(db.Boolean, default=True)

class Cancellation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey("ride.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey("ride.id"), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    method = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default="pending")
    reference = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DriverWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("driver.id"), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0)
    total_earned = db.Column(db.Float, default=0)
    total_commission = db.Column(db.Float, default=0)
    driver = db.relationship("Driver", backref="wallet", uselist=False)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey("ride.id"), nullable=False)
    number = db.Column(db.String(80), unique=True, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    commission = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CorporateAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(180), nullable=False)
    contact_phone = db.Column(db.String(40))
    active = db.Column(db.Boolean, default=True)
    credit_limit = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)


class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    partner_type = db.Column(db.String(40), nullable=False)  # hotel, agency, company
    phone = db.Column(db.String(40))
    email = db.Column(db.String(180))
    active = db.Column(db.Boolean, default=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pickup = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default="scheduled")
    estimated_fare = db.Column(db.Float, default=0)
    partner_id = db.Column(db.Integer, db.ForeignKey("partner.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PromoCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False)
    percent = db.Column(db.Float, default=0)
    max_uses = db.Column(db.Integer, default=100)
    uses = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)

class LoyaltyAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.String(30), default="Standard")
