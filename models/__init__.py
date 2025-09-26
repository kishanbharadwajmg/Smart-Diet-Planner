from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to make them available when this module is imported
from .user import User
from .food import Food
from .food_log import FoodLog, DailySummary
from .user_preferences import UserPreference

__all__ = ['db', 'User', 'Food', 'FoodLog', 'DailySummary', 'UserPreference']