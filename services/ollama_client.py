import requests
import json
import logging
from typing import Dict, List, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama local AI models"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """Initialize Ollama client
        
        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
            model: Model name to use (default: llama2)
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        self.session.timeout = 60  # 60 second timeout
    
    def is_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama server not available: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def generate(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> Dict:
        """Generate text using Ollama model
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with 'success', 'text', and optional 'error' keys
        """
        try:
            # Prepare the full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "stop": ["User:", "Human:"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120  # 2 minutes for generation
            )
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data.get('response', '').strip()
                
                if generated_text:
                    return {
                        'success': True,
                        'text': generated_text,
                        'model': self.model
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Empty response from model'
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout - model may be too slow'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Cannot connect to Ollama server. Make sure Ollama is running.'
            }
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return {
                'success': False,
                'error': f'Generation error: {str(e)}'
            }
    
    def chat(self, messages: List[Dict[str, str]]) -> Dict:
        """Chat with the model using conversation format
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            
        Returns:
            Dict with 'success', 'text', and optional 'error' keys
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})
                content = message.get('content', '').strip()
                
                if content:
                    return {
                        'success': True,
                        'text': content,
                        'model': self.model
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Empty response from model'
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                'success': False,
                'error': f'Chat error: {str(e)}'
            }