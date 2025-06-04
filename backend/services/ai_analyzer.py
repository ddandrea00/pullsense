import openai
import json
from typing import Dict, Optional
from config import settings

class CodeAnalyzer:
    """Handles AI analysis of pull requests"""
    
    def __init__(self):
        # Only initialize if we have an API key
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            print("✅ OpenAI client initialized")
        else:
            self.client = None
            print("⚠️  No OpenAI API key - using mock analysis")
    
    def analyze_pr(self, pr_data: dict) -> dict:
        """
        Analyze a PR and return structured feedback.
        In a real job, you'd iterate on this prompt many times!
        """
        if not self.client:
            return self._mock_analysis(pr_data)
        
        try:
            # Build the prompt
            prompt = f"""
            Analyze this pull request:
            
            Title: {pr_data.get('title', 'No title')}
            Description: {pr_data.get('body', 'No description')}
            Author: {pr_data.get('author', 'Unknown')}
            
            Provide a brief analysis including:
            1. What this PR does
            2. Any potential issues
            3. Suggestions for improvement
            
            Keep it concise and constructive.
            """
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cheaper for testing
                messages=[
                    {"role": "system", "content": "You are a helpful code reviewer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "status": "completed",
                "analysis": analysis,
                "model": "gpt-3.5-turbo"
            }
            
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback": self._mock_analysis(pr_data)
            }
    
    def _mock_analysis(self, pr_data: dict) -> dict:
        """Mock analysis when no API key is available"""
        return {
            "status": "mock",
            "analysis": f"Mock analysis for '{pr_data.get('title', 'Unknown PR')}':\n"
                       f"- Looks good overall\n"
                       f"- Consider adding tests\n"
                       f"- Check error handling",
            "model": "mock"
        }

# Initialize singleton
analyzer = CodeAnalyzer()