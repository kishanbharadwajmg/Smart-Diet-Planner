"""
Seed data for Smart Diet Planner - Indian Food Database
This script populates the database with comprehensive Indian food items
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Food
from app import create_app

# Indian food data with nutritional information
INDIAN_FOODS = [
    # Rice and Grains
    {
        'name': 'Basmati Rice (cooked)',
        'name_hindi': 'बासमती चावल',
        'category': 'Rice & Grains',
        'food_type': 'Vegetarian',
        'calories_per_100g': 130,
        'protein_per_100g': 2.7,
        'carbs_per_100g': 28.2,
        'fat_per_100g': 0.3,
        'fiber_per_100g': 0.4,
        'gi_index': 58,
        'description': 'Long grain aromatic rice, staple food',
        'serving_size_grams': 150
    },
    {
        'name': 'Brown Rice (cooked)',
        'name_hindi': 'ब्राउन चावल',
        'category': 'Rice & Grains',
        'food_type': 'Vegetarian',
        'calories_per_100g': 112,
        'protein_per_100g': 2.3,
        'carbs_per_100g': 22.9,
        'fat_per_100g': 0.9,
        'fiber_per_100g': 1.8,
        'gi_index': 50,
        'description': 'Whole grain brown rice',
        'serving_size_grams': 150
    },
    {
        'name': 'Jeera Rice',
        'name_hindi': 'जीरा चावल',
        'category': 'Rice & Grains',
        'food_type': 'Vegetarian',
        'calories_per_100g': 142,
        'protein_per_100g': 2.8,
        'carbs_per_100g': 28.5,
        'fat_per_100g': 1.2,
        'fiber_per_100g': 0.5,
        'gi_index': 60,
        'description': 'Cumin flavored rice',
        'serving_size_grams': 150
    },
    {
        'name': 'Biryani (Chicken)',
        'name_hindi': 'चिकन बिरयानी',
        'category': 'Rice & Grains',
        'food_type': 'Non-Vegetarian',
        'calories_per_100g': 165,
        'protein_per_100g': 8.2,
        'carbs_per_100g': 22.1,
        'fat_per_100g': 4.3,
        'fiber_per_100g': 0.8,
        'gi_index': 45,
        'description': 'Aromatic rice with chicken and spices',
        'serving_size_grams': 200
    },
    {
        'name': 'Vegetable Biryani',
        'name_hindi': 'सब्जी बिरयानी',
        'category': 'Rice & Grains',
        'food_type': 'Vegetarian',
        'calories_per_100g': 145,
        'protein_per_100g': 3.8,
        'carbs_per_100g': 25.2,
        'fat_per_100g': 3.1,
        'fiber_per_100g': 2.1,
        'gi_index': 50,
        'description': 'Aromatic rice with mixed vegetables',
        'serving_size_grams': 200
    },

    # Dal and Lentils
    {
        'name': 'Dal Tadka',
        'name_hindi': 'दाल तड़का',
        'category': 'Dal & Lentils',
        'food_type': 'Vegetarian',
        'calories_per_100g': 108,
        'protein_per_100g': 7.6,
        'carbs_per_100g': 15.2,
        'fat_per_100g': 1.8,
        'fiber_per_100g': 4.2,
        'gi_index': 35,
        'description': 'Tempered yellow lentils',
        'serving_size_grams': 150
    },
    {
        'name': 'Dal Makhani',
        'name_hindi': 'दाल मखनी',
        'category': 'Dal & Lentils',
        'food_type': 'Vegetarian',
        'calories_per_100g': 142,
        'protein_per_100g': 8.1,
        'carbs_per_100g': 12.8,
        'fat_per_100g': 6.7,
        'fiber_per_100g': 3.8,
        'gi_index': 30,
        'description': 'Creamy black lentils with butter',
        'serving_size_grams': 150
    },
    {
        'name': 'Masoor Dal',
        'name_hindi': 'मसूर दाल',
        'category': 'Dal & Lentils',
        'food_type': 'Vegetarian',
        'calories_per_100g': 98,
        'protein_per_100g': 8.9,
        'carbs_per_100g': 13.1,
        'fat_per_100g': 0.8,
        'fiber_per_100g': 4.9,
        'gi_index': 25,
        'description': 'Red lentil curry',
        'serving_size_grams': 150
    },
    {
        'name': 'Chana Dal',
        'name_hindi': 'चना दाल',
        'category': 'Dal & Lentils',
        'food_type': 'Vegetarian',
        'calories_per_100g': 115,
        'protein_per_100g': 9.2,
        'carbs_per_100g': 16.8,
        'fat_per_100g': 1.2,
        'fiber_per_100g': 5.1,
        'gi_index': 33,
        'description': 'Split chickpea lentils',
        'serving_size_grams': 150
    },
    {
        'name': 'Rajma',
        'name_hindi': 'राजमा',
        'category': 'Dal & Lentils',
        'food_type': 'Vegetarian',
        'calories_per_100g': 127,
        'protein_per_100g': 8.7,
        'carbs_per_100g': 22.8,
        'fat_per_100g': 0.5,
        'fiber_per_100g': 6.4,
        'gi_index': 29,
        'description': 'Kidney beans curry',
        'serving_size_grams': 150
    },

    # Vegetables
    {
        'name': 'Aloo Gobi',
        'name_hindi': 'आलू गोभी',
        'category': 'Vegetables',
        'food_type': 'Vegetarian',
        'calories_per_100g': 89,
        'protein_per_100g': 2.8,
        'carbs_per_100g': 13.2,
        'fat_per_100g': 3.1,
        'fiber_per_100g': 2.8,
        'gi_index': 55,
        'description': 'Potato and cauliflower curry',
        'serving_size_grams': 100
    },
    {
        'name': 'Palak Paneer',
        'name_hindi': 'पालक पनीर',
        'category': 'Vegetables',
        'food_type': 'Vegetarian',
        'calories_per_100g': 118,
        'protein_per_100g': 7.2,
        'carbs_per_100g': 5.8,
        'fat_per_100g': 8.1,
        'fiber_per_100g': 2.9,
        'gi_index': 15,
        'description': 'Spinach with cottage cheese',
        'serving_size_grams': 100
    },
    {
        'name': 'Baingan Bharta',
        'name_hindi': 'बैगन भरता',
        'category': 'Vegetables',
        'food_type': 'Vegetarian',
        'calories_per_100g': 67,
        'protein_per_100g': 1.8,
        'carbs_per_100g': 7.2,
        'fat_per_100g': 3.8,
        'fiber_per_100g': 3.4,
        'gi_index': 20,
        'description': 'Roasted eggplant mash',
        'serving_size_grams': 100
    },
    {
        'name': 'Bhindi Masala',
        'name_hindi': 'भिंडी मसाला',
        'category': 'Vegetables',
        'food_type': 'Vegetarian',
        'calories_per_100g': 79,
        'protein_per_100g': 2.1,
        'carbs_per_100g': 7.8,
        'fat_per_100g': 4.6,
        'fiber_per_100g': 3.2,
        'gi_index': 20,
        'description': 'Spiced okra curry',
        'serving_size_grams': 100
    },
    {
        'name': 'Mixed Vegetable Curry',
        'name_hindi': 'मिक्स सब्जी',
        'category': 'Vegetables',
        'food_type': 'Vegetarian',
        'calories_per_100g': 72,
        'protein_per_100g': 2.4,
        'carbs_per_100g': 9.8,
        'fat_per_100g': 2.8,
        'fiber_per_100g': 3.1,
        'gi_index': 25,
        'description': 'Mixed seasonal vegetables',
        'serving_size_grams': 100
    },

    # Non-Vegetarian
    {
        'name': 'Chicken Curry',
        'name_hindi': 'चिकन करी',
        'category': 'Non-Vegetarian',
        'food_type': 'Non-Vegetarian',
        'calories_per_100g': 165,
        'protein_per_100g': 18.6,
        'carbs_per_100g': 4.2,
        'fat_per_100g': 8.1,
        'fiber_per_100g': 1.2,
        'gi_index': 10,
        'description': 'Traditional chicken curry',
        'serving_size_grams': 150
    },
    {
        'name': 'Chicken Tandoori',
        'name_hindi': 'तंदूरी चिकन',
        'category': 'Non-Vegetarian',
        'food_type': 'Non-Vegetarian',
        'calories_per_100g': 189,
        'protein_per_100g': 27.6,
        'carbs_per_100g': 1.8,
        'fat_per_100g': 7.8,
        'fiber_per_100g': 0.5,
        'gi_index': 5,
        'description': 'Tandoor grilled chicken',
        'serving_size_grams': 150
    },
    {
        'name': 'Mutton Curry',
        'name_hindi': 'मटन करी',
        'category': 'Non-Vegetarian',
        'food_type': 'Non-Vegetarian',
        'calories_per_100g': 217,
        'protein_per_100g': 18.2,
        'carbs_per_100g': 3.8,
        'fat_per_100g': 14.1,
        'fiber_per_100g': 0.8,
        'gi_index': 8,
        'description': 'Spiced goat meat curry',
        'serving_size_grams': 150
    },
    {
        'name': 'Fish Curry',
        'name_hindi': 'मछली करी',
        'category': 'Non-Vegetarian',
        'food_type': 'Non-Vegetarian',
        'calories_per_100g': 136,
        'protein_per_100g': 20.3,
        'carbs_per_100g': 3.1,
        'fat_per_100g': 4.8,
        'fiber_per_100g': 0.9,
        'gi_index': 5,
        'description': 'Traditional fish curry',
        'serving_size_grams': 150
    },
    {
        'name': 'Butter Chicken',
        'name_hindi': 'बटर चिकन',
        'category': 'Non-Vegetarian',
        'food_type': 'Non-Vegetarian',
        'calories_per_100g': 198,
        'protein_per_100g': 16.8,
        'carbs_per_100g': 6.2,
        'fat_per_100g': 12.1,
        'fiber_per_100g': 1.1,
        'gi_index': 15,
        'description': 'Creamy tomato-based chicken curry',
        'serving_size_grams': 150
    },

    # Egg Items
    {
        'name': 'Boiled Egg',
        'name_hindi': 'उबला अंडा',
        'category': 'Eggs',
        'food_type': 'Eggetarian',
        'calories_per_100g': 155,
        'protein_per_100g': 13.0,
        'carbs_per_100g': 1.1,
        'fat_per_100g': 10.6,
        'fiber_per_100g': 0.0,
        'gi_index': 0,
        'description': 'Hard boiled chicken egg',
        'serving_size_grams': 50
    },
    {
        'name': 'Egg Curry',
        'name_hindi': 'अंडा करी',
        'category': 'Eggs',
        'food_type': 'Eggetarian',
        'calories_per_100g': 142,
        'protein_per_100g': 9.8,
        'carbs_per_100g': 4.2,
        'fat_per_100g': 9.6,
        'fiber_per_100g': 1.1,
        'gi_index': 15,
        'description': 'Spiced egg curry',
        'serving_size_grams': 100
    },
    {
        'name': 'Masala Omelette',
        'name_hindi': 'मसाला ऑमलेट',
        'category': 'Eggs',
        'food_type': 'Eggetarian',
        'calories_per_100g': 178,
        'protein_per_100g': 12.8,
        'carbs_per_100g': 2.8,
        'fat_per_100g': 13.1,
        'fiber_per_100g': 0.8,
        'gi_index': 5,
        'description': 'Spiced Indian style omelette',
        'serving_size_grams': 100
    },

    # Bread and Rotis
    {
        'name': 'Chapati/Roti',
        'name_hindi': 'चपाती/रोटी',
        'category': 'Bread & Rotis',
        'food_type': 'Vegetarian',
        'calories_per_100g': 297,
        'protein_per_100g': 10.7,
        'carbs_per_100g': 58.6,
        'fat_per_100g': 3.7,
        'fiber_per_100g': 10.7,
        'gi_index': 62,
        'description': 'Whole wheat flatbread',
        'serving_size_grams': 30
    },
    {
        'name': 'Naan',
        'name_hindi': 'नान',
        'category': 'Bread & Rotis',
        'food_type': 'Vegetarian',
        'calories_per_100g': 310,
        'protein_per_100g': 9.1,
        'carbs_per_100g': 56.8,
        'fat_per_100g': 5.4,
        'fiber_per_100g': 2.7,
        'gi_index': 71,
        'description': 'Leavened flatbread',
        'serving_size_grams': 60
    },
    {
        'name': 'Paratha (Plain)',
        'name_hindi': 'पराठा',
        'category': 'Bread & Rotis',
        'food_type': 'Vegetarian',
        'calories_per_100g': 320,
        'protein_per_100g': 8.8,
        'carbs_per_100g': 52.3,
        'fat_per_100g': 8.9,
        'fiber_per_100g': 4.2,
        'gi_index': 65,
        'description': 'Layered flatbread with ghee',
        'serving_size_grams': 50
    },
    {
        'name': 'Aloo Paratha',
        'name_hindi': 'आलू पराठा',
        'category': 'Bread & Rotis',
        'food_type': 'Vegetarian',
        'calories_per_100g': 289,
        'protein_per_100g': 7.2,
        'carbs_per_100g': 48.1,
        'fat_per_100g': 7.8,
        'fiber_per_100g': 4.8,
        'gi_index': 68,
        'description': 'Potato stuffed flatbread',
        'serving_size_grams': 80
    },
    {
        'name': 'Puri',
        'name_hindi': 'पूरी',
        'category': 'Bread & Rotis',
        'food_type': 'Vegetarian',
        'calories_per_100g': 501,
        'protein_per_100g': 9.9,
        'carbs_per_100g': 45.1,
        'fat_per_100g': 31.2,
        'fiber_per_100g': 1.8,
        'gi_index': 75,
        'description': 'Deep fried puffed bread',
        'serving_size_grams': 15
    },

    # Snacks and Appetizers
    {
        'name': 'Samosa',
        'name_hindi': 'समोसा',
        'category': 'Snacks',
        'food_type': 'Vegetarian',
        'calories_per_100g': 308,
        'protein_per_100g': 5.2,
        'carbs_per_100g': 32.1,
        'fat_per_100g': 17.8,
        'fiber_per_100g': 3.1,
        'gi_index': 55,
        'description': 'Deep fried triangular pastry with filling',
        'serving_size_grams': 50
    },
    {
        'name': 'Pakora',
        'name_hindi': 'पकौड़ा',
        'category': 'Snacks',
        'food_type': 'Vegetarian',
        'calories_per_100g': 287,
        'protein_per_100g': 8.9,
        'carbs_per_100g': 28.2,
        'fat_per_100g': 16.1,
        'fiber_per_100g': 4.2,
        'gi_index': 50,
        'description': 'Deep fried vegetable fritters',
        'serving_size_grams': 30
    },
    {
        'name': 'Dhokla',
        'name_hindi': 'ढोकला',
        'category': 'Snacks',
        'food_type': 'Vegetarian',
        'calories_per_100g': 160,
        'protein_per_100g': 6.8,
        'carbs_per_100g': 25.2,
        'fat_per_100g': 3.8,
        'fiber_per_100g': 2.1,
        'gi_index': 35,
        'description': 'Steamed chickpea flour cake',
        'serving_size_grams': 50
    },
    {
        'name': 'Aloo Tikki',
        'name_hindi': 'आलू टिक्की',
        'category': 'Snacks',
        'food_type': 'Vegetarian',
        'calories_per_100g': 195,
        'protein_per_100g': 3.8,
        'carbs_per_100g': 28.9,
        'fat_per_100g': 7.2,
        'fiber_per_100g': 2.8,
        'gi_index': 62,
        'description': 'Shallow fried potato patties',
        'serving_size_grams': 60
    },
    {
        'name': 'Chaat',
        'name_hindi': 'चाट',
        'category': 'Snacks',
        'food_type': 'Vegetarian',
        'calories_per_100g': 142,
        'protein_per_100g': 4.1,
        'carbs_per_100g': 22.8,
        'fat_per_100g': 4.2,
        'fiber_per_100g': 3.8,
        'gi_index': 45,
        'description': 'Mixed savory snack',
        'serving_size_grams': 100
    },

    # Sweets and Desserts
    {
        'name': 'Gulab Jamun',
        'name_hindi': 'गुलाब जामुन',
        'category': 'Sweets',
        'food_type': 'Vegetarian',
        'calories_per_100g': 387,
        'protein_per_100g': 6.2,
        'carbs_per_100g': 52.8,
        'fat_per_100g': 16.8,
        'fiber_per_100g': 0.8,
        'gi_index': 85,
        'description': 'Sweet milk dumplings in syrup',
        'serving_size_grams': 40
    },
    {
        'name': 'Rasgulla',
        'name_hindi': 'रसगुल्ला',
        'category': 'Sweets',
        'food_type': 'Vegetarian',
        'calories_per_100g': 186,
        'protein_per_100g': 4.9,
        'carbs_per_100g': 32.8,
        'fat_per_100g': 4.1,
        'fiber_per_100g': 0.0,
        'gi_index': 80,
        'description': 'Spongy cottage cheese balls in syrup',
        'serving_size_grams': 40
    },
    {
        'name': 'Kheer',
        'name_hindi': 'खीर',
        'category': 'Sweets',
        'food_type': 'Vegetarian',
        'calories_per_100g': 97,
        'protein_per_100g': 3.1,
        'carbs_per_100g': 16.8,
        'fat_per_100g': 2.1,
        'fiber_per_100g': 0.2,
        'gi_index': 65,
        'description': 'Rice pudding with milk',
        'serving_size_grams': 100
    },
    {
        'name': 'Halwa (Suji)',
        'name_hindi': 'सूजी हलवा',
        'category': 'Sweets',
        'food_type': 'Vegetarian',
        'calories_per_100g': 418,
        'protein_per_100g': 6.8,
        'carbs_per_100g': 58.2,
        'fat_per_100g': 17.1,
        'fiber_per_100g': 1.2,
        'gi_index': 75,
        'description': 'Semolina pudding',
        'serving_size_grams': 50
    },

    # Beverages
    {
        'name': 'Masala Chai',
        'name_hindi': 'मसाला चाय',
        'category': 'Beverages',
        'food_type': 'Vegetarian',
        'calories_per_100g': 38,
        'protein_per_100g': 1.8,
        'carbs_per_100g': 5.2,
        'fat_per_100g': 1.1,
        'fiber_per_100g': 0.0,
        'gi_index': 55,
        'description': 'Spiced tea with milk and sugar',
        'serving_size_grams': 150
    },
    {
        'name': 'Lassi (Sweet)',
        'name_hindi': 'मीठी लस्सी',
        'category': 'Beverages',
        'food_type': 'Vegetarian',
        'calories_per_100g': 89,
        'protein_per_100g': 3.2,
        'carbs_per_100g': 12.8,
        'fat_per_100g': 2.8,
        'fiber_per_100g': 0.0,
        'gi_index': 45,
        'description': 'Sweet yogurt drink',
        'serving_size_grams': 200
    },
    {
        'name': 'Nimbu Paani',
        'name_hindi': 'नींबू पानी',
        'category': 'Beverages',
        'food_type': 'Vegetarian',
        'calories_per_100g': 25,
        'protein_per_100g': 0.1,
        'carbs_per_100g': 6.8,
        'fat_per_100g': 0.0,
        'fiber_per_100g': 0.1,
        'gi_index': 35,
        'description': 'Fresh lime water with sugar',
        'serving_size_grams': 250
    },
    {
        'name': 'Coconut Water',
        'name_hindi': 'नारियल पानी',
        'category': 'Beverages',
        'food_type': 'Vegetarian',
        'calories_per_100g': 19,
        'protein_per_100g': 0.7,
        'carbs_per_100g': 3.7,
        'fat_per_100g': 0.2,
        'fiber_per_100g': 1.1,
        'gi_index': 54,
        'description': 'Fresh coconut water',
        'serving_size_grams': 250
    },

    # South Indian
    {
        'name': 'Idli',
        'name_hindi': 'इडली',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 158,
        'protein_per_100g': 5.1,
        'carbs_per_100g': 30.8,
        'fat_per_100g': 1.2,
        'fiber_per_100g': 2.0,
        'gi_index': 69,
        'description': 'Steamed rice and lentil cakes',
        'serving_size_grams': 40
    },
    {
        'name': 'Dosa (Plain)',
        'name_hindi': 'डोसा',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 168,
        'protein_per_100g': 4.1,
        'carbs_per_100g': 28.6,
        'fat_per_100g': 3.8,
        'fiber_per_100g': 1.2,
        'gi_index': 77,
        'description': 'Fermented rice and lentil crepe',
        'serving_size_grams': 80
    },
    {
        'name': 'Masala Dosa',
        'name_hindi': 'मसाला डोसा',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 145,
        'protein_per_100g': 3.8,
        'carbs_per_100g': 24.2,
        'fat_per_100g': 3.9,
        'fiber_per_100g': 2.1,
        'gi_index': 66,
        'description': 'Dosa with spiced potato filling',
        'serving_size_grams': 120
    },
    {
        'name': 'Sambhar',
        'name_hindi': 'सांभर',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 85,
        'protein_per_100g': 4.2,
        'carbs_per_100g': 12.8,
        'fat_per_100g': 2.1,
        'fiber_per_100g': 3.8,
        'gi_index': 30,
        'description': 'Lentil and vegetable stew',
        'serving_size_grams': 150
    },
    {
        'name': 'Upma',
        'name_hindi': 'उपमा',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 101,
        'protein_per_100g': 2.6,
        'carbs_per_100g': 16.2,
        'fat_per_100g': 3.1,
        'fiber_per_100g': 1.2,
        'gi_index': 67,
        'description': 'Semolina porridge with vegetables',
        'serving_size_grams': 150
    },
    {
        'name': 'Vada',
        'name_hindi': 'वड़ा',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 232,
        'protein_per_100g': 6.8,
        'carbs_per_100g': 28.4,
        'fat_per_100g': 10.2,
        'fiber_per_100g': 3.5,
        'gi_index': 55,
        'description': 'Deep fried lentil donuts',
        'serving_size_grams': 40
    },
    {
        'name': 'Uttapam',
        'name_hindi': 'उत्तपम',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 156,
        'protein_per_100g': 4.2,
        'carbs_per_100g': 26.8,
        'fat_per_100g': 3.9,
        'fiber_per_100g': 2.1,
        'gi_index': 72,
        'description': 'Thick pancake with vegetables',
        'serving_size_grams': 100
    },
    {
        'name': 'Rava Dosa',
        'name_hindi': 'रवा डोसा',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 175,
        'protein_per_100g': 3.8,
        'carbs_per_100g': 32.1,
        'fat_per_100g': 4.2,
        'fiber_per_100g': 1.8,
        'gi_index': 68,
        'description': 'Crispy semolina crepe',
        'serving_size_grams': 100
    },
    {
        'name': 'Pongal',
        'name_hindi': 'पोंगल',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 142,
        'protein_per_100g': 4.1,
        'carbs_per_100g': 24.8,
        'fat_per_100g': 3.2,
        'fiber_per_100g': 1.8,
        'gi_index': 58,
        'description': 'Rice and lentil porridge',
        'serving_size_grams': 150
    },
    {
        'name': 'Rasam',
        'name_hindi': 'रसम',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 52,
        'protein_per_100g': 2.1,
        'carbs_per_100g': 8.8,
        'fat_per_100g': 1.2,
        'fiber_per_100g': 1.8,
        'gi_index': 25,
        'description': 'Tangy tomato and tamarind soup',
        'serving_size_grams': 150
    },
    {
        'name': 'Coconut Chutney',
        'name_hindi': 'नारियल चटनी',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 187,
        'protein_per_100g': 3.2,
        'carbs_per_100g': 8.4,
        'fat_per_100g': 16.8,
        'fiber_per_100g': 4.2,
        'gi_index': 20,
        'description': 'Fresh coconut condiment',
        'serving_size_grams': 30
    },
    {
        'name': 'Curd Rice',
        'name_hindi': 'दही चावल',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 112,
        'protein_per_100g': 3.8,
        'carbs_per_100g': 19.2,
        'fat_per_100g': 2.1,
        'fiber_per_100g': 0.8,
        'gi_index': 62,
        'description': 'Rice mixed with yogurt and spices',
        'serving_size_grams': 150
    },
    {
        'name': 'Appam',
        'name_hindi': 'अप्पम',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 134,
        'protein_per_100g': 2.8,
        'carbs_per_100g': 26.4,
        'fat_per_100g': 2.1,
        'fiber_per_100g': 1.2,
        'gi_index': 65,
        'description': 'Fermented rice pancake',
        'serving_size_grams': 50
    },
    {
        'name': 'Puttu',
        'name_hindi': 'पुट्टू',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 167,
        'protein_per_100g': 3.2,
        'carbs_per_100g': 34.8,
        'fat_per_100g': 1.8,
        'fiber_per_100g': 2.4,
        'gi_index': 58,
        'description': 'Steamed rice flour and coconut',
        'serving_size_grams': 80
    },
    {
        'name': 'Idiyappam',
        'name_hindi': 'इडियप्पम',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 156,
        'protein_per_100g': 2.9,
        'carbs_per_100g': 32.1,
        'fat_per_100g': 1.4,
        'fiber_per_100g': 1.8,
        'gi_index': 64,
        'description': 'String hoppers made from rice flour',
        'serving_size_grams': 100
    },
    {
        'name': 'Medu Vada',
        'name_hindi': 'मेदु वडा',
        'category': 'South Indian',
        'food_type': 'Vegetarian',
        'calories_per_100g': 242,
        'protein_per_100g': 7.2,
        'carbs_per_100g': 26.8,
        'fat_per_100g': 12.1,
        'fiber_per_100g': 4.2,
        'gi_index': 52,
        'description': 'Crispy urad dal fritters',
        'serving_size_grams': 35
    },

    # Dairy Products
    {
        'name': 'Paneer',
        'name_hindi': 'पनीर',
        'category': 'Dairy',
        'food_type': 'Vegetarian',
        'calories_per_100g': 265,
        'protein_per_100g': 18.3,
        'carbs_per_100g': 1.2,
        'fat_per_100g': 20.8,
        'fiber_per_100g': 0.0,
        'gi_index': 0,
        'description': 'Fresh cottage cheese',
        'serving_size_grams': 50
    },
    {
        'name': 'Curd/Yogurt',
        'name_hindi': 'दही',
        'category': 'Dairy',
        'food_type': 'Vegetarian',
        'calories_per_100g': 60,
        'protein_per_100g': 3.5,
        'carbs_per_100g': 4.7,
        'fat_per_100g': 3.3,
        'fiber_per_100g': 0.0,
        'gi_index': 35,
        'description': 'Fresh yogurt',
        'serving_size_grams': 100
    },
    {
        'name': 'Buttermilk',
        'name_hindi': 'छाछ',
        'category': 'Dairy',
        'food_type': 'Vegetarian',
        'calories_per_100g': 40,
        'protein_per_100g': 3.1,
        'carbs_per_100g': 4.8,
        'fat_per_100g': 0.9,
        'fiber_per_100g': 0.0,
        'gi_index': 32,
        'description': 'Spiced buttermilk drink',
        'serving_size_grams': 200
    }
]

def seed_database():
    """Populate database with Indian food items"""
    app = create_app()
    
    with app.app_context():
        # Clear existing food data
        Food.query.delete()
        
        # Add all food items
        for food_data in INDIAN_FOODS:
            food = Food(**food_data)
            db.session.add(food)
        
        try:
            db.session.commit()
            total_count = Food.query.count()
            print(f"Successfully added {len(INDIAN_FOODS)} Indian food items to database!")
            print(f"Total food items in database: {total_count}")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding food items: {e}")

if __name__ == '__main__':
    seed_database()