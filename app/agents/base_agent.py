"""
Base Agent Class
Defines common interface for all AI agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os

class BaseAgent(ABC):
    """Abstract base class for all AI agents"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM connection if available"""
        llm_provider = os.getenv("LLM_PROVIDER", "huggingface")
        
        try:
            if llm_provider == "ollama":
                from langchain.llms import Ollama
                return Ollama(model=os.getenv("OLLAMA_MODEL", "mistral"))
            else:  # huggingface
                from langchain.llms import HuggingFaceHub
                return HuggingFaceHub(
                    repo_id=os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.1"),
                    model_kwargs={"temperature": 0.5, "max_length": 500}
                )
        except Exception:
            # LangChain LLM bindings may not be installed in this environment.
            return None
    
    @abstractmethod
    def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input and return response"""
        pass
    
    def _format_response(self, content: str, structured_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Format agent response"""
        return {
            "agent": self.name,
            "role": self.role,
            "response": content,
            "data": structured_data or {}
        }
    
    def generate_prompt(self, template: str, **kwargs) -> str:
        """Generate formatted prompt"""
        return template.format(**kwargs)

class SimpleAgent(BaseAgent):
    """Simplified agent that uses basic rules instead of LLM (faster for demo)"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.llm = None
    
    def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input with simple rule-based logic"""
        return {
            "agent": self.name,
            "response": f"Processing: {user_input}",
            "data": {}
        }
