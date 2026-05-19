import traceback
from google import genai


class DeepScraperAgent:

    def __init__(self, api_key, logger=None):

        self.api_key = api_key
        self.logger = logger

        try:

            self.log("[System] Initializing Gemini client...")

            # NEW SDK CLIENT
            self.client = genai.Client(
                api_key=self.api_key
            )

            self.log("[System] Gemini client connected successfully.")

        except Exception as e:

            self.log(f"[Error] API Key configuration failed: {str(e)}")

            traceback.print_exc()

            raise Exception(f"Gemini initialization failed: {e}")

    def log(self, message):

        print(message)

        if self.logger:
            try:
                self.logger(message)
            except:
                pass

    def ask_gemini(self, prompt):

        try:

            self.log("[Agent] Prompting Gemini to architect parsing scripts...")

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            if hasattr(response, "text"):
                return response.text

            return str(response)

        except Exception as e:

            self.log(f"[Error] Runtime execution crashed: {str(e)}")

            traceback.print_exc()

            return None

    def generate_scraping_strategy(self, city):

        prompt = f"""
You are an elite web scraping architect.

Generate a structured scraping strategy for:

City: {city}

Platforms:
1. Zomato
2. Swiggy

Need:
- Restaurant names
- Ratings
- Cuisine
- Delivery time
- Address
- Price for two

Also include:
- Pagination handling
- Anti-bot bypass recommendations
- HTML parsing logic
- JSON extraction ideas
"""

        return self.ask_gemini(prompt)

    def test_connection(self):

        try:

            self.log("[System] Testing Gemini API connection...")

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Reply only with: connection successful"
            )

            self.log("[System] Gemini API test passed.")

            return response.text

        except Exception as e:

            self.log(f"[Error] Gemini API connection failed: {str(e)}")

            traceback.print_exc()

            return None
