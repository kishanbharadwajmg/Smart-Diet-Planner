from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Float, nullable=False)  # in cm
    weight = db.Column(db.Float, nullable=False)  # in kg
    activity_level = db.Column(db.String(20), nullable=False, default='Sedentary')
    food_preferences = db.Column(db.String(20), nullable=False, default='Vegetarian')
    is_diabetic = db.Column(db.Boolean, nullable=False, default=False)
    disliked_foods = db.Column(db.Text)  # JSON array of food IDs
    daily_calorie_goal = db.Column(db.Float)
    protein_goal = db.Column(db.Float)
    carb_goal = db.Column(db.Float)
    fat_goal = db.Column(db.Float)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    food_logs = db.relationship('FoodLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    daily_summaries = db.relationship('DailySummary', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_disliked_foods(self):
        """Get list of disliked food IDs"""
        if not self.disliked_foods:
            return []
        try:
            return json.loads(self.disliked_foods)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_disliked_foods(self, food_ids):
        """Set disliked foods as JSON"""
        if isinstance(food_ids, list):
            self.disliked_foods = json.dumps(food_ids)
        else:
            self.disliked_foods = json.dumps([])
    
    def calculate_bmr(self):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if self.gender.lower() == 'male':
            # BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
        else:
            # BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161
        return bmr
    
    def calculate_tdee(self):
        """Calculate Total Daily Energy Expenditure"""
        bmr = self.calculate_bmr()
        
        # Activity multipliers
        activity_multipliers = {
            'Sedentary': 1.2,
            'Lightly Active': 1.375,
            'Moderately Active': 1.55,
            'Very Active': 1.725,
            'Extremely Active': 1.9
        }
        
        multiplier = activity_multipliers.get(self.activity_level, 1.2)
        tdee = bmr * multiplier
        return tdee
    
    def calculate_macro_goals(self, calorie_goal=None):
        """Calculate protein, carb, and fat goals based on calories"""
        if calorie_goal is None:
            calorie_goal = self.daily_calorie_goal or self.calculate_tdee()
        
        # Standard macro ratios (adjustable)
        protein_ratio = 0.25  # 25% of calories from protein
        carb_ratio = 0.45     # 45% of calories from carbs
        fat_ratio = 0.30      # 30% of calories from fat
        
        # Calculate grams (protein = 4 cal/g, carbs = 4 cal/g, fat = 9 cal/g)
        protein_grams = (calorie_goal * protein_ratio) / 4
        carb_grams = (calorie_goal * carb_ratio) / 4
        fat_grams = (calorie_goal * fat_ratio) / 9
        
        return {
            'protein': round(protein_grams, 1),
            'carbs': round(carb_grams, 1),
            'fat': round(fat_grams, 1)
        }
    
    def update_goals(self):
        """Update calorie and macro goals based on current stats"""
        self.daily_calorie_goal = round(self.calculate_tdee(), 0)
        macro_goals = self.calculate_macro_goals()
        self.protein_goal = macro_goals['protein']
        self.carb_goal = macro_goals['carbs']
        self.fat_goal = macro_goals['fat']
        self.updated_at = datetime.utcnow()
    
    def get_bmi(self):
        """Calculate Body Mass Index"""
        height_m = self.height / 100  # Convert cm to meters
        bmi = self.weight / (height_m ** 2)
        return round(bmi, 1)
    
    def get_bmi_category(self):
        """Get BMI category"""
        bmi = self.get_bmi()
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal weight'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
    
    def get_today_summary(self, date=None):
        """Get daily summary for a specific date (default: today)"""
        if date is None:
            date = datetime.utcnow().date()
        
        from .food_log import DailySummary
        return DailySummary.query.filter_by(
            user_id=self.id,
            date=date
        ).first()
    
    def get_calorie_progress(self, date=None):
        """Get calorie progress for a specific date"""
        summary = self.get_today_summary(date)
        if not summary:
            return {
                'consumed': 0,
                'goal': self.daily_calorie_goal or 2000,
                'remaining': self.daily_calorie_goal or 2000,
                'percentage': 0
            }
        
        remaining = max(0, summary.calorie_goal - summary.total_calories)
        percentage = (summary.total_calories / summary.calorie_goal) * 100 if summary.calorie_goal > 0 else 0
        
        return {
            'consumed': round(summary.total_calories, 1),
            'goal': summary.calorie_goal,
            'remaining': round(remaining, 1),
            'percentage': round(percentage, 1)
        }
    
    def get_macro_progress(self, date=None):
        """Get macro progress for a specific date"""
        summary = self.get_today_summary(date)
        if not summary:
            return {
                'protein': {'consumed': 0, 'goal': self.protein_goal or 50, 'percentage': 0},
                'carbs': {'consumed': 0, 'goal': self.carb_goal or 200, 'percentage': 0},
                'fat': {'consumed': 0, 'goal': self.fat_goal or 65, 'percentage': 0}
            }
        
        progress = {}
        macros = ['protein', 'carbs', 'fat']
        
        for macro in macros:
            consumed = getattr(summary, f'total_{macro}', 0)
            goal = getattr(summary, f'{macro}_goal', 0)
            percentage = (consumed / goal) * 100 if goal > 0 else 0
            
            progress[macro] = {
                'consumed': round(consumed, 1),
                'goal': goal,
                'percentage': round(percentage, 1)
            }
        
        return progress
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f'{self.first_name} {self.last_name}',
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'activity_level': self.activity_level,
            'food_preferences': self.food_preferences,
            'is_diabetic': self.is_diabetic,
            'daily_calorie_goal': self.daily_calorie_goal,
            'protein_goal': self.protein_goal,
            'carb_goal': self.carb_goal,
            'fat_goal': self.fat_goal,
            'bmr': round(self.calculate_bmr(), 0),
            'tdee': round(self.calculate_tdee(), 0),
            'bmi': self.get_bmi(),
            'bmi_category': self.get_bmi_category(),
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }