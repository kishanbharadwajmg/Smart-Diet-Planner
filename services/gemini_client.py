import google.generativeai as genai
import logging
from typing import Dict, List, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google Gemini AI models"""
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        """Initialize Gemini client
        
        Args:
            api_key: Google AI API key
            model: Model name to use (default: gemini-2.5-flash)
        """
        self.api_key = api_key
        self.model_name = model
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Ensure model name has the correct prefix
                if not self.model_name.startswith('models/'):
                    self.model_name = f'models/{self.model_name}'
                self.model = genai.GenerativeModel(self.model_name)
            except Exception as e:
                logger.error(f"Error configuring Gemini client: {e}")
                self.model = None
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return False
        
        if not self.model:
            logger.warning("Gemini model not initialized")
            return False
        
        try:
            # Test with a simple prompt
            response = self.model.generate_content("Hello")
            return bool(response.text)
        except Exception as e:
            logger.warning(f"Gemini API not available: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        if not self.api_key:
            return []
        
        try:
            models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    models.append(model.name.replace('models/', ''))
            return models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return [self.model_name]
    
    def generate(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> Dict:
        """Generate text using Gemini model
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with 'success', 'text', and optional 'error' keys
        """
        if not self.model:
            return {
                'success': False,
                'error': 'Gemini model not initialized. Check API key configuration.'
            }
        
        try:
            # Prepare the full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            # Configure generation parameters
            # Note: Gemini 2.5 Flash may need higher token limits, avoid very low limits
            generation_config_kwargs = {
                'temperature': 0.7,
                'top_p': 0.9,
                'top_k': 40
            }
            
            # Only set max_output_tokens if it's reasonably high (avoids premature truncation)
            if max_tokens >= 1000:
                generation_config_kwargs['max_output_tokens'] = max_tokens
                
            generation_config = genai.types.GenerationConfig(**generation_config_kwargs)
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Handle different response formats for Gemini 2.5 Flash
            response_text = None
            
            # Try to get text from response
            if hasattr(response, 'text') and response.text:
                response_text = response.text.strip()
            
            if not response_text and hasattr(response, 'candidates') and response.candidates:
                # Check candidates for text
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    response_text = part.text.strip()
                                    break
                    if response_text:
                        break
            
            if response_text:
                return {
                    'success': True,
                    'text': response_text,
                    'model': self.model_name
                }
            else:
                return {
                    'success': False,
                    'error': 'Empty response from Gemini model'
                }
                
        except Exception as e:
            error_msg = str(e)
            
            # Handle common API errors
            if "API_KEY_INVALID" in error_msg:
                error_msg = "Invalid Gemini API key. Please check your configuration."
            elif "QUOTA_EXCEEDED" in error_msg:
                error_msg = "Gemini API quota exceeded. Please try again later or upgrade your plan."
            elif "SAFETY" in error_msg:
                error_msg = "Content was blocked by Gemini safety filters. Please rephrase your request."
            elif "RATE_LIMIT" in error_msg:
                error_msg = "Rate limit exceeded. Please wait a moment and try again."
            
            logger.error(f"Error generating text with Gemini: {error_msg}")
            return {
                'success': False,
                'error': f'Gemini API error: {error_msg}'
            }
    
    def chat(self, messages: List[Dict[str, str]]) -> Dict:
        """Chat with the model using conversation format
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            
        Returns:
            Dict with 'success', 'text', and optional 'error' keys
        """
        if not self.model:
            return {
                'success': False,
                'error': 'Gemini model not initialized. Check API key configuration.'
            }
        
        try:
            # Convert messages to Gemini format
            chat = self.model.start_chat(history=[])
            
            # Process conversation history
            conversation_text = ""
            user_message = ""
            
            for message in messages:
                role = message.get('role', '')
                content = message.get('content', '')
                
                if role == 'system':
                    conversation_text += f"System: {content}\n\n"
                elif role == 'user':
                    user_message = content
                elif role == 'assistant':
                    conversation_text += f"Assistant: {content}\n\nUser: "
            
            # Combine system context with user message
            if conversation_text:
                full_message = f"{conversation_text}{user_message}"
            else:
                full_message = user_message
            
            # Configure generation - same fix as generate method
            generation_config_kwargs = {
                'temperature': 0.7,
                'top_p': 0.9,
                'top_k': 40
            }
            
            # Only set max_output_tokens if it's reasonably high (2000 is fine for chat)
            generation_config_kwargs['max_output_tokens'] = 2000
                
            generation_config = genai.types.GenerationConfig(**generation_config_kwargs)
            
            # Send message and get response
            response = chat.send_message(
                full_message,
                generation_config=generation_config
            )
            
            # Handle different response formats for Gemini 2.5 Flash
            response_text = None
            
            # Try to get text from response
            if hasattr(response, 'text') and response.text:
                response_text = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                # Check candidates for text
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    response_text = part.text.strip()
                                    break
                    if response_text:
                        break
            
            if response_text:
                return {
                    'success': True,
                    'text': response_text,
                    'model': self.model_name
                }
            else:
                return {
                    'success': False,
                    'error': 'Empty response from Gemini model'
                }
                
        except Exception as e:
            error_msg = str(e)
            
            # Handle common API errors
            if "API_KEY_INVALID" in error_msg:
                error_msg = "Invalid Gemini API key. Please check your configuration."
            elif "QUOTA_EXCEEDED" in error_msg:
                error_msg = "Gemini API quota exceeded. Please try again later or upgrade your plan."
            elif "SAFETY" in error_msg:
                error_msg = "Content was blocked by Gemini safety filters. Please rephrase your request."
            elif "RATE_LIMIT" in error_msg:
                error_msg = "Rate limit exceeded. Please wait a moment and try again."
            
            logger.error(f"Error in Gemini chat: {error_msg}")
            return {
                'success': False,
                'error': f'Gemini chat error: {error_msg}'
            }
    
    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        if not self.model:
            return {
                'model_name': self.model_name,
                'status': 'Not initialized',
                'api_key_configured': bool(self.api_key)
            }
        
        return {
            'model_name': self.model_name,
            'status': 'Available' if self.is_available() else 'Unavailable',
            'api_key_configured': bool(self.api_key),
            'available_models': self.list_models()
        }