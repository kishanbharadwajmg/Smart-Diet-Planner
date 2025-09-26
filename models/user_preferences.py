from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    preference_type = db.Column(db.String(50), nullable=False)
    preference_value = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreference {self.user.username} - {self.preference_type}: {self.preference_value}>'
    
    def to_dict(self):
        """Convert user preference to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preference_type': self.preference_type,
            'preference_value': self.preference_value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def get_user_preferences(user_id, preference_type=None):
        """Get all preferences for a user"""
        query_filter = UserPreference.query.filter_by(
            user_id=user_id,
            is_active=True
        )
        
        if preference_type:
            query_filter = query_filter.filter_by(preference_type=preference_type)
        
        return query_filter.all()
    
    @staticmethod
    def add_preference(user_id, preference_type, preference_value):
        """Add a new preference for a user"""
        # Check if preference already exists
        existing = UserPreference.query.filter_by(
            user_id=user_id,
            preference_type=preference_type,
            preference_value=preference_value,
            is_active=True
        ).first()
        
        if existing:
            return existing
        
        preference = UserPreference(
            user_id=user_id,
            preference_type=preference_type,
            preference_value=preference_value
        )
        
        db.session.add(preference)
        db.session.commit()
        return preference
    
    @staticmethod
    def remove_preference(user_id, preference_type, preference_value):
        """Remove a preference (soft delete by setting is_active=False)"""
        preference = UserPreference.query.filter_by(
            user_id=user_id,
            preference_type=preference_type,
            preference_value=preference_value,
            is_active=True
        ).first()
        
        if preference:
            preference.is_active = False
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def get_allergies(user_id):
        """Get user's food allergies"""
        preferences = UserPreference.get_user_preferences(user_id, 'allergy')
        return [pref.preference_value for pref in preferences]
    
    @staticmethod
    def get_dislikes(user_id):
        """Get user's food dislikes"""
        preferences = UserPreference.get_user_preferences(user_id, 'dislike')
        return [pref.preference_value for pref in preferences]
    
    @staticmethod
    def get_medical_restrictions(user_id):
        """Get user's medical dietary restrictions"""
        preferences = UserPreference.get_user_preferences(user_id, 'medical')
        return [pref.preference_value for pref in preferences]
    
    @staticmethod
    def bulk_add_preferences(user_id, preference_type, preference_values):
        """Add multiple preferences at once"""
        added_preferences = []
        
        for value in preference_values:
            if value.strip():  # Only add non-empty values
                pref = UserPreference.add_preference(user_id, preference_type, value.strip())
                added_preferences.append(pref)
        
        return added_preferences