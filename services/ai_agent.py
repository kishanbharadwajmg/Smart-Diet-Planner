from typing import Dict, List, Optional
import json
import logging
from datetime import datetime, date
from flask import current_app
from .ollama_client import OllamaClient
from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class DietAIAgent:
    """AI Agent for diet planning and nutrition questions"""
    
    def __init__(self, use_gemini: bool = None, use_ollama: bool = None):
        """Initialize the AI agent
        
        Args:
            use_gemini: Use Gemini API (default: from config)
            use_ollama: Use Ollama local model (default: from config)
        """
        # Get preferences from config if not specified
        self.use_gemini = use_gemini if use_gemini is not None else current_app.config.get('USE_GEMINI', True)
        self.use_ollama = use_ollama if use_ollama is not None else current_app.config.get('USE_OLLAMA', True)
        
        # Initialize Gemini client
        if self.use_gemini:
            gemini_api_key = current_app.config.get('GEMINI_API_KEY')
            gemini_model = current_app.config.get('GEMINI_MODEL', 'gemini-2.5-flash')
            self.gemini_client = GeminiClient(gemini_api_key, gemini_model)
        
        # Initialize Ollama client
        if self.use_ollama:
            ollama_url = current_app.config.get('OLLAMA_URL', 'http://localhost:11434')
            ollama_model = current_app.config.get('OLLAMA_MODEL', 'llama2')
            self.ollama_client = OllamaClient(ollama_url, ollama_model)
        
        # OpenAI fallback
        self.openai_api_key = current_app.config.get('OPENAI_API_KEY')
    
    def _generate_with_ai(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> Dict:
        """Generate text using available AI service"""
        
        # Try Gemini first (best reasoning)
        if self.use_gemini and hasattr(self, 'gemini_client'):
            if self.gemini_client.is_available():
                result = self.gemini_client.generate(prompt, system_prompt, max_tokens)
                if result['success']:
                    result['source'] = 'gemini'
                    return result
                else:
                    logger.warning(f"Gemini failed: {result.get('error', 'Unknown error')}")
        
        # Try Ollama as fallback (local/free)
        if self.use_ollama and hasattr(self, 'ollama_client'):
            if self.ollama_client.is_available():
                result = self.ollama_client.generate(prompt, system_prompt, max_tokens)
                if result['success']:
                    result['source'] = 'ollama'
                    return result
                else:
                    logger.warning(f"Ollama failed: {result.get('error', 'Unknown error')}")
        
        # Try OpenAI as final fallback
        if self.openai_api_key:
            try:
                import openai
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                
                return {
                    'success': True,
                    'text': response.choices[0].message.content,
                    'source': 'openai'
                }
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
        
        # All AI services failed
        return {
            'success': False,
            'error': 'All AI services unavailable. Using rule-based fallback.',
            'fallback': True
        }
    
    def generate_diet_plan(self, user_data: Dict, preferences: Dict) -> Dict:
        """Generate a personalized diet plan based on user data and preferences"""
        try:
            # Prepare user profile for AI
            user_profile = self._format_user_profile(user_data, preferences)
            
            # Extract specific user goals
            daily_calories = user_data.get('daily_calorie_goal', 2000)
            protein_goal = user_data.get('protein_goal', 100)
            carb_goal = user_data.get('carb_goal', 250)
            fat_goal = user_data.get('fat_goal', 65)
            activity_level = user_data.get('activity_level', 'Moderate')
            user_preferences = preferences.get('additional_notes', '')
            
            # Enhance protein goal based on activity level if not explicitly set
            if user_data.get('protein_goal') is None:
                weight = user_data.get('weight', 70)
                if activity_level in ['Very Active', 'Highly Active']:
                    protein_goal = max(120, int(weight * 1.8))  # Higher for very active
                elif activity_level in ['Active', 'Moderately Active']:
                    protein_goal = max(100, int(weight * 1.5))  # Moderate for active
                else:
                    protein_goal = max(80, int(weight * 1.2))   # Base for sedentary
            
            prompt = f"""
            As an expert nutritionist specializing in South Indian cuisine, create a HIGHLY PERSONALIZED 7-day diet plan for this specific user:
            
            {user_profile}
            
            CRITICAL NUTRITIONAL TARGETS (MUST BE MET):
            - Daily Calories: EXACTLY {daily_calories} calories (distribute across 5 meals)
            - Daily Protein: MINIMUM {protein_goal}g protein (high priority for {activity_level} person)
            - Daily Carbs: Around {carb_goal}g carbs
            - Daily Fat: Around {fat_goal}g fat
            
            PERSONALIZATION REQUIREMENTS:
            1. CUSTOMIZE portion sizes to meet the EXACT calorie target of {daily_calories} calories
            2. BOOST protein content significantly - include protein-rich South Indian foods
            3. VARY dishes based on user's activity level ({activity_level})
            4. Consider user notes: {user_preferences}
            5. Make it suitable for their age ({user_data.get('age', 30)}) and weight ({user_data.get('weight', 70)}kg)
            
            HIGH-PROTEIN SOUTH INDIAN FOODS TO EMPHASIZE:
            - Essential proteins: Paneer (20g/100g), Sprouts (7g/100g), Dal varieties (25g/100g), Greek yogurt (10g/100g)
            - For {activity_level} person: Larger portions, protein supplements if needed
            - Breakfast: Protein-rich options like Quinoa Upma with paneer (25g protein), Moong Dal Chilla (20g), Sprouts Pongal (18g)
            - Lunch: High-protein combinations like Paneer Biryani (35g), Dal-Rice with curd (30g), Chickpea curry with quinoa (32g)
            - Dinner: Protein-focused meals like Lentil curry with paneer (28g), Mixed dal preparations (25g)
            - Snacks: Protein-rich like Roasted chana (20g), Peanut sundal (15g), Protein smoothies (25g)
            
            PROTEIN DISTRIBUTION STRATEGY (Total: {protein_goal}g):
            - Aim for 20-30g protein per main meal (breakfast, lunch, dinner)
            - Include 10-15g protein in each snack
            - Use protein-dense ingredients: Paneer, Greek yogurt, sprouts, mixed dals, quinoa
            - Consider protein powder in smoothies if natural sources are insufficient
            
            MEAL CALORIE DISTRIBUTION FOR {daily_calories} CALORIES:
            - Breakfast: {int(daily_calories * 0.25)} calories, {int(protein_goal * 0.3)}g protein
            - Morning Snack: {int(daily_calories * 0.10)} calories, {int(protein_goal * 0.1)}g protein  
            - Lunch: {int(daily_calories * 0.35)} calories, {int(protein_goal * 0.35)}g protein
            - Evening Snack: {int(daily_calories * 0.10)} calories, {int(protein_goal * 0.1)}g protein
            - Dinner: {int(daily_calories * 0.20)} calories, {int(protein_goal * 0.25)}g protein
            
            VARIETY REQUIREMENTS:
            - 7 DIFFERENT breakfast options (not just idli every day) - Examples: Day 1: Quinoa Upma, Day 2: Moong Dal Chilla, Day 3: Sprouted Ragi Dosa, Day 4: Paneer Stuffed Uttapam, Day 5: Oats Pongal, Day 6: Protein Smoothie Bowl, Day 7: Mixed Dal Adai
            - Mix traditional and modern South Indian dishes with protein enhancements
            - Include regional varieties (Tamil: Chettinad dishes, Kerala: Appam variations, Karnataka: Bisi Bele Bath, Andhra: Pesarattu)
            - Seasonal vegetables and fruits with focus on protein-rich combinations
            - Different cooking methods (steamed, grilled, curry, dry preparations) but ensure adequate protein in each
            
            PERSONALIZATION FOR THIS USER:
            - Age {user_data.get('age', 30)}: {'Metabolism-boosting foods' if user_data.get('age', 30) < 30 else 'Nutrient-dense, easily digestible options' if user_data.get('age', 30) > 50 else 'Balanced energy foods'}
            - Weight {user_data.get('weight', 70)}kg: {'Portion control focus' if user_data.get('weight', 70) > 80 else 'Adequate portions for energy'}
            - Activity level {activity_level}: {'Pre/post workout meal timing' if 'Active' in activity_level else 'Steady energy throughout day'}
            - Gender {user_data.get('gender', 'Unknown')}: {'Iron-rich foods' if user_data.get('gender') == 'Female' else 'Higher calorie density' if user_data.get('gender') == 'Male' else 'Balanced approach'}
            
            Format as JSON with ACCURATE nutritional values:
            {{
                "diet_plan": {{
                    "day_1": {{
                        "breakfast": {{
                            "name": "Protein-rich specific dish (e.g., Quinoa Vegetable Upma with Paneer)",
                            "calories": {int(daily_calories * 0.25)},
                            "protein": {int(protein_goal * 0.30)},
                            "carbs": {int(carb_goal * 0.25)},
                            "fat": {int(fat_goal * 0.25)},
                            "ingredients": ["detailed quantities like 1 cup quinoa, 100g paneer, 2 tbsp oil"],
                            "instructions": "Detailed step-by-step preparation"
                        }},
                        "morning_snack": {{
                            "name": "High-protein snack",
                            "calories": {int(daily_calories * 0.10)},
                            "protein": {int(protein_goal * 0.10)},
                            "carbs": {int(carb_goal * 0.10)},
                            "fat": {int(fat_goal * 0.10)},
                            "ingredients": ["specific quantities"],
                            "instructions": "preparation method"
                        }},
                        "lunch": {{
                            "name": "Substantial protein-rich lunch",
                            "calories": {int(daily_calories * 0.35)},
                            "protein": {int(protein_goal * 0.35)},
                            "carbs": {int(carb_goal * 0.35)},
                            "fat": {int(fat_goal * 0.35)},
                            "ingredients": ["detailed ingredients with exact quantities"],
                            "instructions": "complete cooking instructions"
                        }},
                        "evening_snack": {{
                            "name": "Protein-focused evening snack",
                            "calories": {int(daily_calories * 0.10)},
                            "protein": {int(protein_goal * 0.10)},
                            "carbs": {int(carb_goal * 0.10)},
                            "fat": {int(fat_goal * 0.10)},
                            "ingredients": ["ingredient list"],
                            "instructions": "preparation method"
                        }},
                        "dinner": {{
                            "name": "Light but protein-rich dinner",
                            "calories": {int(daily_calories * 0.20)},
                            "protein": {int(protein_goal * 0.25)},
                            "carbs": {int(carb_goal * 0.20)},
                            "fat": {int(fat_goal * 0.20)},
                            "ingredients": ["complete ingredient list with quantities"],
                            "instructions": "detailed cooking method"
                        }}
                    }},
                    "day_2": {{ ... 6 more days with COMPLETELY DIFFERENT dishes ... }}
                }},
                "nutritional_summary": {{
                    "daily_average": {{"calories": {daily_calories}, "protein": {protein_goal}, "carbs": {carb_goal}, "fat": {fat_goal}}},
                    "weekly_total": {{"calories": {daily_calories * 7}, "protein": {protein_goal * 7}, "carbs": {carb_goal * 7}, "fat": {fat_goal * 7}}}
                }},
                "shopping_list": [
                    "HIGH-PROTEIN ESSENTIALS for {activity_level} person:",
                    "Quinoa (1 kg) - complete protein grain", "Paneer (1 kg) - 20g protein/100g", 
                    "Mixed dals - Moong, Chana, Masoor (3 kg total)", "Greek yogurt (2 liters) - probiotic protein",
                    "Fresh sprouts - Moong, Chana (1 kg)", "Nuts: Almonds, peanuts, walnuts (500g each)",
                    "Seeds: Chia, flax, sunflower (250g each)", "Protein powder (optional - 1 container)",
                    "Tofu/soy products (500g)", "Eggs (2 dozen)", "Cottage cheese ingredients",
                    "Protein-rich vegetables: Spinach, broccoli, peas", "Seasonal fruits for smoothies"
                ],
                "tips": [
                    "PROTEIN OPTIMIZATION for {activity_level} lifestyle:",
                    "Combine dals with quinoa/brown rice for complete proteins",
                    "Add paneer/tofu to traditional dishes (upma, biryani, curries)",
                    "Start each meal with protein-rich items to boost satiety",
                    "Prep protein smoothies with Greek yogurt + fruits for quick snacks",
                    "Soak nuts/seeds overnight for better protein absorption",
                    "Use sprouted legumes - 30% more protein than regular",
                    "Meal timing: Spread {protein_goal}g protein across 5 meals (20-30g each)",
                    "Hydration: 3-4 liters water daily for {activity_level} person",
                    "Post-workout: Have protein within 30 minutes for muscle recovery"
                ],
                "meal_timing": {{
                    "7:30 AM": "Breakfast ({int(daily_calories * 0.25)} cal)",
                    "10:30 AM": "Morning Snack ({int(daily_calories * 0.10)} cal)", 
                    "1:00 PM": "Lunch ({int(daily_calories * 0.35)} cal)",
                    "4:30 PM": "Evening Snack ({int(daily_calories * 0.10)} cal)",
                    "8:00 PM": "Dinner ({int(daily_calories * 0.20)} cal)"
                }}
            }}
            """
            
            system_prompt = "You are a professional nutritionist specializing in South Indian cuisine with deep knowledge of traditional recipes, ingredients, and cooking methods. Provide authentic South Indian meal plans with specific dish names, detailed ingredients, and proper cooking instructions. Always ensure nutritional accuracy and cultural authenticity."
            
            # Generate response using AI (increased tokens for detailed recipes)
            ai_result = self._generate_with_ai(prompt, system_prompt, 8000)
            
            if not ai_result['success']:
                # Fallback to rule-based diet plan
                return self._generate_fallback_diet_plan(user_data, preferences)
            
            diet_plan_text = ai_result['text']
            
            # Try to extract JSON from response (handle markdown code blocks)
            try:
                # Remove markdown code block markers if present
                clean_text = diet_plan_text.replace('```json', '').replace('```', '').strip()
                
                # Handle multiple JSON objects by finding the largest one
                json_candidates = []
                brace_count = 0
                start_idx = -1
                
                for i, char in enumerate(clean_text):
                    if char == '{':
                        if brace_count == 0:
                            start_idx = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and start_idx != -1:
                            json_candidates.append(clean_text[start_idx:i+1])
                
                # Try parsing each JSON candidate
                for json_str in json_candidates:
                    try:
                        diet_plan = json.loads(json_str)
                        # Validate that it has the expected structure
                        if 'diet_plan' in diet_plan or 'breakfast' in str(diet_plan):
                            logger.info("Successfully parsed diet plan JSON from AI response")
                            break
                    except json.JSONDecodeError:
                        continue
                else:
                    # No valid JSON found
                    logger.warning("No valid JSON found in AI response, using fallback parser")
                    diet_plan = self._parse_diet_plan_from_text(diet_plan_text)
                    
            except Exception as e:
                logger.warning(f"JSON parsing error: {e}, using fallback parser")
                diet_plan = self._parse_diet_plan_from_text(diet_plan_text)
            
            return {
                'success': True,
                'diet_plan': diet_plan,
                'generated_at': datetime.utcnow().isoformat(),
                'source': ai_result.get('source', 'ai')
            }
            
        except Exception as e:
            logger.error(f"Error generating diet plan: {str(e)}")
            # Fallback to rule-based plan
            return self._generate_fallback_diet_plan(user_data, preferences)
    
    def answer_nutrition_question(self, question: str, user_data: Dict) -> Dict:
        """Answer nutrition-related questions based on user profile"""
        try:
            user_profile = self._format_user_profile(user_data)
            
            prompt = f"""
            As a nutrition expert, answer this question for a user with the following profile:
            
            {user_profile}
            
            Question: {question}
            
            Please provide:
            1. A clear, evidence-based answer
            2. Specific recommendations for this user
            3. Any relevant warnings or considerations
            4. Actionable next steps if applicable
            
            Keep the response conversational but professional, and tailor it to the user's specific situation.
            """
            
            system_prompt = "You are a professional nutritionist providing personalized advice. Always give safe, evidence-based recommendations and remind users to consult healthcare providers for medical concerns."
            
            # Generate response using AI
            ai_result = self._generate_with_ai(prompt, system_prompt, 800)
            
            if not ai_result['success']:
                # Fallback to rule-based answer
                return self._generate_fallback_answer(question, user_data)
            
            return {
                'success': True,
                'answer': ai_result['text'],
                'generated_at': datetime.utcnow().isoformat(),
                'source': ai_result.get('source', 'ai')
            }
            
        except Exception as e:
            logger.error(f"Error answering nutrition question: {str(e)}")
            return self._generate_fallback_answer(question, user_data)
    
    def suggest_meal_alternatives(self, current_meal: str, user_data: Dict, restrictions: List[str] = None) -> Dict:
        """Suggest alternative meals based on user preferences and restrictions"""
        try:
            user_profile = self._format_user_profile(user_data)
            restrictions_text = ", ".join(restrictions) if restrictions else "None specified"
            
            prompt = f"""
            Suggest 5 healthy alternative meals for a user with this profile:
            
            {user_profile}
            
            Current meal: {current_meal}
            Additional restrictions: {restrictions_text}
            
            Provide alternatives that:
            1. Have similar nutritional value
            2. Fit the user's dietary preferences
            3. Are practical to prepare
            4. Include ingredient lists and basic instructions
            
            Format as JSON:
            {{
                "alternatives": [
                    {{"name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "ingredients": [], "instructions": "...", "prep_time": "..."}}
                ]
            }}
            """
            
            system_prompt = "You are a nutritionist providing meal alternatives. Focus on practical, healthy options."
            
            # Generate response using AI
            ai_result = self._generate_with_ai(prompt, system_prompt, 1500)
            
            if not ai_result['success']:
                # Fallback to rule-based alternatives
                return self._generate_fallback_alternatives(current_meal, user_data, restrictions)
            
            alternatives_text = ai_result['text']
            
            # Parse JSON response
            try:
                start_idx = alternatives_text.find('{')
                end_idx = alternatives_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = alternatives_text[start_idx:end_idx]
                    alternatives = json.loads(json_str)
                else:
                    alternatives = {"alternatives": []}
            except json.JSONDecodeError:
                alternatives = {"alternatives": []}
            
            return {
                'success': True,
                'alternatives': alternatives.get('alternatives', []),
                'generated_at': datetime.utcnow().isoformat(),
                'source': ai_result.get('source', 'ai')
            }
            
        except Exception as e:
            logger.error(f"Error suggesting meal alternatives: {str(e)}")
            return self._generate_fallback_alternatives(current_meal, user_data, restrictions)
    
    def _format_user_profile(self, user_data: Dict, preferences: Dict = None) -> str:
        """Format user data into a readable profile for AI prompts"""
        profile_parts = [
            f"Age: {user_data.get('age', 'Not specified')}",
            f"Gender: {user_data.get('gender', 'Not specified')}",
            f"Height: {user_data.get('height', 'Not specified')} cm",
            f"Weight: {user_data.get('weight', 'Not specified')} kg",
            f"Activity Level: {user_data.get('activity_level', 'Not specified')}",
            f"Food Preferences: {user_data.get('food_preferences', 'Not specified')}",
            f"Is Diabetic: {'Yes' if user_data.get('is_diabetic') else 'No'}",
            f"Daily Calorie Goal: {user_data.get('daily_calorie_goal', 'Not set')} calories",
            f"Protein Goal: {user_data.get('protein_goal', 'Not set')} grams",
            f"Carb Goal: {user_data.get('carb_goal', 'Not set')} grams",
            f"Fat Goal: {user_data.get('fat_goal', 'Not set')} grams"
        ]
        
        if user_data.get('disliked_foods'):
            disliked = user_data['disliked_foods']
            if isinstance(disliked, list) and disliked:
                profile_parts.append(f"Disliked Foods: {', '.join(map(str, disliked))}")
        
        if preferences:
            profile_parts.append(f"Additional Preferences: {preferences}")
        
        return "\n".join(profile_parts)
    
    def _parse_diet_plan_from_text(self, text: str) -> Dict:
        """Fallback method to parse diet plan from unstructured text"""
        logger.info("Using fallback text parser for diet plan")
        
        # Try to extract meal names from the text
        meals = {
            "breakfast": {"name": "Protein-Enhanced Idli with Sambhar", "calories": 350, "protein": 18, "carbs": 45, "fat": 12},
            "morning_snack": {"name": "Sprouted Moong Sundal", "calories": 150, "protein": 8, "carbs": 20, "fat": 4},
            "lunch": {"name": "Paneer Biryani with Raita", "calories": 550, "protein": 25, "carbs": 65, "fat": 18},
            "evening_snack": {"name": "Protein Smoothie", "calories": 180, "protein": 12, "carbs": 15, "fat": 6},
            "dinner": {"name": "Mixed Dal with Quinoa", "calories": 420, "protein": 22, "carbs": 55, "fat": 10}
        }
        
        # Look for specific South Indian dishes in the text
        south_indian_dishes = [
            "idli", "dosa", "sambhar", "rasam", "upma", "vada", "uttapam", 
            "appam", "puttu", "pongal", "curd rice", "coconut chutney"
        ]
        
        text_lower = text.lower()
        found_dishes = [dish for dish in south_indian_dishes if dish in text_lower]
        
        if found_dishes:
            # If we found South Indian dishes, try to create a more appropriate plan
            if "idli" in text_lower:
                meals["breakfast"]["name"] = "Idli with Sambhar and Coconut Chutney"
            if "dosa" in text_lower:
                meals["lunch"]["name"] = "Masala Dosa with Sambhar"
            if "curd rice" in text_lower or "rasam" in text_lower:
                meals["dinner"]["name"] = "Curd Rice with Rasam"
        
        return {
            "diet_plan": {
                "day_1": meals
            },
            "nutritional_summary": {
                "daily_average": {"calories": 1650, "protein": 85, "carbs": 200, "fat": 50}
            },
            "shopping_list": ["Rice (2 kg)", "Urad dal (500g)", "Coconut (2 pieces)", "Vegetables", "Spices", "Curd (500ml)"],
            "tips": ["Prepare idli/dosa batter in advance", "Use fresh coconut for chutneys", "Cook sambhar in larger batches"],
            "raw_response": text[:500] + "..." if len(text) > 500 else text
        }
    
    def _generate_fallback_diet_plan(self, user_data: Dict, preferences: Dict) -> Dict:
        """Generate a basic rule-based diet plan when AI is unavailable"""
        calories = user_data.get('daily_calorie_goal', 2000)
        is_vegetarian = user_data.get('food_preferences', '').lower() == 'vegetarian'
        is_diabetic = user_data.get('is_diabetic', False)
        
        # Simple meal templates
        if is_vegetarian:
            breakfast = {"name": "Oatmeal with Berries", "calories": 300, "protein": 12, "carbs": 55, "fat": 8}
            lunch = {"name": "Quinoa Salad Bowl", "calories": 450, "protein": 18, "carbs": 65, "fat": 15}
            dinner = {"name": "Lentil Curry with Rice", "calories": 400, "protein": 20, "carbs": 60, "fat": 12}
        else:
            breakfast = {"name": "Scrambled Eggs with Toast", "calories": 320, "protein": 18, "carbs": 30, "fat": 15}
            lunch = {"name": "Grilled Chicken Salad", "calories": 420, "protein": 35, "carbs": 25, "fat": 20}
            dinner = {"name": "Baked Fish with Vegetables", "calories": 380, "protein": 30, "carbs": 25, "fat": 18}
        
        # Create 7-day plan (simplified)
        diet_plan = {}
        for day in range(1, 8):
            diet_plan[f"day_{day}"] = {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner
            }
        
        return {
            'success': True,
            'diet_plan': {
                "diet_plan": diet_plan,
                "nutritional_summary": {
                    "daily_average": {"calories": calories, "protein": 85, "carbs": 140, "fat": 53}
                },
                "shopping_list": ["Eggs", "Chicken", "Fish", "Vegetables", "Grains"],
                "tips": ["Eat balanced meals", "Stay hydrated", "Exercise regularly"]
            },
            'generated_at': datetime.utcnow().isoformat(),
            'source': 'fallback'
        }
    
    def _generate_fallback_answer(self, question: str, user_data: Dict) -> Dict:
        """Generate a detailed rule-based answer when AI is unavailable"""
        question_lower = question.lower()
        
        # Get user-specific data
        name = user_data.get('first_name', 'there')
        age = user_data.get('age', 30)
        gender = user_data.get('gender', 'Unknown')
        weight = user_data.get('weight', 70)
        activity = user_data.get('activity_level', 'Moderately Active')
        calories = user_data.get('daily_calorie_goal', 2000)
        is_vegetarian = user_data.get('food_preferences', '').lower() == 'vegetarian'
        is_diabetic = user_data.get('is_diabetic', False)
        
        # Enhanced rule-based responses
        if 'protein' in question_lower:
            protein_goal = user_data.get('protein_goal', 70)
            if is_vegetarian:
                answer = f"Hi {name}! Based on your vegetarian preferences and {activity.lower()} lifestyle, aim for {protein_goal}g of protein daily. Great sources include: lentils (18g per cup), Greek yogurt (20g per cup), quinoa (8g per cup), tofu (20g per cup), eggs (6g each), and nuts/seeds. Try having protein with each meal - like oatmeal with nuts for breakfast, quinoa salad for lunch, and lentil curry for dinner."
            else:
                answer = f"Hi {name}! For your {activity.lower()} lifestyle, target {protein_goal}g of protein daily. Top sources: chicken breast (25g per 100g), fish (20-25g per 100g), eggs (6g each), Greek yogurt (20g per cup), beans (15g per cup). Spread it across meals: 20-25g at breakfast, lunch, and dinner."
        
        elif 'calorie' in question_lower or 'weight' in question_lower:
            if 'lose' in question_lower or 'loss' in question_lower:
                deficit_calories = max(1200, calories - 500)
                answer = f"Hi {name}! For healthy weight loss, aim for {deficit_calories} calories (500 below your {calories} goal). Focus on protein-rich foods to maintain muscle, include plenty of vegetables, and choose whole grains. Track your food and aim to lose 1-2 pounds per week safely."
            elif 'gain' in question_lower:
                surplus_calories = calories + 300
                answer = f"Hi {name}! For healthy weight gain, target {surplus_calories} calories daily. Add calorie-dense healthy foods like nuts, avocados, olive oil, and protein smoothies. Eat every 3-4 hours and focus on strength training to build muscle."
            else:
                answer = f"Hi {name}! Your daily calorie goal is {calories} calories. Based on your {activity.lower()} lifestyle, this should support your current weight of {weight}kg. Focus on nutrient-dense whole foods and balanced meals."
        
        elif 'breakfast' in question_lower:
            if is_vegetarian:
                answer = f"Hi {name}! Great vegetarian breakfast ideas: Overnight oats with berries and nuts (300 cal), avocado toast with eggs (350 cal), Greek yogurt parfait with granola (280 cal), or a green smoothie with protein powder (250 cal). Aim for 20g protein to keep you satisfied until lunch."
            else:
                answer = f"Hi {name}! Balanced breakfast options: Scrambled eggs with whole grain toast (320 cal), Greek yogurt with berries (250 cal), oatmeal with protein powder (300 cal), or a veggie omelet (280 cal). Include protein, healthy fats, and complex carbs for sustained energy."
        
        elif 'lunch' in question_lower:
            if is_vegetarian:
                answer = f"Hi {name}! Satisfying vegetarian lunches: Quinoa Buddha bowl with chickpeas (450 cal), lentil soup with whole grain bread (400 cal), veggie wrap with hummus (380 cal), or caprese salad with extra protein (350 cal). Add healthy fats like avocado or nuts."
            else:
                answer = f"Hi {name}! Balanced lunch ideas: Grilled chicken salad (400 cal), turkey and avocado wrap (420 cal), salmon with quinoa (450 cal), or chicken soup with vegetables (350 cal). Include lean protein, vegetables, and complex carbs."
        
        elif 'dinner' in question_lower:
            if is_vegetarian:
                answer = f"Hi {name}! Nutritious vegetarian dinners: Lentil curry with brown rice (420 cal), stuffed bell peppers with quinoa (380 cal), vegetable stir-fry with tofu (360 cal), or black bean tacos (400 cal). Make vegetables the star of your plate."
            else:
                answer = f"Hi {name}! Healthy dinner options: Baked fish with roasted vegetables (380 cal), lean beef stir-fry (420 cal), chicken breast with sweet potato (400 cal), or turkey meatballs with zucchini noodles (350 cal). Fill half your plate with vegetables."
        
        elif 'snack' in question_lower:
            answer = f"Hi {name}! Healthy snacks for your {activity.lower()} lifestyle: Apple with almond butter (190 cal), Greek yogurt with berries (150 cal), handful of nuts (160 cal), veggie sticks with hummus (120 cal), or protein smoothie (180 cal). Choose snacks with protein and fiber to stay satisfied."
        
        elif 'water' in question_lower or 'hydration' in question_lower:
            water_goal = max(8, weight * 0.035)  # 35ml per kg
            answer = f"Hi {name}! Aim for {water_goal:.1f} cups of water daily based on your {weight}kg weight and {activity.lower()} lifestyle. Start your day with a glass, drink before meals, and carry a water bottle. Increase intake during exercise or hot weather."
        
        elif 'exercise' in question_lower or 'workout' in question_lower:
            if 'before' in question_lower:
                answer = f"Hi {name}! Pre-workout nutrition: Eat 30-60 minutes before exercising. Good options: banana with peanut butter, oatmeal with berries, or Greek yogurt with granola. Focus on easily digestible carbs with a little protein."
            elif 'after' in question_lower:
                answer = f"Hi {name}! Post-workout nutrition: Eat within 30 minutes after exercise. Combine protein and carbs: chocolate milk, protein smoothie with fruit, or Greek yogurt with berries. Aim for 20-30g protein to support muscle recovery."
            else:
                answer = f"Hi {name}! For your {activity.lower()} lifestyle, fuel your workouts with balanced nutrition. Eat regularly, stay hydrated, and consider timing your meals around exercise for optimal performance and recovery."
        
        elif 'diabetic' in question_lower or is_diabetic:
            answer = f"Hi {name}! For diabetes management: Focus on low glycemic foods (vegetables, lean proteins, whole grains), eat regular meals to stabilize blood sugar, portion control, and pair carbs with protein or fiber. Monitor your blood sugar and work with your healthcare team for personalized advice."
        
        elif 'vitamin' in question_lower or 'supplement' in question_lower:
            answer = f"Hi {name}! Consider these nutrients: Vitamin D (especially if limited sun exposure), B12 ({'essential' if is_vegetarian else 'important'} for vegetarians), Omega-3s (from fish or algae), and a basic multivitamin. Focus on getting nutrients from whole foods first, then supplement as needed. Consult your doctor for personalized recommendations."
        
        else:
            answer = f"Hi {name}! Based on your profile ({age} years, {gender.lower()}, {activity.lower()}), focus on: eating {calories} calories daily with balanced macros, staying hydrated, choosing whole foods over processed ones, and eating regular meals. {'As a vegetarian' if is_vegetarian else ''}{', manage blood sugar carefully' if is_diabetic else ''}. Consider consulting a registered dietitian for detailed personalized guidance."
        
        # Add a note about AI unavailability
        answer += f"\n\n⚠️ Note: AI assistant is currently unavailable. This is a rule-based response. For more personalized advice, ensure Ollama is running with a nutrition model installed."
        
        return {
            'success': True,
            'answer': answer,
            'generated_at': datetime.utcnow().isoformat(),
            'source': 'fallback'
        }
    
    def _generate_fallback_alternatives(self, current_meal: str, user_data: Dict, restrictions: List[str] = None) -> Dict:
        """Generate basic meal alternatives when AI is unavailable"""
        is_vegetarian = user_data.get('food_preferences', '').lower() == 'vegetarian'
        
        # Simple alternatives based on meal type
        if 'chicken' in current_meal.lower():
            if is_vegetarian:
                alternatives = [
                    {"name": "Grilled Tofu", "calories": 200, "protein": 20, "carbs": 5, "fat": 12},
                    {"name": "Lentil Patty", "calories": 180, "protein": 15, "carbs": 25, "fat": 5}
                ]
            else:
                alternatives = [
                    {"name": "Grilled Fish", "calories": 220, "protein": 25, "carbs": 0, "fat": 12},
                    {"name": "Turkey Breast", "calories": 200, "protein": 22, "carbs": 0, "fat": 10}
                ]
        else:
            # Generic healthy alternatives
            alternatives = [
                {"name": "Mixed Green Salad", "calories": 150, "protein": 8, "carbs": 15, "fat": 8},
                {"name": "Vegetable Soup", "calories": 120, "protein": 6, "carbs": 20, "fat": 3},
                {"name": "Quinoa Bowl", "calories": 250, "protein": 12, "carbs": 40, "fat": 6}
            ]
        
        return {
            'success': True,
            'alternatives': alternatives,
            'generated_at': datetime.utcnow().isoformat(),
            'source': 'fallback'
        }