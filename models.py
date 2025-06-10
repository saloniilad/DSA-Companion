from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    
    # Relationship with DSA questions
    questions = db.relationship('DSAQuestion', backref='author', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username
    
    def __repr__(self):
        return f'<User {self.username}>'

class DSAQuestion(db.Model):
    """Model for storing DSA questions with multiple approaches"""
    
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(100), nullable=False)
    question_name = db.Column(db.String(200), nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)  # Easy, Medium, Hard
    question_link = db.Column(db.String(500), nullable=True)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Approach 1 (required)
    approach1_description = db.Column(db.Text, nullable=False)
    approach1_time_complexity = db.Column(db.String(50), nullable=False)
    
    # Approach 2 (optional)
    approach2_description = db.Column(db.Text, nullable=True)
    approach2_time_complexity = db.Column(db.String(50), nullable=True)
    
    # Approach 3 (optional)
    approach3_description = db.Column(db.Text, nullable=True)
    approach3_time_complexity = db.Column(db.String(50), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DSAQuestion {self.question_name}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'topic_name': self.topic_name,
            'question_name': self.question_name,
            'difficulty_level': self.difficulty_level,
            'question_link': self.question_link,
            'approach1_description': self.approach1_description,
            'approach1_time_complexity': self.approach1_time_complexity,
            'approach2_description': self.approach2_description,
            'approach2_time_complexity': self.approach2_time_complexity,
            'approach3_description': self.approach3_description,
            'approach3_time_complexity': self.approach3_time_complexity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
