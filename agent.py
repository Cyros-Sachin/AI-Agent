import requests
import logging
from typing import Optional
from config import Config

# Set up logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

class PlanGenerator:
    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {Config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

    def generate_plan(self, task: str, context: Optional[str] = None) -> str:
        """
        Generate an execution plan for the given task using Groq AI.
        
        Args:
            task: The task to accomplish
            context: Additional context about previous attempts or requirements
            
        Returns:
            The generated plan as a string
        """
        logger.info("🤖 Generating plan using Groq AI...")
        
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that creates detailed execution plans for technical tasks. Provide clear, executable commands with necessary explanations."},
            {"role": "user", "content": f"Task: {task}"}
        ]
        
        if context:
            messages.insert(1, {"role": "assistant", "content": context})

        data = {
            "model": Config.DEFAULT_MODEL,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4000
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            logger.debug(f"Generated plan: {content}")
            return content
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"Failed to generate plan: {str(e)}")