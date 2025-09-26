from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard.home'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '')
        height = request.form.get('height', type=float)
        weight = request.form.get('weight', type=float)
        activity_level = request.form.get('activity_level', 'Sedentary')
        food_preferences = request.form.get('food_preferences', 'Vegetarian')
        is_diabetic = request.form.get('is_diabetic') == 'on'
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if not first_name or not last_name:
            errors.append('First name and last name are required.')
        
        if not age or age < 13 or age > 120:
            errors.append('Please enter a valid age between 13 and 120.')
        
        if not gender or gender not in ['Male', 'Female', 'Other']:
            errors.append('Please select a valid gender.')
        
        if not height or height < 100 or height > 250:
            errors.append('Please enter a valid height between 100-250 cm.')
        
        if not weight or weight < 30 or weight > 300:
            errors.append('Please enter a valid weight between 30-300 kg.')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                age=age,
                gender=gender,
                height=height,
                weight=weight,
                activity_level=activity_level,
                food_preferences=food_preferences,
                is_diabetic=is_diabetic,
                is_admin=False
            )
            user.set_password(password)
            user.update_goals()  # Calculate TDEE and set goals
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard.home'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not username_or_email or not password:
            flash('Please enter both username/email and password.', 'danger')
            return render_template('auth/login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            
            # Update last login time (if you want to track it)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect based on user type
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('dashboard.home'))
        else:
            flash('Invalid username/email or password.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    user_name = current_user.first_name
    logout_user()
    flash(f'Goodbye, {user_name}! You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '')
        height = request.form.get('height', type=float)
        weight = request.form.get('weight', type=float)
        activity_level = request.form.get('activity_level', 'Sedentary')
        food_preferences = request.form.get('food_preferences', 'Vegetarian')
        is_diabetic = request.form.get('is_diabetic') == 'on'
        
        # Validation
        errors = []
        
        if not first_name or not last_name:
            errors.append('First name and last name are required.')
        
        if not age or age < 13 or age > 120:
            errors.append('Please enter a valid age between 13 and 120.')
        
        if not gender or gender not in ['Male', 'Female', 'Other']:
            errors.append('Please select a valid gender.')
        
        if not height or height < 100 or height > 250:
            errors.append('Please enter a valid height between 100-250 cm.')
        
        if not weight or weight < 30 or weight > 300:
            errors.append('Please enter a valid weight between 30-300 kg.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/edit_profile.html')
        
        # Update user
        try:
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.age = age
            current_user.gender = gender
            current_user.height = height
            current_user.weight = weight
            current_user.activity_level = activity_level
            current_user.food_preferences = food_preferences
            current_user.is_diabetic = is_diabetic
            
            # Recalculate goals if physical parameters changed
            current_user.update_goals()
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
    
    return render_template('auth/edit_profile.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not current_password:
            flash('Please enter your current password.', 'danger')
            return render_template('auth/change_password.html')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')
        
        if not new_password or len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')
        
        # Update password
        try:
            current_user.set_password(new_password)
            current_user.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while changing your password.', 'danger')
    
    return render_template('auth/change_password.html')

@auth_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Manage user dietary preferences"""
    from models.user_preferences import UserPreference
    
    if request.method == 'POST':
        # Handle adding preferences
        preference_type = request.form.get('preference_type', '')
        preference_value = request.form.get('preference_value', '').strip()
        
        if preference_type and preference_value:
            try:
                UserPreference.add_preference(
                    current_user.id,
                    preference_type,
                    preference_value
                )
                flash(f'{preference_type.title()} added successfully!', 'success')
            except Exception as e:
                flash('Error adding preference.', 'danger')
        
        return redirect(url_for('auth.preferences'))
    
    # Get user's preferences
    allergies = UserPreference.get_allergies(current_user.id)
    dislikes = UserPreference.get_dislikes(current_user.id)
    medical = UserPreference.get_medical_restrictions(current_user.id)
    
    return render_template('auth/preferences.html', 
                         allergies=allergies, 
                         dislikes=dislikes, 
                         medical=medical)

@auth_bp.route('/preferences/remove/<preference_type>/<preference_value>')
@login_required
def remove_preference(preference_type, preference_value):
    """Remove a dietary preference"""
    from models.user_preferences import UserPreference
    
    try:
        UserPreference.remove_preference(
            current_user.id,
            preference_type,
            preference_value
        )
        flash(f'{preference_type.title()} removed successfully!', 'success')
    except Exception as e:
        flash('Error removing preference.', 'danger')
    
    return redirect(url_for('auth.preferences'))

@auth_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    password = request.form.get('password', '')
    confirm_delete = request.form.get('confirm_delete')
    
    # Validation
    if not password:
        flash('Please enter your password to confirm deletion.', 'danger')
        return redirect(url_for('auth.profile'))
    
    if not current_user.check_password(password):
        flash('Incorrect password. Account deletion cancelled.', 'danger')
        return redirect(url_for('auth.profile'))
    
    if not confirm_delete:
        flash('Please confirm that you understand this action cannot be undone.', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Delete user account
    try:
        user_id = current_user.id
        logout_user()
        
        # Delete user and all related data (cascading should handle this)
        from models import User
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
        
        flash('Your account has been successfully deleted.', 'info')
        return redirect(url_for('index'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting your account. Please try again.', 'danger')
        return redirect(url_for('auth.profile'))