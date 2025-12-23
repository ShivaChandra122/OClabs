import logging
from typing import List, Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from core.config import get_settings
from schemas.models import VibeReportOutput, BrandVoiceOutput, SmartReceiptOutput

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIService:
    """
    Manages AI interactions, including prompt generation and model calls.
    """
    def __init__(self):
        settings = get_settings()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.2, openai_api_key=settings.openai_api_key)

        # 1. Vibe Profiler Prompt
        self.vibe_profiler_prompt = PromptTemplate.from_template(
            """
            Analyze the following 12-month transaction summary for a customer to generate a Vibe Report.
            Identify their shopping persona, key behavioral metrics, key purchase metrics, and suggest a color palette.

            Transaction Summary:
            {transaction_summary}

            Output must be a JSON object with the following keys:
            - shopping_persona (string, e.g., "Family Man", "Green Flag", "Tech Enthusiast")
            - key_behavioral_metrics (dictionary, e.g., {{"avg_items_per_purchase": 3, "return_rate": 0.05}})
            - key_purchase_metrics (dictionary, e.g., {{"total_spend": 1200.50, "most_bought_category": "Apparel"}})
            - color_palette_hints (list of strings, e.g., ["#FFD700", "#FF6347", "#6A5ACD"])
            """
        )

        # 2. Brand Voice Cloner Prompt
        self.brand_voice_cloner_prompt = PromptTemplate.from_template(
            """
            Analyze the following 10 past campaign texts to extract the brand's tone, emoji density, CTA style, and body style.
            Then, generate a new campaign body text based on these characteristics and predict its success score (0-100).

            Past Campaign Texts:
            {campaign_texts}

            Output must be a JSON object with the following keys:
            - tone (string, e.g., "playful", "authoritative", "friendly")
            - emoji_density (float, percentage of emojis per word)
            - cta_style (string, e.g., "urgent", "informative", "subtle")
            - body_style (string, e.g., "short paragraphs", "bullet points", "storytelling")
            - predicted_score (integer, 0-100, based on 'sent', 'read', 'unsent' patterns)
            - new_campaign_body (string, the generated text)
            """
        )

        # 3. Smart Receipt Recommender Prompt
        self.smart_receipt_recommender_prompt = PromptTemplate.from_template(
            """
            Based on the customer's current basket items and past purchase patterns,
            recommend the next best item, provide a loyalty incentive text, and suggest relevant coupons.

            Current Basket Items:
            {current_basket_items}

            Past Purchase Patterns:
            {past_purchase_patterns}

            Output must be a JSON object with the following keys:
            - next_best_item (string, name of the recommended product)
            - loyalty_incentive_text (string, e.g., "Earn double points on your next purchase!")
            - coupons (list of strings, e.g., ["10% off next coffee", "Free delivery on orders over $50"])
            """
        )

    def _call_ai_model(self, prompt: PromptTemplate, input_data: Dict[str, Any], output_model: Any) -> Any:
        """
        Helper to call the AI model, handle logging, try/except, and Pydantic validation.
        """
        try:
            formatted_prompt = prompt.format(**input_data)
            logging.info(f"Sending prompt to AI: {formatted_prompt[:200]}...") # Log first 200 chars
            
            # Assuming the LLM directly returns a JSON string that can be parsed
            # For more robust parsing, consider LangChain's structured output parsers.
            response_content = self.llm.invoke(formatted_prompt).content
            logging.info(f"Received raw AI response: {response_content[:200]}...")

            # Attempt to parse JSON and validate with Pydantic model
            import json
            response_json = json.loads(response_content)
            validated_output = output_model(**response_json)
            
            logging.info("AI call successful and response validated.")
            return validated_output
        except ValidationError as e:
            logging.error(f"Pydantic validation error for AI response: {e}\nRaw response: {response_content}")
            raise
        except Exception as e:
            logging.error(f"Error during AI model call: {e}", exc_info=True)
            raise

    def get_vibe_report(self, transaction_summary: str) -> VibeReportOutput:
        """
        Generates a Vibe Report based on the transaction summary.
        """
        return self._call_ai_model(
            self.vibe_profiler_prompt,
            {"transaction_summary": transaction_summary},
            VibeReportOutput
        )

    def clone_brand_voice(self, campaign_texts: List[str]) -> BrandVoiceOutput:
        """
        Clones a brand's voice from past campaign texts and generates a new campaign.
        """
        return self._call_ai_model(
            self.brand_voice_cloner_prompt,
            {"campaign_texts": "\n".join(campaign_texts)}, # Join for prompt
            BrandVoiceOutput
        )

    def get_smart_receipt_recommendations(
        self, current_basket_items: List[str], past_purchase_patterns: Dict[str, Any]
    ) -> SmartReceiptOutput:
        """
        Generates smart receipt recommendations.
        """
        return self._call_ai_model(
            self.smart_receipt_recommender_prompt,
            {
                "current_basket_items": ", ".join(current_basket_items),
                "past_purchase_patterns": str(past_purchase_patterns) # Convert dict to string for prompt
            },
            SmartReceiptOutput
        )

# Example usage (for testing purposes, not part of the class logic)
if __name__ == "__main__":
    # NOTE: To run this example, you need to set OPENAI_API_KEY in your .env file
    # and potentially mock the LLM if you don't want to make actual API calls.

    # Example .env content:
    # OPENAI_API_KEY="your_openai_api_key_here"

    ai_service = AIService()

    # Test Vibe Report
    print("\n--- Testing Vibe Report ---")
    try:
        summary = "Customer purchased 5 t-shirts in various green shades, 2 eco-friendly water bottles, and a recycled material backpack over 12 months. Total spend: $350. Frequently browsed outdoor gear."
        vibe_report = ai_service.get_vibe_report(summary)
        print("Vibe Report Result:")
        print(vibe_report.model_dump_json(indent=2))
    except Exception as e:
        print(f"Vibe Report Test Failed: {e}")

    # Test Brand Voice Cloner
    print("\n--- Testing Brand Voice Cloner ---")
    try:
        campaigns = [
            "Hey there, fashionista! ✨ Our new collection just dropped. Shop now and sparkle! #NewArrivals #Fashion",
            "Don't miss out! Get 20% off all dresses this weekend. Tap to shop! 🛍️ Limited stock!",
            "Feeling chic? Our latest blog post has tips on styling your spring wardrobe. Link in bio! 🌸",
            "Another campaign text.",
            "Yet another campaign text.",
            "Test campaign 1.",
            "Test campaign 2.",
            "Test campaign 3.",
            "Test campaign 4.",
            "Test campaign 5."
        ]
        brand_voice = ai_service.clone_brand_voice(campaigns)
        print("Brand Voice Cloner Result:")
        print(brand_voice.model_dump_json(indent=2))
    except Exception as e:
        print(f"Brand Voice Cloner Test Failed: {e}")

    # Test Smart Receipt Recommender
    print("\n--- Testing Smart Receipt Recommender ---")
    try:
        basket = ["Organic Coffee Beans", "Almond Milk"]
        patterns = {"last_purchase_category": "Beverages", "favorite_brand": "EcoBrew"}
        smart_receipt = ai_service.get_smart_receipt_recommendations(basket, patterns)
        print("Smart Receipt Recommender Result:")
        print(smart_receipt.model_dump_json(indent=2))
    except Exception as e:
        print(f"Smart Receipt Recommender Test Failed: {e}")
