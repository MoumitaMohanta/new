import logging
import json
from typing import Optional
from anthropic import Anthropic
from src.config import settings
from src.schemas import ReviewIssueSchema, IssueSeverity

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with Anthropic Claude API"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
    
    async def review_code(
        self,
        code: str,
        language: str,
        filename: Optional[str] = None
    ) -> dict:
        """
        Perform comprehensive code review using Claude
        
        Args:
            code: The code to review
            language: Programming language
            filename: Optional filename for context
            
        Returns:
            Dictionary with review results
        """
        try:
            prompt = self._build_review_prompt(code, language, filename)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            review_result = self._parse_review_response(response_text, code)
            
            logger.info(f"Code review completed for {filename or 'untitled'}")
            return review_result
            
        except Exception as e:
            logger.error(f"Error reviewing code: {str(e)}")
            raise
    
    def _build_review_prompt(self, code: str, language: str, filename: Optional[str]) -> str:
        """Build the review prompt for Claude"""
        
        filename_context = f"File: {filename}\n" if filename else ""
        
        prompt = f"""You are an expert code reviewer. Analyze the following {language} code and provide a comprehensive review.

{filename_context}Language: {language}

CODE TO REVIEW:
```{language}
{code}
```

Please provide your analysis in the following JSON format:
{{
    "summary": "Brief overview of code quality",
    "score": <0-10 float>,
    "complexity": <1-10 int>,
    "maintainability": <0-10 float>,
    "security_score": <0-10 float>,
    "performance_score": <0-10 float>,
    "issues": [
        {{
            "severity": "info|warning|error|critical",
            "category": "security|performance|style|logic|testing",
            "message": "Description of the issue",
            "line": <line number>,
            "suggestion": "How to fix this"
        }}
    ],
    "suggestions": ["List", "of", "general", "improvements"]
}}

Analyze the code for:
1. Security vulnerabilities
2. Performance issues
3. Code style and best practices
4. Logic errors
5. Testing coverage gaps
6. Maintainability concerns
7. Documentation

Be thorough but constructive. Focus on actionable feedback."""
        
        return prompt
    
    def _parse_review_response(self, response: str, code: str) -> dict:
        """Parse Claude's response into structured review data"""
        try:
            # Extract JSON from response (Claude might add extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("Could not find JSON in response")
            
            json_str = response[json_start:json_end]
            review_data = json.loads(json_str)
            
            # Add code metrics
            review_data['code_lines'] = len(code.split('\n'))
            
            # Ensure all required fields exist
            review_data.setdefault('summary', 'Code review completed')
            review_data.setdefault('score', 5.0)
            review_data.setdefault('complexity', 5)
            review_data.setdefault('maintainability', 5.0)
            review_data.setdefault('security_score', 5.0)
            review_data.setdefault('performance_score', 5.0)
            review_data.setdefault('issues', [])
            review_data.setdefault('suggestions', [])
            
            return review_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse review response: {str(e)}")
            return {
                'summary': 'Review completed',
                'score': 5.0,
                'complexity': 5,
                'maintainability': 5.0,
                'security_score': 5.0,
                'performance_score': 5.0,
                'issues': [],
                'suggestions': [],
                'code_lines': len(code.split('\n'))
            }
    
    async def detect_security_issues(self, code: str, language: str) -> list:
        """Focused security analysis"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Analyze this {language} code ONLY for security vulnerabilities.
Return a JSON array with security issues:
[{{"severity": "critical|error|warning", "issue": "description", "line": <number>, "fix": "recommendation"}}]

CODE:
```{language}
{code}
```"""
                    }
                ]
            )
            
            response_text = message.content[0].text
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
            return []
            
        except Exception as e:
            logger.error(f"Security analysis failed: {str(e)}")
            return []
    
    async def suggest_refactoring(self, code: str, language: str) -> list:
        """Suggest refactoring improvements"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Suggest refactoring improvements for this {language} code.
Return a JSON array:
[{{"improvement": "description", "reason": "why", "difficulty": "easy|medium|hard"}}]

CODE:
```{language}
{code}
```"""
                    }
                ]
            )
            
            response_text = message.content[0].text
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
            return []
            
        except Exception as e:
            logger.error(f"Refactoring suggestions failed: {str(e)}")
            return []

# Singleton instance
llm_service = LLMService()
