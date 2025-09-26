-- Smart Diet Planner Database Schema

-- Users table for storing user information
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    height REAL NOT NULL, -- in cm
    weight REAL NOT NULL, -- in kg
    activity_level VARCHAR(20) NOT NULL DEFAULT 'Sedentary' 
        CHECK (activity_level IN ('Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extremely Active')),
    food_preferences VARCHAR(20) NOT NULL DEFAULT 'Vegetarian'
        CHECK (food_preferences IN ('Vegetarian', 'Non-Vegetarian', 'Eggetarian')),
    is_diabetic BOOLEAN NOT NULL DEFAULT 0,
    disliked_foods TEXT, -- JSON array of disliked food IDs
    daily_calorie_goal REAL,
    protein_goal REAL,
    carb_goal REAL,
    fat_goal REAL,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Foods table for Indian food database
CREATE TABLE foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    name_hindi VARCHAR(200), -- Hindi name for Indian foods
    category VARCHAR(50) NOT NULL, -- Rice, Dal, Vegetables, Meat, Snacks, etc.
    food_type VARCHAR(20) NOT NULL DEFAULT 'Vegetarian'
        CHECK (food_type IN ('Vegetarian', 'Non-Vegetarian', 'Eggetarian')),
    calories_per_100g REAL NOT NULL,
    protein_per_100g REAL NOT NULL,
    carbs_per_100g REAL NOT NULL,
    fat_per_100g REAL NOT NULL,
    fiber_per_100g REAL NOT NULL DEFAULT 0,
    gi_index INTEGER, -- Glycemic Index (0-100, NULL if unknown)
    description TEXT,
    serving_size_grams REAL DEFAULT 100, -- Common serving size
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Food logs table for tracking user meals
CREATE TABLE food_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity_grams REAL NOT NULL,
    meal_type VARCHAR(20) NOT NULL 
        CHECK (meal_type IN ('Breakfast', 'Mid-Morning', 'Lunch', 'Evening Snack', 'Dinner', 'Late Night')),
    calories_consumed REAL NOT NULL,
    protein_consumed REAL NOT NULL,
    carbs_consumed REAL NOT NULL,
    fat_consumed REAL NOT NULL,
    date_logged DATE NOT NULL,
    time_logged TIME DEFAULT CURRENT_TIME,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods (id) ON DELETE RESTRICT
);

-- User preferences for detailed dietary requirements
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    preference_type VARCHAR(50) NOT NULL, -- 'allergy', 'dislike', 'medical', etc.
    preference_value VARCHAR(200) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Daily summaries for quick access to user progress
CREATE TABLE daily_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    total_calories REAL NOT NULL DEFAULT 0,
    total_protein REAL NOT NULL DEFAULT 0,
    total_carbs REAL NOT NULL DEFAULT 0,
    total_fat REAL NOT NULL DEFAULT 0,
    calorie_goal REAL NOT NULL,
    protein_goal REAL NOT NULL,
    carb_goal REAL NOT NULL,
    fat_goal REAL NOT NULL,
    meals_logged INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE(user_id, date)
);

-- Indexes for better query performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_foods_name ON foods(name);
CREATE INDEX idx_foods_category ON foods(category);
CREATE INDEX idx_foods_type ON foods(food_type);
CREATE INDEX idx_foods_gi ON foods(gi_index);
CREATE INDEX idx_food_logs_user_date ON food_logs(user_id, date_logged);
CREATE INDEX idx_food_logs_date ON food_logs(date_logged);
CREATE INDEX idx_daily_summaries_user_date ON daily_summaries(user_id, date);
CREATE INDEX idx_user_preferences_user ON user_preferences(user_id);

-- Triggers for maintaining daily summaries
CREATE TRIGGER update_daily_summary_insert
AFTER INSERT ON food_logs
BEGIN
    INSERT OR REPLACE INTO daily_summaries (
        user_id, date, total_calories, total_protein, total_carbs, total_fat,
        calorie_goal, protein_goal, carb_goal, fat_goal, meals_logged, updated_at
    )
    SELECT 
        NEW.user_id,
        NEW.date_logged,
        COALESCE(SUM(fl.calories_consumed), 0),
        COALESCE(SUM(fl.protein_consumed), 0),
        COALESCE(SUM(fl.carbs_consumed), 0),
        COALESCE(SUM(fl.fat_consumed), 0),
        u.daily_calorie_goal,
        u.protein_goal,
        u.carb_goal,
        u.fat_goal,
        COUNT(fl.id),
        CURRENT_TIMESTAMP
    FROM users u
    LEFT JOIN food_logs fl ON fl.user_id = u.id AND fl.date_logged = NEW.date_logged
    WHERE u.id = NEW.user_id
    GROUP BY u.id;
END;

CREATE TRIGGER update_daily_summary_delete
AFTER DELETE ON food_logs
BEGIN
    INSERT OR REPLACE INTO daily_summaries (
        user_id, date, total_calories, total_protein, total_carbs, total_fat,
        calorie_goal, protein_goal, carb_goal, fat_goal, meals_logged, updated_at
    )
    SELECT 
        OLD.user_id,
        OLD.date_logged,
        COALESCE(SUM(fl.calories_consumed), 0),
        COALESCE(SUM(fl.protein_consumed), 0),
        COALESCE(SUM(fl.carbs_consumed), 0),
        COALESCE(SUM(fl.fat_consumed), 0),
        u.daily_calorie_goal,
        u.protein_goal,
        u.carb_goal,
        u.fat_goal,
        COUNT(fl.id),
        CURRENT_TIMESTAMP
    FROM users u
    LEFT JOIN food_logs fl ON fl.user_id = u.id AND fl.date_logged = OLD.date_logged
    WHERE u.id = OLD.user_id
    GROUP BY u.id;
END;