from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from .user import db

class GeneratedImage(db.Model):
    """Model for storing generated images"""
    __tablename__ = 'generated_images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_input = db.Column(db.Text, nullable=False)  # Benutzer-Eingabe
    image_type = db.Column(db.String(20), nullable=False)  # 'header' oder 'kachel'
    image_url = db.Column(db.String(500), nullable=False)  # URL des generierten Bildes
    prompt_used = db.Column(db.Text, nullable=True)  # Der vollständige Prompt der verwendet wurde
    image_size = db.Column(db.String(20), nullable=True)  # z.B. "1792x1024"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('generated_images', lazy=True))
    
    def to_dict(self):
        """Convert image to dictionary for JSON response"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_input': self.user_input,
            'image_type': self.image_type,
            'image_url': self.image_url,
            'prompt_used': self.prompt_used,
            'image_size': self.image_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<GeneratedImage {self.id}: {self.image_type} for user {self.user_id}>'

