from flask import Blueprint, request, jsonify, make_response, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import db, User, Food, FoodLog, DailySummary
import csv
import io

api_bp = Blueprint('api', __name__)

@api_bp.route('/search_foods')
@login_required
def search_foods():
    """API endpoint for food search"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    food_type = request.args.get('food_type', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not query and not category and not food_type:
        return jsonify({'status': 'error', 'message': 'No search parameters provided'})
    
    try:
        foods = Food.search(
            query=query if query else None,
            user=current_user,
            category=category if category else None,
            food_type=food_type if food_type else None,
            limit=limit
        )
        
        foods_data = [food.to_dict() for food in foods]
        
        return jsonify({
            'status': 'success',
            'foods': foods_data,
            'count': len(foods_data)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Search failed'})

@api_bp.route('/log_meal', methods=['POST'])
@login_required
def log_meal():
    """API endpoint for logging meals"""
    try:
        food_id = request.form.get('food_id', type=int)
        quantity_grams = request.form.get('quantity_grams', type=float)
        meal_type = request.form.get('meal_type', '')
        notes = request.form.get('notes', '').strip()
        log_date = request.form.get('log_date', '')
        
        # Validation
        if not food_id:
            return jsonify({'status': 'error', 'message': 'Food ID is required'})
        
        if not quantity_grams or quantity_grams <= 0:
            return jsonify({'status': 'error', 'message': 'Valid quantity is required'})
        
        if not meal_type:
            return jsonify({'status': 'error', 'message': 'Meal type is required'})
        
        # Parse log date
        if log_date:
            try:
                parsed_date = datetime.strptime(log_date, '%Y-%m-%d').date()
            except ValueError:
                parsed_date = date.today()
        else:
            parsed_date = date.today()
        
        # Create food log entry
        food_log = FoodLog.create_from_food(
            user_id=current_user.id,
            food_id=food_id,
            quantity_grams=quantity_grams,
            meal_type=meal_type,
            notes=notes,
            log_date=parsed_date
        )
        
        db.session.add(food_log)
        db.session.commit()
        
        # Update daily summary
        DailySummary.update_from_logs(current_user.id, parsed_date)
        
        return jsonify({
            'status': 'success',
            'message': 'Meal logged successfully',
            'log_id': food_log.id
        })
        
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to log meal'})

@api_bp.route('/dashboard_data')
@login_required
def dashboard_data():
    """API endpoint for dashboard data"""
    try:
        target_date = request.args.get('date', date.today().isoformat())
        try:
            parsed_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            parsed_date = date.today()
        
        # Get daily summary
        summary = current_user.get_today_summary(parsed_date)
        if not summary:
            summary = DailySummary.get_or_create(current_user.id, parsed_date)
        
        # Get progress data
        calorie_progress = current_user.get_calorie_progress(parsed_date)
        macro_progress = current_user.get_macro_progress(parsed_date)
        
        # Get recent meals
        recent_meals = FoodLog.get_daily_logs(current_user.id, parsed_date)
        recent_meals_data = [meal.to_dict() for meal in recent_meals[:5]]
        
        # Chart data for macros
        chart_data = {
            'protein': summary.total_protein if summary else 0,
            'carbs': summary.total_carbs if summary else 0,
            'fat': summary.total_fat if summary else 0
        }
        
        return jsonify({
            'status': 'success',
            'stats': {
                'today_calories': summary.total_calories if summary else 0,
                'today_protein': summary.total_protein if summary else 0,
                'today_carbs': summary.total_carbs if summary else 0,
                'today_fat': summary.total_fat if summary else 0,
                'calorie_goal': current_user.daily_calorie_goal or 2000
            },
            'progress': {
                'calories': calorie_progress,
                'protein': macro_progress['protein'],
                'carbs': macro_progress['carbs'],
                'fat': macro_progress['fat']
            },
            'recent_meals': recent_meals_data,
            'chart_data': chart_data
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to fetch dashboard data'})

@api_bp.route('/chart_data')
@login_required
def chart_data():
    """API endpoint for chart data"""
    try:
        # Get date range
        days = request.args.get('days', 7, type=int)
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Get weekly summaries
        summaries = DailySummary.get_weekly_summary(current_user.id, start_date)
        
        # Prepare chart data
        chart_data = {
            'dates': [s.date.strftime('%m/%d') for s in summaries],
            'calories': [s.total_calories for s in summaries],
            'protein': [s.total_protein for s in summaries],
            'carbs': [s.total_carbs for s in summaries],
            'fat': [s.total_fat for s in summaries],
            'calorie_goals': [s.calorie_goal for s in summaries]
        }
        
        return jsonify({
            'status': 'success',
            'chart_data': chart_data
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to fetch chart data'})

@api_bp.route('/export_csv')
@login_required
def export_csv():
    """Export food logs as CSV"""
    try:
        # Get date range
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Parse dates
        if date_from:
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                start_date = date.today() - timedelta(days=30)
        else:
            start_date = date.today() - timedelta(days=30)
        
        if date_to:
            try:
                end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                end_date = date.today()
        else:
            end_date = date.today()
        
        # Get food logs
        logs = FoodLog.get_user_logs(current_user.id, start_date, end_date)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date', 'Time', 'Meal Type', 'Food Name', 'Quantity (g)',
            'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Notes'
        ])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.date_logged.strftime('%Y-%m-%d'),
                log.time_logged.strftime('%H:%M:%S'),
                log.meal_type,
                log.food.name,
                log.quantity_grams,
                log.calories_consumed,
                log.protein_consumed,
                log.carbs_consumed,
                log.fat_consumed,
                log.notes or ''
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=food_log_{start_date}_to_{end_date}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to export data'})

@api_bp.route('/food/<int:food_id>/nutrition')
@login_required
def food_nutrition(food_id):
    """Get nutrition information for a specific quantity of food"""
    try:
        food = Food.query.get_or_404(food_id)
        quantity = request.args.get('quantity', 100, type=float)
        
        if quantity <= 0:
            return jsonify({'status': 'error', 'message': 'Invalid quantity'})
        
        nutrition = food.calculate_nutrition(quantity)
        
        return jsonify({
            'status': 'success',
            'food_id': food_id,
            'food_name': food.name,
            'quantity_grams': quantity,
            'nutrition': nutrition
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to calculate nutrition'})

@api_bp.route('/recommendations')
@login_required
def recommendations():
    """Get food recommendations for user"""
    try:
        meal_type = request.args.get('meal_type', '')
        limit = request.args.get('limit', 10, type=int)
        
        # Get recommended foods
        recommended_foods = Food.get_recommended_for_user(
            current_user,
            meal_type=meal_type if meal_type else None,
            limit=limit
        )
        
        foods_data = [food.to_dict() for food in recommended_foods]
        
        return jsonify({
            'status': 'success',
            'recommendations': foods_data,
            'meal_type': meal_type,
            'count': len(foods_data)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to get recommendations'})

@api_bp.route('/user/goals/update', methods=['POST'])
@login_required
def update_goals():
    """Update user goals"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            # JSON request (API)
            calorie_goal = request.json.get('calorie_goal', type=float)
            protein_goal = request.json.get('protein_goal', type=float)
            carb_goal = request.json.get('carb_goal', type=float)
            fat_goal = request.json.get('fat_goal', type=float)
        else:
            # Form data request (web form)
            calorie_goal = request.form.get('daily_calorie_goal', type=float)
            protein_goal = request.form.get('protein_goal', type=float)
            carb_goal = request.form.get('carb_goal', type=float)
            fat_goal = request.form.get('fat_goal', type=float)
        
        # Validation for form requests
        if not request.is_json:
            if not calorie_goal or calorie_goal < 1000 or calorie_goal > 5000:
                flash('Please enter a valid calorie goal between 1000-5000 calories.', 'danger')
                return redirect(url_for('dashboard.goals'))
        
        if calorie_goal:
            current_user.daily_calorie_goal = calorie_goal
        if protein_goal:
            current_user.protein_goal = protein_goal
        if carb_goal:
            current_user.carb_goal = carb_goal
        if fat_goal:
            current_user.fat_goal = fat_goal
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': 'Goals updated successfully'
            })
        else:
            flash('Goals updated successfully!', 'success')
            return redirect(url_for('dashboard.goals'))
        
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'status': 'error', 'message': 'Failed to update goals'})
        else:
            flash('Error updating goals. Please try again.', 'danger')
            return redirect(url_for('dashboard.goals'))

# Admin API endpoints
@api_bp.route('/admin/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def admin_delete_user(user_id):
    """Admin endpoint to delete a user"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting other admins
        if user.is_admin and user.id != current_user.id:
            return jsonify({'status': 'error', 'message': 'Cannot delete other admin users'})
        
        # Prevent self-deletion
        if user.id == current_user.id:
            return jsonify({'status': 'error', 'message': 'Cannot delete your own account'})
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'User deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to delete user'})

@api_bp.route('/admin/delete_food/<int:food_id>', methods=['DELETE'])
@login_required
def admin_delete_food(food_id):
    """Admin endpoint to delete a food item"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    try:
        food = Food.query.get_or_404(food_id)
        
        # Check if food is used in any logs
        log_count = FoodLog.query.filter_by(food_id=food_id).count()
        if log_count > 0:
            return jsonify({
                'status': 'error', 
                'message': f'Cannot delete food item. It is used in {log_count} meal logs.'
            })
        
        db.session.delete(food)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Food item deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to delete food item'})

@api_bp.route('/remove_preference', methods=['POST'])
@login_required
def remove_preference():
    """API endpoint to remove user preference"""
    from models.user_preferences import UserPreference
    
    try:
        preference_type = request.form.get('preference_type', '')
        preference_value = request.form.get('preference_value', '')
        
        if not preference_type or not preference_value:
            return jsonify({'status': 'error', 'message': 'Missing required fields'})
        
        # Find and deactivate the preference
        preference = UserPreference.query.filter_by(
            user_id=current_user.id,
            preference_type=preference_type,
            preference_value=preference_value,
            is_active=True
        ).first()
        
        if preference:
            preference.is_active = False
            db.session.commit()
            flash(f'{preference_type.title()} "{preference_value}" removed successfully!', 'success')
        else:
            flash('Preference not found.', 'warning')
        
        return redirect(url_for('auth.preferences'))
        
    except Exception as e:
        db.session.rollback()
        flash('Error removing preference.', 'danger')
        return redirect(url_for('auth.preferences'))

