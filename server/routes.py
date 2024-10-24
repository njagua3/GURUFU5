from flask import request, jsonify, abort
from flask_restful import Resource, Api
from flask_login import login_required, current_user
from marshmallow import ValidationError
from functools import wraps
from database import db
from models import Tenant, Landlord, Property
from app import app

api = Api(app)

def get_object_or_404(model, object_id):
    obj = model.query.get(object_id)
    if obj is None:
        abort(404, description=f"{model.__name__} with ID {object_id} not found")
    return obj

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return wrap

class TenantResource(Resource):
    def get(self, id=None):
        if id:
            tenant = get_object_or_404(Tenant, id)
            return tenant.to_dict(), 200
        tenants = Tenant.query.all()
        return [tenant.to_dict() for tenant in tenants], 200

    def post(self):
        data = request.get_json()
        tenant = Tenant(**data)
        db.session.add(tenant)
        db.session.commit()
        return tenant.to_dict(), 201

class LandlordResource(Resource):
    def get(self, id=None):
        if id:
            landlord = get_object_or_404(Landlord, id)
            return landlord.to_dict(), 200
        landlords = Landlord.query.all()
        return [landlord.to_dict() for landlord in landlords], 200

    def post(self):
        data = request.get_json()
        landlord = Landlord(**data)
        db.session.add(landlord)
        db.session.commit()
        return landlord.to_dict(), 201

class PropertyResource(Resource):
    def get(self, id=None):
        if id:
            property = get_object_or_404(Property, id)
            return property.to_dict(), 200
        properties = Property.query.all()
        return [property.to_dict() for property in properties], 200

    def post(self):
        data = request.get_json()
        property = Property(**data)
        db.session.add(property)
        db.session.commit()
        return property.to_dict(), 201

@app.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    tenant_count = Tenant.query.count()
    landlord_count = Landlord.query.count()
    property_count = Property.query.count()
    
    return jsonify({
        "tenants": tenant_count,
        "landlords": landlord_count,
        "properties": property_count
    }), 200

api.add_resource(TenantResource, '/tenants', '/tenants/<int:id>')
api.add_resource(LandlordResource, '/landlords', '/landlords/<int:id>')
api.add_resource(PropertyResource, '/properties', '/properties/<int:id>')