from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint that returns JWT token"""
    data = request.json
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role, 'username': user.username}
        )
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    """Register new user (admin only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Username, email, and password required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'user')  # Default to 'user' role
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify if token is valid"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    
    return jsonify({'valid': True, 'user': user.to_dict()}), 200

