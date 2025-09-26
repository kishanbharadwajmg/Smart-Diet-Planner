from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import db, User, Food, FoodLog, DailySummary

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get system statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_foods = Food.query.filter_by(is_active=True).count()
    total_logs_today = FoodLog.query.filter_by(date_logged=date.today()).count()
    
    # Get recent activity
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    recent_logs = FoodLog.query.order_by(FoodLog.created_at.desc()).limit(10).all()
    
    # Get weekly stats
    week_ago = date.today() - timedelta(days=7)
    weekly_logs = FoodLog.query.filter(FoodLog.date_logged >= week_ago).count()
    new_users_this_week = User.query.filter(
        User.created_at >= datetime.combine(week_ago, datetime.min.time()),
        User.is_admin == False
    ).count()
    
    stats = {
        'total_users': total_users,
        'total_foods': total_foods,
        'total_logs_today': total_logs_today,
        'weekly_logs': weekly_logs,
        'new_users_this_week': new_users_this_week
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         recent_logs=recent_logs)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '').strip()
    
    # Build query
    query = User.query.filter_by(is_admin=False)
    
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    users_pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html',
                         users=users_pagination.items,
                         pagination=users_pagination,
                         search=search)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """User detail page"""
    user = User.query.filter_by(id=user_id, is_admin=False).first_or_404()
    
    # Get user statistics
    total_logs = FoodLog.query.filter_by(user_id=user.id).count()
    days_active = db.session.query(FoodLog.date_logged.distinct()).filter_by(user_id=user.id).count()
    
    # Get recent activity
    recent_logs = FoodLog.query.filter_by(user_id=user.id).order_by(
        FoodLog.date_logged.desc(), FoodLog.time_logged.desc()
    ).limit(10).all()
    
    # Get current goals and progress
    today_summary = user.get_today_summary()
    calorie_progress = user.get_calorie_progress()
    macro_progress = user.get_macro_progress()
    
    user_stats = {
        'total_logs': total_logs,
        'days_active': days_active,
        'avg_logs_per_day': round(total_logs / max(days_active, 1), 1),
        'bmr': round(user.calculate_bmr(), 0),
        'tdee': round(user.calculate_tdee(), 0),
        'bmi': user.get_bmi(),
        'bmi_category': user.get_bmi_category()
    }
    
    return render_template('admin/user_detail.html',
                         user=user,
                         user_stats=user_stats,
                         recent_logs=recent_logs,
                         today_summary=today_summary,
                         calorie_progress=calorie_progress,
                         macro_progress=macro_progress)

@admin_bp.route('/foods')
@login_required
@admin_required
def foods():
    """Food management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '')
    food_type = request.args.get('food_type', '')
    
    # Build query
    query = Food.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            db.or_(
                Food.name.ilike(f'%{search}%'),
                Food.name_hindi.ilike(f'%{search}%'),
                Food.description.ilike(f'%{search}%')
            )
        )
    
    if category:
        query = query.filter_by(category=category)
    
    if food_type:
        query = query.filter_by(food_type=food_type)
    
    foods_pagination = query.order_by(Food.name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get filter options
    categories = Food.get_categories()
    food_types = Food.get_food_types()
    
    return render_template('admin/foods.html',
                         foods=foods_pagination.items,
                         pagination=foods_pagination,
                         categories=categories,
                         food_types=food_types,
                         search=search,
                         selected_category=category,
                         selected_food_type=food_type)

@admin_bp.route('/foods/<int:food_id>')
@login_required
@admin_required
def food_detail(food_id):
    """Food detail page"""
    food = Food.query.get_or_404(food_id)
    
    # Get usage statistics
    total_logs = FoodLog.query.filter_by(food_id=food.id).count()
    unique_users = db.session.query(FoodLog.user_id.distinct()).filter_by(food_id=food.id).count()
    
    # Get recent usage
    recent_logs = FoodLog.query.filter_by(food_id=food.id).order_by(
        FoodLog.date_logged.desc(), FoodLog.time_logged.desc()
    ).limit(10).all()
    
    food_stats = {
        'total_logs': total_logs,
        'unique_users': unique_users,
        'avg_quantity': db.session.query(db.func.avg(FoodLog.quantity_grams)).filter_by(food_id=food.id).scalar() or 0,
        'nutrition_density': food.get_nutrition_density(),
        'gi_category': food.get_gi_category()
    }
    
    return render_template('admin/food_detail.html',
                         food=food,
                         food_stats=food_stats,
                         recent_logs=recent_logs)

@admin_bp.route('/foods/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_food():
    """Add new food item"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        name_hindi = request.form.get('name_hindi', '').strip()
        category = request.form.get('category', '').strip()
        food_type = request.form.get('food_type', 'Vegetarian')
        calories_per_100g = request.form.get('calories_per_100g', type=float)
        protein_per_100g = request.form.get('protein_per_100g', type=float)
        carbs_per_100g = request.form.get('carbs_per_100g', type=float)
        fat_per_100g = request.form.get('fat_per_100g', type=float)
        fiber_per_100g = request.form.get('fiber_per_100g', type=float) or 0
        gi_index = request.form.get('gi_index', type=int)
        description = request.form.get('description', '').strip()
        serving_size_grams = request.form.get('serving_size_grams', type=float) or 100
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Food name is required.')
        
        if not category:
            errors.append('Category is required.')
        
        if not food_type or food_type not in Food.get_food_types():
            errors.append('Valid food type is required.')
        
        if calories_per_100g is None or calories_per_100g < 0:
            errors.append('Valid calories per 100g is required.')
        
        if protein_per_100g is None or protein_per_100g < 0:
            errors.append('Valid protein per 100g is required.')
        
        if carbs_per_100g is None or carbs_per_100g < 0:
            errors.append('Valid carbs per 100g is required.')
        
        if fat_per_100g is None or fat_per_100g < 0:
            errors.append('Valid fat per 100g is required.')
        
        if gi_index is not None and (gi_index < 0 or gi_index > 100):
            errors.append('GI index must be between 0 and 100.')
        
        # Check for duplicate names
        if Food.query.filter_by(name=name, is_active=True).first():
            errors.append('A food item with this name already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin/add_food.html',
                                 categories=Food.get_categories(),
                                 food_types=Food.get_food_types())
        
        # Create new food
        try:
            food = Food(
                name=name,
                name_hindi=name_hindi if name_hindi else None,
                category=category,
                food_type=food_type,
                calories_per_100g=calories_per_100g,
                protein_per_100g=protein_per_100g,
                carbs_per_100g=carbs_per_100g,
                fat_per_100g=fat_per_100g,
                fiber_per_100g=fiber_per_100g,
                gi_index=gi_index,
                description=description if description else None,
                serving_size_grams=serving_size_grams
            )
            
            db.session.add(food)
            db.session.commit()
            
            flash(f'Food item "{name}" added successfully!', 'success')
            return redirect(url_for('admin.food_detail', food_id=food.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error adding food item.', 'danger')
    
    return render_template('admin/add_food.html',
                         categories=Food.get_categories(),
                         food_types=Food.get_food_types())

@admin_bp.route('/foods/<int:food_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_food(food_id):
    """Edit food item"""
    food = Food.query.get_or_404(food_id)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        name_hindi = request.form.get('name_hindi', '').strip()
        category = request.form.get('category', '').strip()
        food_type = request.form.get('food_type', 'Vegetarian')
        calories_per_100g = request.form.get('calories_per_100g', type=float)
        protein_per_100g = request.form.get('protein_per_100g', type=float)
        carbs_per_100g = request.form.get('carbs_per_100g', type=float)
        fat_per_100g = request.form.get('fat_per_100g', type=float)
        fiber_per_100g = request.form.get('fiber_per_100g', type=float) or 0
        gi_index = request.form.get('gi_index', type=int)
        description = request.form.get('description', '').strip()
        serving_size_grams = request.form.get('serving_size_grams', type=float) or 100
        is_active = request.form.get('is_active') == 'on'
        
        # Validation (same as add_food)
        errors = []
        
        if not name:
            errors.append('Food name is required.')
        
        if not category:
            errors.append('Category is required.')
        
        if not food_type or food_type not in Food.get_food_types():
            errors.append('Valid food type is required.')
        
        if calories_per_100g is None or calories_per_100g < 0:
            errors.append('Valid calories per 100g is required.')
        
        if protein_per_100g is None or protein_per_100g < 0:
            errors.append('Valid protein per 100g is required.')
        
        if carbs_per_100g is None or carbs_per_100g < 0:
            errors.append('Valid carbs per 100g is required.')
        
        if fat_per_100g is None or fat_per_100g < 0:
            errors.append('Valid fat per 100g is required.')
        
        if gi_index is not None and (gi_index < 0 or gi_index > 100):
            errors.append('GI index must be between 0 and 100.')
        
        # Check for duplicate names (excluding current food)
        duplicate = Food.query.filter(
            Food.name == name,
            Food.is_active == True,
            Food.id != food.id
        ).first()
        if duplicate:
            errors.append('A food item with this name already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin/edit_food.html',
                                 food=food,
                                 categories=Food.get_categories(),
                                 food_types=Food.get_food_types())
        
        # Update food
        try:
            food.name = name
            food.name_hindi = name_hindi if name_hindi else None
            food.category = category
            food.food_type = food_type
            food.calories_per_100g = calories_per_100g
            food.protein_per_100g = protein_per_100g
            food.carbs_per_100g = carbs_per_100g
            food.fat_per_100g = fat_per_100g
            food.fiber_per_100g = fiber_per_100g
            food.gi_index = gi_index
            food.description = description if description else None
            food.serving_size_grams = serving_size_grams
            food.is_active = is_active
            food.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Food item "{name}" updated successfully!', 'success')
            return redirect(url_for('admin.food_detail', food_id=food.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating food item.', 'danger')
    
    return render_template('admin/edit_food.html',
                         food=food,
                         categories=Food.get_categories(),
                         food_types=Food.get_food_types())

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """System analytics page"""
    # Date range for analytics (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=29)
    
    # User registration trends
    user_registrations = db.session.query(
        db.func.date(User.created_at).label('date'),
        db.func.count(User.id).label('count')
    ).filter(
        User.created_at >= datetime.combine(start_date, datetime.min.time()),
        User.is_admin == False
    ).group_by(db.func.date(User.created_at)).all()
    
    # Daily log activity
    daily_logs = db.session.query(
        FoodLog.date_logged.label('date'),
        db.func.count(FoodLog.id).label('count')
    ).filter(
        FoodLog.date_logged >= start_date
    ).group_by(FoodLog.date_logged).all()
    
    # Most popular foods
    popular_foods = db.session.query(
        Food.name,
        db.func.count(FoodLog.id).label('usage_count')
    ).join(FoodLog).group_by(Food.id, Food.name).order_by(
        db.func.count(FoodLog.id).desc()
    ).limit(10).all()
    
    # User engagement stats
    active_users = db.session.query(FoodLog.user_id.distinct()).filter(
        FoodLog.date_logged >= start_date
    ).count()
    
    total_users = User.query.filter_by(is_admin=False).count()
    engagement_rate = (active_users / total_users * 100) if total_users > 0 else 0
    
    analytics_data = {
        'user_registrations': [{'date': reg.date.strftime('%Y-%m-%d'), 'count': reg.count} for reg in user_registrations],
        'daily_logs': [{'date': log.date.strftime('%Y-%m-%d'), 'count': log.count} for log in daily_logs],
        'popular_foods': [{'name': food.name, 'count': food.usage_count} for food in popular_foods],
        'active_users': active_users,
        'total_users': total_users,
        'engagement_rate': round(engagement_rate, 1),
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
    }
    
    return render_template('admin/analytics.html', analytics=analytics_data)

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Admin settings page"""
    # System health checks
    total_users = User.query.count()
    total_foods = Food.query.count()
    total_logs = FoodLog.query.count()
    
    # Database statistics
    db_stats = {
        'users': total_users,
        'foods': total_foods,
        'food_logs': total_logs,
        'daily_summaries': DailySummary.query.count()
    }
    
    return render_template('admin/settings.html', db_stats=db_stats)