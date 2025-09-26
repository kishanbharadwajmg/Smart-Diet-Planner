from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db

class Food(db.Model):
    __tablename__ = 'foods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_hindi = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False)
    food_type = db.Column(db.String(20), nullable=False, default='Vegetarian')
    calories_per_100g = db.Column(db.Float, nullable=False)
    protein_per_100g = db.Column(db.Float, nullable=False)
    carbs_per_100g = db.Column(db.Float, nullable=False)
    fat_per_100g = db.Column(db.Float, nullable=False)
    fiber_per_100g = db.Column(db.Float, nullable=False, default=0)
    gi_index = db.Column(db.Integer)  # Glycemic Index
    description = db.Column(db.Text)
    serving_size_grams = db.Column(db.Float, default=100)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    food_logs = db.relationship('FoodLog', backref='food', lazy='dynamic')
    
    def __repr__(self):
        return f'<Food {self.name}>'
    
    def calculate_nutrition(self, quantity_grams):
        """Calculate nutrition values for a specific quantity"""
        multiplier = quantity_grams / 100
        
        return {
            'calories': round(self.calories_per_100g * multiplier, 1),
            'protein': round(self.protein_per_100g * multiplier, 1),
            'carbs': round(self.carbs_per_100g * multiplier, 1),
            'fat': round(self.fat_per_100g * multiplier, 1),
            'fiber': round(self.fiber_per_100g * multiplier, 1)
        }
    
    def is_suitable_for_diabetic(self):
        """Check if food is suitable for diabetic users (low GI)"""
        if self.gi_index is None:
            return True  # Unknown GI, assume safe
        return self.gi_index <= 55  # Low GI threshold
    
    def is_suitable_for_user(self, user):
        """Check if food is suitable for a specific user's preferences"""
        from .user import User
        
        # Check food type preference
        if user.food_preferences == 'Vegetarian' and self.food_type != 'Vegetarian':
            return False
        elif user.food_preferences == 'Eggetarian' and self.food_type == 'Non-Vegetarian':
            return False
        
        # Check diabetic requirements
        if user.is_diabetic and not self.is_suitable_for_diabetic():
            return False
        
        # Check disliked foods
        disliked = user.get_disliked_foods()
        if self.id in disliked:
            return False
        
        return True
    
    def get_gi_category(self):
        """Get glycemic index category"""
        if self.gi_index is None:
            return 'Unknown'
        elif self.gi_index <= 55:
            return 'Low'
        elif self.gi_index <= 70:
            return 'Medium'
        else:
            return 'High'
    
    def get_nutrition_density(self):
        """Calculate nutrition density score (protein per calorie)"""
        if self.calories_per_100g == 0:
            return 0
        return round((self.protein_per_100g / self.calories_per_100g) * 100, 2)
    
    def get_serving_units(self):
        """Get appropriate serving units and base weight per unit for this food item"""
        name_lower = self.name.lower()
        
        # Define serving units based on food type
        # Format: {'unit': 'piece', 'grams_per_unit': 30, 'common_quantities': [1, 2, 3, 4]}
        
        # Idli, Dosa, Vada - piece based
        if any(word in name_lower for word in ['idli', 'dosa', 'vada', 'uttapam', 'dhokla', 'khandvi']):
            return {
                'unit': 'piece',
                'grams_per_unit': 30,
                'common_quantities': [1, 2, 3, 4, 5, 6]
            }
        
        # Rice, Biryani - cup/bowl based  
        elif any(word in name_lower for word in ['rice', 'biryani', 'pulao', 'kheer', 'pongal']):
            return {
                'unit': 'cup',
                'grams_per_unit': 150,
                'common_quantities': [0.5, 1, 1.5, 2]
            }
        
        # Dal, Curry, Sabzi - bowl/cup based
        elif any(word in name_lower for word in ['dal', 'curry', 'sabzi', 'sambar', 'rasam', 'kadhi']):
            return {
                'unit': 'cup',
                'grams_per_unit': 200,
                'common_quantities': [0.5, 1, 1.5, 2]
            }
        
        # Roti, Chapati, Naan - piece based
        elif any(word in name_lower for word in ['roti', 'chapati', 'naan', 'paratha', 'puri', 'kulcha']):
            return {
                'unit': 'piece',
                'grams_per_unit': 40,
                'common_quantities': [1, 2, 3, 4, 5, 6]
            }
        
        # Sweets - piece/small serving based
        elif any(word in name_lower for word in ['laddu', 'halwa', 'burfi', 'gulab jamun', 'rasgulla', 'sweet']):
            return {
                'unit': 'piece',
                'grams_per_unit': 25,
                'common_quantities': [1, 2, 3, 4, 5, 6]
            }
        
        # Snacks - piece/small portion based
        elif any(word in name_lower for word in ['samosa', 'pakora', 'bhel', 'chat', 'namkeen']):
            return {
                'unit': 'piece',
                'grams_per_unit': 20,
                'common_quantities': [1, 2, 3, 4, 5, 10]
            }
        
        # Beverages - cup/glass based
        elif any(word in name_lower for word in ['tea', 'coffee', 'juice', 'milk', 'drink']):
            return {
                'unit': 'cup',
                'grams_per_unit': 150,
                'common_quantities': [1, 1.5, 2, 2.5, 3]
            }
        
        # Vegetables - portion based
        elif self.category == 'Vegetables':
            return {
                'unit': 'cup',
                'grams_per_unit': 150,
                'common_quantities': [0.5, 1, 1.5, 2]
            }
        
        # Fruits - piece/portion based  
        elif self.category == 'Fruits':
            return {
                'unit': 'piece',
                'grams_per_unit': 100,
                'common_quantities': [0.5, 1, 1.5, 2, 3]
            }
        
        # Default - grams
        return {
            'unit': 'grams',
            'grams_per_unit': 1,
            'common_quantities': [50, 100, 150, 200, 250]
        }
    
    def to_dict(self, include_detailed=False):
        """Convert food to dictionary for API responses"""
        basic_dict = {
            'id': self.id,
            'name': self.name,
            'name_hindi': self.name_hindi,
            'category': self.category,
            'food_type': self.food_type,
            'calories_per_100g': self.calories_per_100g,
            'protein_per_100g': self.protein_per_100g,
            'carbs_per_100g': self.carbs_per_100g,
            'fat_per_100g': self.fat_per_100g,
            'serving_size_grams': self.serving_size_grams,
            'is_active': self.is_active,
            'serving_units': self.get_serving_units()
        }
        
        if include_detailed:
            basic_dict.update({
                'fiber_per_100g': self.fiber_per_100g,
                'gi_index': self.gi_index,
                'gi_category': self.get_gi_category(),
                'description': self.description,
                'nutrition_density': self.get_nutrition_density(),
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            })
        
        return basic_dict
    
    @staticmethod
    def search(query, user=None, category=None, food_type=None, limit=20):
        """Search foods with filters"""
        query_filter = Food.query.filter(Food.is_active == True)
        
        # Text search
        if query:
            search_term = f'%{query}%'
            query_filter = query_filter.filter(
                db.or_(
                    Food.name.ilike(search_term),
                    Food.name_hindi.ilike(search_term),
                    Food.category.ilike(search_term),
                    Food.description.ilike(search_term)
                )
            )
        
        # Category filter
        if category:
            query_filter = query_filter.filter(Food.category == category)
        
        # Food type filter
        if food_type:
            query_filter = query_filter.filter(Food.food_type == food_type)
        
        # Get results
        foods = query_filter.order_by(Food.name).limit(limit).all()
        
        # Filter by user preferences if user provided
        if user:
            foods = [food for food in foods if food.is_suitable_for_user(user)]
        
        return foods
    
    @staticmethod
    def get_categories():
        """Get all food categories"""
        categories = db.session.query(Food.category.distinct()).filter(
            Food.is_active == True
        ).all()
        return [category[0] for category in categories]
    
    @staticmethod
    def get_food_types():
        """Get all food types"""
        return ['Vegetarian', 'Non-Vegetarian', 'Eggetarian']
    
    @staticmethod
    def get_recommended_for_user(user, meal_type=None, limit=10):
        """Get recommended foods for a user based on their profile with South Indian preference"""
        # Base query for suitable foods
        query_filter = Food.query.filter(Food.is_active == True)
        
        # Filter by food type preference
        if user.food_preferences == 'Vegetarian':
            query_filter = query_filter.filter(Food.food_type == 'Vegetarian')
        elif user.food_preferences == 'Eggetarian':
            query_filter = query_filter.filter(Food.food_type.in_(['Vegetarian', 'Eggetarian']))
        
        # Filter for diabetic users (low GI foods)
        if user.is_diabetic:
            query_filter = query_filter.filter(
                db.or_(Food.gi_index == None, Food.gi_index <= 55)
            )
        
        # Exclude disliked foods
        disliked = user.get_disliked_foods()
        if disliked:
            query_filter = query_filter.filter(~Food.id.in_(disliked))
        
        # Meal-specific recommendations
        if meal_type:
            if meal_type.lower() in ['breakfast', 'mid-morning']:
                # Prefer high fiber, moderate protein foods for breakfast
                query_filter = query_filter.filter(Food.fiber_per_100g >= 1.5)
            elif meal_type.lower() in ['lunch', 'dinner']:
                # Prefer balanced macro foods for main meals
                query_filter = query_filter.filter(Food.protein_per_100g >= 3)
            elif meal_type.lower() in ['evening snack', 'late night']:
                # Prefer lighter, low-calorie foods for snacks
                query_filter = query_filter.filter(Food.calories_per_100g <= 250)
        
        # Prioritize South Indian foods and traditional Indian foods
        # Get South Indian foods first
        south_indian_foods = query_filter.filter(
            db.or_(
                Food.category == 'South Indian',
                Food.category == 'Dal & Lentils',
                Food.category == 'Rice & Grains',
                Food.category == 'Vegetables'
            )
        ).order_by(
            # Prioritize South Indian category first
            db.case(
                (Food.category == 'South Indian', 1),
                (Food.category == 'Dal & Lentils', 2),
                (Food.category == 'Rice & Grains', 3),
                (Food.category == 'Vegetables', 4),
                else_=5
            ).asc(),
            # Then by nutrition density
            (Food.protein_per_100g / Food.calories_per_100g).desc()
        ).limit(limit).all()
        
        # If we don't have enough South Indian foods, fill with other suitable foods
        if len(south_indian_foods) < limit:
            remaining_limit = limit - len(south_indian_foods)
            other_foods = query_filter.filter(
                ~Food.category.in_(['South Indian', 'Dal & Lentils', 'Rice & Grains', 'Vegetables'])
            ).order_by(
                (Food.protein_per_100g / Food.calories_per_100g).desc()
            ).limit(remaining_limit).all()
            
            south_indian_foods.extend(other_foods)
        
        return south_indian_foods