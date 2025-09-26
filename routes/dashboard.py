from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import db, Food, FoodLog, DailySummary

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def home():
    """Main dashboard page"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # Get today's summary
    today = date.today()
    summary = current_user.get_today_summary(today)
    
    if not summary:
        # Create summary if it doesn't exist
        summary = DailySummary.get_or_create(current_user.id, today)
    
    # Get today's food logs
    today_logs = FoodLog.get_daily_logs(current_user.id, today)
    
    # Get recent meals (last 5)
    recent_meals = today_logs[:5] if today_logs else []
    
    # Calculate progress
    calorie_progress = current_user.get_calorie_progress(today)
    macro_progress = current_user.get_macro_progress(today)
    
    # Get meal recommendations
    recommended_foods = Food.get_recommended_for_user(current_user, limit=5)
    
    return render_template('dashboard/home.html',
                         summary=summary,
                         today_logs=today_logs,
                         recent_meals=recent_meals,
                         calorie_progress=calorie_progress,
                         macro_progress=macro_progress,
                         recommended_foods=recommended_foods)

@dashboard_bp.route('/log-meal')
@login_required
def log_meal():
    """Meal logging page"""
    meal_types = ['Breakfast', 'Mid-Morning', 'Lunch', 'Evening Snack', 'Dinner', 'Late Night']
    return render_template('dashboard/log_meal.html', meal_types=meal_types)

@dashboard_bp.route('/food-diary')
@dashboard_bp.route('/food-diary/<date_str>')
@login_required
def food_diary(date_str=None):
    """Food diary page showing logs for a specific date"""
    if date_str:
        try:
            view_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            view_date = date.today()
    else:
        view_date = date.today()
    
    # Get food logs for the date
    logs = FoodLog.get_daily_logs(current_user.id, view_date)
    
    # Get daily summary
    summary = DailySummary.query.filter_by(
        user_id=current_user.id,
        date=view_date
    ).first()
    
    # Group logs by meal type
    meals_by_type = {}
    for log in logs:
        if log.meal_type not in meals_by_type:
            meals_by_type[log.meal_type] = []
        meals_by_type[log.meal_type].append(log)
    
    # Calculate date range for navigation
    prev_date = view_date - timedelta(days=1)
    next_date = view_date + timedelta(days=1)
    
    return render_template('dashboard/food_diary.html',
                         view_date=view_date,
                         logs=logs,
                         summary=summary,
                         meals_by_type=meals_by_type,
                         prev_date=prev_date,
                         next_date=next_date)

@dashboard_bp.route('/progress')
@login_required
def progress():
    """Progress tracking page with charts and analytics"""
    # Get date range (last 7 days by default)
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    
    # Get weekly summaries
    summaries = DailySummary.get_weekly_summary(current_user.id, start_date)
    
    # Calculate weekly averages
    total_summaries = len(summaries)
    if total_summaries > 0:
        avg_calories = sum(s.total_calories for s in summaries) / total_summaries
        avg_protein = sum(s.total_protein for s in summaries) / total_summaries
        avg_carbs = sum(s.total_carbs for s in summaries) / total_summaries
        avg_fat = sum(s.total_fat for s in summaries) / total_summaries
    else:
        avg_calories = avg_protein = avg_carbs = avg_fat = 0
    
    weekly_stats = {
        'avg_calories': round(avg_calories, 1),
        'avg_protein': round(avg_protein, 1),
        'avg_carbs': round(avg_carbs, 1),
        'avg_fat': round(avg_fat, 1),
        'days_logged': total_summaries,
        'calorie_goal': current_user.daily_calorie_goal
    }
    
    # Prepare chart data
    chart_data = {
        'dates': [s.date.strftime('%Y-%m-%d') for s in summaries],
        'calories': [s.total_calories for s in summaries],
        'protein': [s.total_protein for s in summaries],
        'carbs': [s.total_carbs for s in summaries],
        'fat': [s.total_fat for s in summaries],
        'calorie_goals': [s.calorie_goal for s in summaries]
    }
    
    return render_template('dashboard/progress.html',
                         summaries=summaries,
                         weekly_stats=weekly_stats,
                         chart_data=chart_data,
                         start_date=start_date,
                         end_date=end_date)

@dashboard_bp.route('/goals')
@login_required
def goals():
    """Goals and profile management page"""
    # Calculate current BMR and TDEE
    bmr = current_user.calculate_bmr()
    tdee = current_user.calculate_tdee()
    bmi = current_user.get_bmi()
    bmi_category = current_user.get_bmi_category()
    
    # Calculate progress statistics
    total_logs = current_user.food_logs.count()
    total_days = current_user.daily_summaries.count()
    
    # Calculate average goal achievement
    avg_goal_achievement = 0
    if total_days > 0 and current_user.daily_calorie_goal:
        recent_summaries = current_user.daily_summaries.limit(7).all()
        if recent_summaries:
            total_achievement = sum(
                (summary.total_calories / (current_user.daily_calorie_goal or tdee)) * 100 
                for summary in recent_summaries
            )
            avg_goal_achievement = round(total_achievement / len(recent_summaries), 0)
    
    user_stats = {
        'bmr': round(bmr, 0),
        'tdee': round(tdee, 0),
        'bmi': bmi,
        'bmi_category': bmi_category,
        'total_logs': total_logs,
        'total_days': total_days,
        'avg_goal_achievement': avg_goal_achievement
    }
    
    return render_template('dashboard/goals.html', user_stats=user_stats)

@dashboard_bp.route('/recommendations')
@login_required
def recommendations():
    """Food recommendations page"""
    meal_type = request.args.get('meal_type', '')
    category = request.args.get('category', '')
    
    # Get recommended foods
    recommended_foods = Food.get_recommended_for_user(
        current_user, 
        meal_type=meal_type if meal_type else None, 
        limit=20
    )
    
    # Filter by category if specified
    if category:
        recommended_foods = [f for f in recommended_foods if f.category == category]
    
    # Get available categories for filtering
    categories = Food.get_categories()
    
    meal_types = ['Breakfast', 'Mid-Morning', 'Lunch', 'Evening Snack', 'Dinner', 'Late Night']
    
    return render_template('dashboard/recommendations.html',
                         recommended_foods=recommended_foods,
                         categories=categories,
                         meal_types=meal_types,
                         selected_meal_type=meal_type,
                         selected_category=category)

@dashboard_bp.route('/export')
@login_required
def export_page():
    """Data export page"""
    return render_template('dashboard/export.html')

@dashboard_bp.route('/search')
@login_required
def search():
    """Food search page"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    food_type = request.args.get('food_type', '')
    
    foods = []
    if query or category or food_type:
        foods = Food.search(
            query=query if query else None,
            user=current_user,
            category=category if category else None,
            food_type=food_type if food_type else None,
            limit=50
        )
    
    # Get filter options
    categories = Food.get_categories()
    food_types = Food.get_food_types()
    
    return render_template('dashboard/search.html',
                         foods=foods,
                         categories=categories,
                         food_types=food_types,
                         query=query,
                         selected_category=category,
                         selected_food_type=food_type)

@dashboard_bp.route('/food/<int:food_id>')
@login_required
def food_detail(food_id):
    """Food detail page"""
    food = Food.query.get_or_404(food_id)
    
    # Check if food is suitable for user
    is_suitable = food.is_suitable_for_user(current_user)
    
    # Get nutrition for common serving sizes
    serving_sizes = [50, 100, 150, 200, food.serving_size_grams]
    serving_sizes = sorted(list(set(serving_sizes)))  # Remove duplicates and sort
    
    nutrition_data = []
    for size in serving_sizes:
        nutrition = food.calculate_nutrition(size)
        nutrition_data.append({
            'size': size,
            'nutrition': nutrition
        })
    
    return render_template('dashboard/food_detail.html',
                         food=food,
                         is_suitable=is_suitable,
                         nutrition_data=nutrition_data)

@dashboard_bp.route('/meal-log/<int:log_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_meal_log(log_id):
    """Edit a meal log entry"""
    log = FoodLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        quantity_grams = request.form.get('quantity_grams', type=float)
        meal_type = request.form.get('meal_type', '')
        notes = request.form.get('notes', '').strip()
        
        if not quantity_grams or quantity_grams <= 0:
            flash('Please enter a valid quantity.', 'danger')
            return render_template('dashboard/edit_meal_log.html', log=log)
        
        if not meal_type:
            flash('Please select a meal type.', 'danger')
            return render_template('dashboard/edit_meal_log.html', log=log)
        
        try:
            # Recalculate nutrition based on new quantity
            nutrition = log.food.calculate_nutrition(quantity_grams)
            
            # Update log
            log.quantity_grams = quantity_grams
            log.meal_type = meal_type
            log.calories_consumed = nutrition['calories']
            log.protein_consumed = nutrition['protein']
            log.carbs_consumed = nutrition['carbs']
            log.fat_consumed = nutrition['fat']
            log.notes = notes
            
            db.session.commit()
            
            # Update daily summary
            DailySummary.update_from_logs(current_user.id, log.date_logged)
            
            flash('Meal log updated successfully!', 'success')
            return redirect(url_for('dashboard.food_diary', 
                                  date_str=log.date_logged.strftime('%Y-%m-%d')))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating meal log.', 'danger')
    
    meal_types = ['Breakfast', 'Mid-Morning', 'Lunch', 'Evening Snack', 'Dinner', 'Late Night']
    return render_template('dashboard/edit_meal_log.html', log=log, meal_types=meal_types)

@dashboard_bp.route('/meal-log/<int:log_id>/delete', methods=['POST'])
@login_required
def delete_meal_log(log_id):
    """Delete a meal log entry"""
    log = FoodLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    log_date = log.date_logged
    
    try:
        db.session.delete(log)
        db.session.commit()
        
        # Update daily summary
        DailySummary.update_from_logs(current_user.id, log_date)
        
        flash('Meal log deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting meal log.', 'danger')
    
    return redirect(url_for('dashboard.food_diary', 
                          date_str=log_date.strftime('%Y-%m-%d')))