from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db

user_bp = Blueprint('user', __name__)

def require_admin():
    """Helper function to check if current user is admin"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    return current_user and current_user.role == 'admin'

@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Create new user (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Username, email, and password required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'user')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Check for username/email conflicts
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
    
    if 'role' in data:
        user.role = data['role']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the last admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return jsonify({'error': 'Cannot delete the last admin user'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return '', 204
