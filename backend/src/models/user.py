from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to SEO results
    seo_results = db.relationship('SEOResult', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SEOResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.Text, nullable=True)
    long_description = db.Column(db.Text, nullable=True)
    keywords = db.Column(db.Text, nullable=True)  # JSON string of keywords
    opening_hours = db.Column(db.Text, nullable=True)
    company_info = db.Column(db.Text, nullable=True)  # JSON string of company info
    raw_response = db.Column(db.Text, nullable=True)  # Full GPT response
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<SEOResult {self.domain}>'

    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain,
            'short_description': self.short_description,
            'long_description': self.long_description,
            'keywords': self.keywords,
            'opening_hours': self.opening_hours,
            'company_info': self.company_info,
            'raw_response': self.raw_response,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None
        }
