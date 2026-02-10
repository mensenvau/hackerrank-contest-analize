import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from config import Config

class SubmissionReview(BaseModel):
    score: float = Field(description="Code quality score from 0 to 10")
    cheating_probability: int = Field(description="Cheating probability percentage from 0 to 100")
    summary: str = Field(description="Brief summary of code analysis")

class CodeAnalyzer:
    def __init__(self):
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name='gemini-3.0-flash',
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": SubmissionReview
                }
            )
        else:
            self.model = None

    def analyze(self, code, challenge_name):
        if not self.model: 
            return {"score": 0, "prob": 0, "notes": "AI Key missing"}
        
        if not code or len(code.strip()) < 10: 
            return {"score": 0, "prob": 0, "notes": "No valid code"}

        prompt = f"""
        Analyze code submission.
        Challenge: {challenge_name}
        Code:
        {code}
        """

        try:
            resp = self.model.generate_content(prompt)
            data = json.loads(resp.text)
            return {
                "score": data.get("score", 0),
                "prob": data.get("cheating_probability", 0),
                "notes": data.get("summary", "")
            }
        except Exception as e:
            return {"score": 0, "prob": 0, "notes": f"AI Error: {str(e)}"}
