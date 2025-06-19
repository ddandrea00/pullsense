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
        Analyze a PR with real code diff if available.
        """
        if not self.client:
            return self._mock_analysis(pr_data)
        
        try:
            # Build enhanced prompt with code diff
            diff_section = ""
            if pr_data.get("diff_data") and pr_data["diff_data"].get("files"):
                diff_section = "\n\nCode Changes:\n"
                for file in pr_data["diff_data"]["files"][:5]:  # First 5 files
                    diff_section += f"\n--- File: {file['filename']} ---\n"
                    diff_section += f"Status: {file['status']} "
                    diff_section += f"(+{file['additions']} -{file['deletions']})\n"
                    
                    if file.get('patch'):
                        # Limit patch size to prevent token overflow
                        patch = file['patch']
                        if len(patch) > 1500:
                            patch = patch[:1500] + "\n... (truncated)"
                        diff_section += f"```diff\n{patch}\n```\n"
            
            prompt = f"""
            Analyze this pull request:
            
            Title: {pr_data.get('title', 'No title')}
            Description: {pr_data.get('body', 'No description')}
            Author: {pr_data.get('author', 'Unknown')}
            
            Stats:
            - Files changed: {pr_data.get('diff_data', {}).get('changed_files', 0)}
            - Additions: {pr_data.get('diff_data', {}).get('additions', 0)}
            - Deletions: {pr_data.get('diff_data', {}).get('deletions', 0)}
            
            {diff_section}
            
            Provide a comprehensive code review including:
            1. Summary of what the PR accomplishes
            2. Code quality assessment
            3. Potential bugs or issues found in the code
            4. Security considerations
            5. Performance implications
            6. Specific suggestions for improvement
            
            Be specific and reference actual code when possible. Focus on actionable feedback.
            """
            
            # Call OpenAI with enhanced prompt
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert code reviewer. Provide specific, actionable feedback on the code changes."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=800,  # Increased for more detailed analysis
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "status": "completed",
                "analysis": analysis,
                "model": "gpt-3.5-turbo",
                "used_real_diff": bool(diff_section)
            }
            
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "analysis": self._mock_analysis(pr_data)["analysis"],
                "model": "mock (fallback due to error)"
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