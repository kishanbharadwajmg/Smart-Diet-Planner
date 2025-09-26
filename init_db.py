#!/usr/bin/env python3
"""
Initialize the Smart Diet Planner database
"""

import os
from app import create_app
from models import db, User

def init_database():
    """Initialize the database and create tables"""
    app = create_app()
    
    with app.app_context():
        # Create database directory if it doesn't exist
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                print(f"Created database directory: {db_dir}")
        else:
            # For relative path, create database directory
            os.makedirs("database", exist_ok=True)
        
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@dietplanner.com',
                first_name='Admin',
                last_name='User',
                age=30,
                gender='Other',
                height=170,
                weight=70,
                activity_level='Moderately Active',
                food_preferences='Vegetarian',
                is_admin=True
            )
            admin.set_password('admin123')
            admin.update_goals()
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created successfully!")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_database()