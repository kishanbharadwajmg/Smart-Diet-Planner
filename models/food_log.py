from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from . import db

class FoodLog(db.Model):
    __tablename__ = 'food_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)
    quantity_grams = db.Column(db.Float, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    calories_consumed = db.Column(db.Float, nullable=False)
    protein_consumed = db.Column(db.Float, nullable=False)
    carbs_consumed = db.Column(db.Float, nullable=False)
    fat_consumed = db.Column(db.Float, nullable=False)
    date_logged = db.Column(db.Date, nullable=False, default=date.today)
    time_logged = db.Column(db.Time, default=datetime.now().time)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FoodLog {self.user.username} - {self.food.name}>'
    
    @property
    def fiber_consumed(self):
        """Calculate fiber consumed based on quantity"""
        if self.food:
            return round((self.food.fiber_per_100g * self.quantity_grams) / 100, 1)
        return 0
    
    def to_dict(self):
        """Convert food log to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else 'Unknown',
            'food_name_hindi': self.food.name_hindi if self.food else None,
            'quantity_grams': self.quantity_grams,
            'meal_type': self.meal_type,
            'calories': self.calories_consumed,
            'protein': self.protein_consumed,
            'carbs': self.carbs_consumed,
            'fat': self.fat_consumed,
            'fiber': self.fiber_consumed,
            'date_logged': self.date_logged.isoformat(),
            'time_logged': self.time_logged.strftime('%H:%M:%S'),
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def create_from_food(user_id, food_id, quantity_grams, meal_type, notes=None, log_date=None):
        """Create a food log entry with automatic nutrition calculation"""
        from .food import Food
        
        food = Food.query.get(food_id)
        if not food:
            raise ValueError("Food not found")
        
        # Calculate nutrition values
        nutrition = food.calculate_nutrition(quantity_grams)
        
        # Create food log
        food_log = FoodLog(
            user_id=user_id,
            food_id=food_id,
            quantity_grams=quantity_grams,
            meal_type=meal_type,
            calories_consumed=nutrition['calories'],
            protein_consumed=nutrition['protein'],
            carbs_consumed=nutrition['carbs'],
            fat_consumed=nutrition['fat'],
            date_logged=log_date or date.today(),
            time_logged=datetime.now().time(),
            notes=notes
        )
        
        return food_log
    
    @staticmethod
    def get_user_logs(user_id, start_date=None, end_date=None, meal_type=None):
        """Get food logs for a user with optional filters"""
        query_filter = FoodLog.query.filter_by(user_id=user_id)
        
        if start_date:
            query_filter = query_filter.filter(FoodLog.date_logged >= start_date)
        if end_date:
            query_filter = query_filter.filter(FoodLog.date_logged <= end_date)
        if meal_type:
            query_filter = query_filter.filter_by(meal_type=meal_type)
        
        return query_filter.order_by(FoodLog.date_logged.desc(), FoodLog.time_logged.desc()).all()
    
    @staticmethod
    def get_daily_logs(user_id, log_date=None):
        """Get all food logs for a specific date"""
        if log_date is None:
            log_date = date.today()
        
        return FoodLog.query.filter_by(
            user_id=user_id,
            date_logged=log_date
        ).order_by(FoodLog.time_logged.asc()).all()


class DailySummary(db.Model):
    __tablename__ = 'daily_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_calories = db.Column(db.Float, nullable=False, default=0)
    total_protein = db.Column(db.Float, nullable=False, default=0)
    total_carbs = db.Column(db.Float, nullable=False, default=0)
    total_fat = db.Column(db.Float, nullable=False, default=0)
    calorie_goal = db.Column(db.Float, nullable=False)
    protein_goal = db.Column(db.Float, nullable=False)
    carb_goal = db.Column(db.Float, nullable=False)
    fat_goal = db.Column(db.Float, nullable=False)
    meals_logged = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint on user_id and date
    __table_args__ = (db.UniqueConstraint('user_id', 'date'),)
    
    def __repr__(self):
        return f'<DailySummary {self.user.username} - {self.date}>'
    
    @property
    def calorie_percentage(self):
        """Calculate percentage of calorie goal achieved"""
        if self.calorie_goal == 0:
            return 0
        return round((self.total_calories / self.calorie_goal) * 100, 1)
    
    @property
    def protein_percentage(self):
        """Calculate percentage of protein goal achieved"""
        if self.protein_goal == 0:
            return 0
        return round((self.total_protein / self.protein_goal) * 100, 1)
    
    @property
    def carb_percentage(self):
        """Calculate percentage of carb goal achieved"""
        if self.carb_goal == 0:
            return 0
        return round((self.total_carbs / self.carb_goal) * 100, 1)
    
    @property
    def fat_percentage(self):
        """Calculate percentage of fat goal achieved"""
        if self.fat_goal == 0:
            return 0
        return round((self.total_fat / self.fat_goal) * 100, 1)
    
    @property
    def calories_remaining(self):
        """Calculate remaining calories for the day"""
        return max(0, self.calorie_goal - self.total_calories)
    
    def to_dict(self):
        """Convert daily summary to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'total_calories': self.total_calories,
            'total_protein': self.total_protein,
            'total_carbs': self.total_carbs,
            'total_fat': self.total_fat,
            'calorie_goal': self.calorie_goal,
            'protein_goal': self.protein_goal,
            'carb_goal': self.carb_goal,
            'fat_goal': self.fat_goal,
            'meals_logged': self.meals_logged,
            'calorie_percentage': self.calorie_percentage,
            'protein_percentage': self.protein_percentage,
            'carb_percentage': self.carb_percentage,
            'fat_percentage': self.fat_percentage,
            'calories_remaining': self.calories_remaining,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def get_or_create(user_id, summary_date=None):
        """Get existing daily summary or create a new one"""
        from .user import User
        
        if summary_date is None:
            summary_date = date.today()
        
        summary = DailySummary.query.filter_by(
            user_id=user_id,
            date=summary_date
        ).first()
        
        if not summary:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            summary = DailySummary(
                user_id=user_id,
                date=summary_date,
                calorie_goal=user.daily_calorie_goal or 2000,
                protein_goal=user.protein_goal or 50,
                carb_goal=user.carb_goal or 200,
                fat_goal=user.fat_goal or 65
            )
            db.session.add(summary)
            db.session.commit()
        
        return summary
    
    @staticmethod
    def update_from_logs(user_id, summary_date=None):
        """Update daily summary based on food logs"""
        if summary_date is None:
            summary_date = date.today()
        
        # Get or create summary
        summary = DailySummary.get_or_create(user_id, summary_date)
        
        # Get all food logs for the date
        logs = FoodLog.query.filter_by(
            user_id=user_id,
            date_logged=summary_date
        ).all()
        
        # Calculate totals
        total_calories = sum(log.calories_consumed for log in logs)
        total_protein = sum(log.protein_consumed for log in logs)
        total_carbs = sum(log.carbs_consumed for log in logs)
        total_fat = sum(log.fat_consumed for log in logs)
        
        # Update summary
        summary.total_calories = round(total_calories, 1)
        summary.total_protein = round(total_protein, 1)
        summary.total_carbs = round(total_carbs, 1)
        summary.total_fat = round(total_fat, 1)
        summary.meals_logged = len(logs)
        summary.updated_at = datetime.utcnow()
        
        db.session.commit()
        return summary
    
    @staticmethod
    def get_weekly_summary(user_id, start_date=None):
        """Get weekly summary data for charts"""
        from datetime import timedelta
        
        if start_date is None:
            start_date = date.today() - timedelta(days=6)  # Last 7 days
        
        end_date = start_date + timedelta(days=6)
        
        summaries = DailySummary.query.filter(
            DailySummary.user_id == user_id,
            DailySummary.date >= start_date,
            DailySummary.date <= end_date
        ).order_by(DailySummary.date.asc()).all()
        
        return summaries