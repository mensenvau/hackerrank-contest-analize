import json
import time
import google.generativeai as genai
from pydantic import BaseModel, Field
from config import Config
from typing import List

class ChallengeReview(BaseModel):
    challenge_name: str = Field(description="Name of the challenge")
    cheating_probability: int = Field(description="Cheating probability 0-100")
    summary: str = Field(description="Brief analysis note")

class UserReview(BaseModel):
    overall_cheating_probability: int = Field(description="Overall cheating probability for this user 0-100")
    overall_summary: str = Field(description="Overall summary of user behavior")
    challenges: List[ChallengeReview] = Field(description="Per-challenge analysis")

class CodeAnalyzer:
    def __init__(self):
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": UserReview
                }
            )
        else:
            self.model = None

    def analyze_user(self, username, challenge_codes):
        """
        Analyze ALL challenges for a user in a single API call.
        challenge_codes: dict { "Challenge Name": "source code" }
        Returns UserReview-like dict.
        """
        if not self.model:
            return {"overall_cheating_probability": 0, "overall_summary": "API key missing", "challenges": []}

        # Build combined prompt with all challenges
        code_sections = []
        for ch_name, code in challenge_codes.items():
            code_sections.append(f"=== Challenge: {ch_name} ===\n{code}\n")

        all_code = "\n".join(code_sections)

        prompt = f"""You are an expert anti-cheating analyst for a beginner-level programming contest.
Analyze ALL code submissions below for user "{username}".

DETECTION CRITERIA (red flags):
- Code solved too perfectly on first attempt for a beginner
- Advanced algorithms/patterns not expected from beginners
- Hardcoded outputs instead of real logic
- Generic variable names with complex logic = likely copied
- Competitive programming templates or AI-generated patterns
- Code style inconsistent across challenges (different person wrote each)

SCORING GUIDE for cheating_probability (per challenge AND overall):
- 0-20%: Original work, has beginner mistakes
- 20-50%: Some parts may be from online sources but adapted
- 50-80%: Likely copied or AI-generated
- 80-100%: Definitely copied/AI/hardcoded

Give an OVERALL probability considering all challenges together.
If all solutions are suspiciously perfect, overall should be high.

{all_code}"""

        try:
            resp = self.model.generate_content(prompt)
            data = json.loads(resp.text)
            return data
        except Exception as e:
            return {"overall_cheating_probability": 0, "overall_summary": f"AI Error: {str(e)}", "challenges": []}
