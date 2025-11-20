import os
import json
from typing import Dict, Any, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class LLMClient:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_model = None
        
        # Initialize clients if keys exist
        if os.getenv("OPENAI_API_KEY") and OpenAI:
            self.openai_client = OpenAI()
            
        if os.getenv("ANTHROPIC_API_KEY") and Anthropic:
            self.anthropic_client = Anthropic()
            
        if os.getenv("GOOGLE_API_KEY") and genai:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')

    def analyze_show_tone(self, show_title: str, description: str = "") -> Dict[str, float]:
        # ... (Prompt definition) ...
        prompt = f"""
        Analyze the TV show '{show_title}' {f'({description})' if description else ''}.
        Rate it on these 5 dimensions from 0-100:
        1. Darkness (Light/Sitcom to Grim/Dark)
        2. Pace (Slow/Languid to Fast/Sorkin)
        3. Satire (Sincere to Cynical/Satirical)
        4. Heart (Cold to Warm/Ted Lasso)
        5. Absurdity (Grounded to Surreal)
        
        Return ONLY a JSON object with these keys: "Darkness", "Pace", "Satire", "Heart", "Absurdity".
        """
        
        if self.gemini_model:
            return self._call_gemini(prompt)
        elif self.anthropic_client:
            return self._call_claude(prompt)
        elif self.openai_client:
            return self._call_openai(prompt)
        else:
            return self._mock_response(show_title)

    def analyze_show_deep(self, show_title: str) -> Dict[str, Any]:
        # ... (Prompt definition) ...
        prompt = f"""
        Analyze the TV show '{show_title}'.
        Provide a JSON object with:
        1. "Plot": A 1-sentence logline.
        2. "Themes": A list of 3-5 key themes (e.g. "Existentialism", "Family Dynamics").
        3. "Impact": A score 0-100 of its cultural impact/legacy.
        
        Return ONLY JSON.
        """
        if self.gemini_model:
            return self._call_gemini(prompt)
        elif self.anthropic_client:
            return self._call_claude(prompt)
        elif self.openai_client:
            return self._call_openai(prompt)
        else:
            return {
                "Plot": f"A group of characters navigate life in {show_title}.",
                "Themes": ["Friendship", "Work", "Life"],
                "Impact": 75.0
            }

    def analyze_writer_deep(self, writer_name: str, credits: list) -> Dict[str, Any]:
        # ... (Prompt definition) ...
        credits_str = ", ".join(credits[:5])
        prompt = f"""
        Analyze comedy writer '{writer_name}', known for: {credits_str}.
        Provide a JSON object with:
        1. "Background": List of origins (e.g. "Stand-up", "Improv", "Sketch", "Playwright").
        2. "Awards": List of major awards (Emmy, WGA, etc.) or "None".
        3. "Strengths": List of 3 key writing strengths (e.g. "Dialogue", "Structure", "Heart").
        4. "Bio": A 1-sentence professional bio.
        
        Return ONLY JSON.
        """
        if self.gemini_model:
            return self._call_gemini(prompt)
        elif self.anthropic_client:
            return self._call_claude(prompt)
        elif self.openai_client:
            return self._call_openai(prompt)
        else:
            return {
                "Background": ["Writer's Room"],
                "Awards": [],
                "Strengths": ["Dialogue", "Jokes"],
                "Bio": f"{writer_name} is a comedy writer known for {credits_str}."
            }

    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        try:
            response = self.gemini_model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return self._mock_response("Error")

    def _call_claude(self, prompt: str) -> Dict[str, Any]:
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=100,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            content = message.content[0].text
            return self._parse_json(content)
        except Exception as e:
            print(f"Claude API Error: {e}")
            return self._mock_response("Error")

    def _call_openai(self, prompt: str) -> Dict[str, float]:
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return self._parse_json(content)
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return self._mock_response("Error")

    def _parse_json(self, content: str) -> Dict[str, float]:
        try:
            # Find JSON in text if needed
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
            return json.loads(content)
        except:
            return self._mock_response("Parse Error")

    def _mock_response(self, title: str) -> Dict[str, float]:
        """Fallback heuristic if no API key."""
        # Simple hash-based determinism for consistent mock values
        seed = sum(ord(c) for c in title)
        import random
        rng = random.Random(seed)
        
        return {
            "Darkness": rng.randint(20, 80),
            "Pace": rng.randint(30, 90),
            "Satire": rng.randint(20, 80),
            "Heart": rng.randint(20, 80),
            "Absurdity": rng.randint(10, 70)
        }
