from database import db, bcrypt
from datetime import datetime
from sqlalchemy.orm import validates
from flask_login import UserMixin

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_name = db.Column(db.String(100), nullable=False)
    tenant_phone_number = db.Column(db.String(20), nullable=False, unique=True)
    house_number = db.Column(db.String(10), nullable=False)
    house_type = db.Column(db.String(50), nullable=False)
    deposit_paid = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    receipt_number_deposit = db.Column(db.String(100), nullable=True, unique=True)
    rent_amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(day=5))
    rent_receipt_number = db.Column(db.String(100), nullable=True, unique=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    property = db.relationship('Property', back_populates='tenants')
    rent_paid = db.Column(db.Float, nullable=True)
    amount_due = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "tenant_name": self.tenant_name,
            "tenant_phone_number": self.tenant_phone_number,
            "house_number": self.house_number,
            "house_type": self.house_type,
            "deposit_paid": self.deposit_paid,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "receipt_number_deposit": self.receipt_number_deposit,
            "rent_amount": self.rent_amount,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "rent_receipt_number": self.rent_receipt_number,
            "property_id": self.property_id,
            "rent_paid": self.rent_paid,
            "amount_due": self.amount_due
        }

    @validates('tenant_phone_number')
    def validate_phone(self, key, phone):
        if len(phone) != 10 or not phone.isdigit():
            raise ValueError("Phone number must be 10 digits long and numeric.")
        return phone

class Landlord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    landlord_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    properties_owned = db.relationship('Property', back_populates='landlord', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "landlord_name": self.landlord_name,
            "phone_number": self.phone_number,
            "email": self.email,
            "properties_owned": [property.to_dict() for property in self.properties_owned]
        }

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'), nullable=False)
    number_of_rooms = db.Column(db.Integer, nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    house_number = db.Column(db.String(10), nullable=False)
    occupied_rooms = db.Column(db.Integer, nullable=False, default=0)
    price_bedsitter = db.Column(db.Float, nullable=True)
    price_one_bedroom = db.Column(db.Float, nullable=True)
    price_two_bedroom = db.Column(db.Float, nullable=True)
    tenants = db.relationship('Tenant', back_populates='property', lazy=True)
    landlord = db.relationship('Landlord', back_populates='properties_owned')

    def to_dict(self):
        return {
            "id": self.id,
            "property_name": self.property_name,
            "location": self.location,
            "landlord_id": self.landlord_id,
            "number_of_rooms": self.number_of_rooms,
            "is_occupied": self.is_occupied,
            "house_number": self.house_number,
            "occupied_rooms": self.occupied_rooms,
            "price_bedsitter": self.price_bedsitter,
            "price_one_bedroom": self.price_one_bedroom,
            "price_two_bedroom": self.price_two_bedroom,
            "tenants": [tenant.to_dict() for tenant in self.tenants]
        }

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
