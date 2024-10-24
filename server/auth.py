from app import app, db  # Import db along with app
from models import User
from flask import request, jsonify

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(username=username, role=role)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback if there's an error
        return jsonify({'error': str(e)}), 500  # Return the error message

    return jsonify({'message': f'User {username} registered successfully as {role}'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({
            'isLoggedIn': True,
            'user': {
                'username': user.username,
                'role': user.role
            }
        }), 200
    return jsonify({'error': 'Invalid credentials'}), 401
