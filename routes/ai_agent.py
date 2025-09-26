from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import json
import logging
from services.ai_agent import DietAIAgent

logger = logging.getLogger(__name__)

ai_agent_bp = Blueprint('ai_agent', __name__)

@ai_agent_bp.route('/')
@login_required
def chat_interface():
    """Main AI agent chat interface"""
    return render_template('ai_agent/chat.html')

@ai_agent_bp.route('/debug')
@login_required
def debug_ai():
    """Debug AI agent status"""
    try:
        ai_agent = DietAIAgent()
        
        # Test Gemini connection
        gemini_status = "Not configured"
        gemini_models = []
        if hasattr(ai_agent, 'gemini_client'):
            gemini_status = "Available" if ai_agent.gemini_client.is_available() else "Not available"
            gemini_models = ai_agent.gemini_client.list_models()
        
        # Test Ollama connection
        ollama_status = "Not configured"
        ollama_models = []
        if hasattr(ai_agent, 'ollama_client'):
            ollama_status = "Available" if ai_agent.ollama_client.is_available() else "Not running"
            ollama_models = ai_agent.ollama_client.list_models()
        
        # Test a simple question
        test_result = ai_agent.answer_nutrition_question("What is protein?", current_user.to_dict())
        
        debug_info = {
            'use_gemini': ai_agent.use_gemini,
            'gemini_status': gemini_status,
            'gemini_models': gemini_models,
            'use_ollama': ai_agent.use_ollama,
            'ollama_status': ollama_status,
            'ollama_models': ollama_models,
            'test_question_result': test_result
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': str(e.__traceback__)
        }), 500

@ai_agent_bp.route('/ask', methods=['POST'])
@login_required
def ask_question():
    """Handle AI agent questions via AJAX"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Please provide a question'
            }), 400
        
        # Initialize AI agent
        ai_agent = DietAIAgent()
        
        # Prepare user data
        user_data = current_user.to_dict()
        
        # Get answer from AI agent
        result = ai_agent.answer_nutrition_question(question, user_data)
        
        # Log the result for debugging
        logger.info(f"AI agent result: {result}")
        
        if result['success']:
            return jsonify({
                'success': True,
                'answer': result['answer'],
                'generated_at': result['generated_at'],
                'source': result.get('source', 'unknown')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to get answer'),
                'message': result.get('message', ''),
                'source': result.get('source', 'unknown')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@ai_agent_bp.route('/generate-diet-plan', methods=['GET', 'POST'])
@login_required
def generate_diet_plan():
    """Generate a personalized diet plan"""
    if request.method == 'POST':
        try:
            # Get preferences from form
            preferences = {
                'meal_count': request.form.get('meal_count', '3'),
                'cuisine_preference': request.form.get('cuisine_preference', ''),
                'cooking_time': request.form.get('cooking_time', ''),
                'budget_range': request.form.get('budget_range', ''),
                'special_goals': request.form.get('special_goals', ''),
                'additional_notes': request.form.get('additional_notes', '')
            }
            
            # Initialize AI agent
            ai_agent = DietAIAgent()
            
            # Prepare user data
            user_data = current_user.to_dict()
            
            # Generate diet plan
            result = ai_agent.generate_diet_plan(user_data, preferences)
            
            if result['success']:
                # Store the generated plan in session or database if needed
                # For now, just pass it to the template
                return render_template('ai_agent/diet_plan_result.html', 
                                     diet_plan=result['diet_plan'],
                                     generated_at=result['generated_at'])
            else:
                flash(f"Failed to generate diet plan: {result.get('message', 'Unknown error')}", 'danger')
                return redirect(url_for('ai_agent.generate_diet_plan'))
                
        except Exception as e:
            logger.error(f"Error generating diet plan: {str(e)}")
            flash('An error occurred while generating the diet plan.', 'danger')
            return redirect(url_for('ai_agent.generate_diet_plan'))
    
    # GET request - show the form
    return render_template('ai_agent/generate_diet_plan.html')

@ai_agent_bp.route('/meal-alternatives', methods=['POST'])
@login_required
def suggest_meal_alternatives():
    """Suggest alternative meals via AJAX"""
    try:
        data = request.get_json()
        current_meal = data.get('current_meal', '').strip()
        restrictions = data.get('restrictions', [])
        
        if not current_meal:
            return jsonify({
                'success': False,
                'error': 'Please provide a current meal'
            }), 400
        
        # Initialize AI agent
        ai_agent = DietAIAgent()
        
        # Prepare user data
        user_data = current_user.to_dict()
        
        # Get meal alternatives
        result = ai_agent.suggest_meal_alternatives(current_meal, user_data, restrictions)
        
        if result['success']:
            return jsonify({
                'success': True,
                'alternatives': result['alternatives'],
                'generated_at': result['generated_at']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to get alternatives'),
                'message': result.get('message', '')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in suggest_meal_alternatives: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@ai_agent_bp.route('/quick-tips')
@login_required
def quick_tips():
    """Provide quick nutrition tips based on user profile"""
    try:
        # Initialize AI agent
        ai_agent = DietAIAgent()
        
        # Prepare user data
        user_data = current_user.to_dict()
        
        # Generate personalized quick tips
        question = "Give me 5 quick nutrition tips based on my profile and goals"
        result = ai_agent.answer_nutrition_question(question, user_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'tips': result['answer'],
                'generated_at': result['generated_at']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to get tips'),
                'message': result.get('message', '')
            }), 500
            
    except Exception as e:
        logger.error(f"Error getting quick tips: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@ai_agent_bp.route('/analyze-progress')
@login_required
def analyze_progress():
    """Analyze user's diet progress and provide insights"""
    try:
        # Get user's recent progress data
        from models import DailySummary
        from datetime import date, timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        recent_summaries = DailySummary.query.filter(
            DailySummary.user_id == current_user.id,
            DailySummary.date >= start_date,
            DailySummary.date <= end_date
        ).all()
        
        # Prepare progress data for AI analysis
        progress_data = []
        for summary in recent_summaries:
            progress_data.append({
                'date': summary.date.isoformat(),
                'calories': summary.total_calories,
                'protein': summary.total_protein,
                'carbs': summary.total_carbs,
                'fat': summary.total_fat,
                'calorie_goal': summary.calorie_goal
            })
        
        # Initialize AI agent
        ai_agent = DietAIAgent()
        
        # Prepare user data with progress
        user_data = current_user.to_dict()
        user_data['recent_progress'] = progress_data
        
        # Ask AI to analyze progress
        question = f"Analyze my diet progress from the last 7 days and provide insights and recommendations. Here's my data: {json.dumps(progress_data)}"
        result = ai_agent.answer_nutrition_question(question, user_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'analysis': result['answer'],
                'progress_data': progress_data,
                'generated_at': result['generated_at']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to analyze progress'),
                'message': result.get('message', '')
            }), 500
            
    except Exception as e:
        logger.error(f"Error analyzing progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500