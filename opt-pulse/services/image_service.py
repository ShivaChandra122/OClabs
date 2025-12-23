from PIL import Image, ImageDraw, ImageFont
import os
from typing import Dict, Any

class ImageService:
    """
    Manages image generation for Vibe Cards.
    """

    def __init__(self):
        self.assets_dir = "opt-pulse/assets"
        self.static_dir = "opt-pulse/static"
        os.makedirs(self.static_dir, exist_ok=True) # Ensure static directory exists
        
        # Create a dummy template image if it doesn't exist for development purposes
        self.template_path = os.path.join(self.assets_dir, "vibe_card_template.png")
        if not os.path.exists(self.template_path):
            self._create_dummy_template()

    def _create_dummy_template(self):
        """Creates a simple dummy template image for Vibe Cards."""
        try:
            img = Image.new('RGB', (800, 400), color = (73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((50,180), "Vibe Card Template", fill=(255,255,255))
            os.makedirs(self.assets_dir, exist_ok=True)
            img.save(self.template_path)
            print(f"Created dummy vibe card template at: {self.template_path}")
        except Exception as e:
            print(f"Could not create dummy template image: {e}")

    def generate_vibe_card(
        self,
        username: str,
        vibe_label: str,
        stats: Dict[str, Any]
    ) -> str:
        """
        Generates a shareable Vibe Card image based on user data.

        Args:
            username: The name of the user.
            vibe_label: The main Vibe Report label (e.g., "Green Flag").
            stats: A dictionary of key statistics to display.

        Returns:
            The file path to the generated image.
        """
        try:
            # Load the base template image
            img = Image.open(self.template_path)
            draw = ImageDraw.Draw(img)

            # Define fonts (using a default font, ideally should load custom fonts)
            try:
                title_font = ImageFont.truetype("arial.ttf", 40)
                text_font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()

            # Overlay text
            # Title: Vibe Report for [Username]
            title_text = f"Vibe Report for {username}"
            draw.text((50, 50), title_text, font=title_font, fill=(255, 255, 255))

            # Vibe Label
            vibe_text = f"Your Vibe: {vibe_label}"
            draw.text((50, 120), vibe_text, font=text_font, fill=(255, 255, 0)) # Yellow for emphasis

            # Stats
            y_offset = 180
            for key, value in stats.items():
                stat_text = f"{key.replace('_', ' ').title()}: {value}"
                draw.text((50, y_offset), stat_text, font=text_font, fill=(255, 255, 255))
                y_offset += 30

            # Save the generated image
            output_filename = f"vibe_card_{username.replace(' ', '_').lower()}.png"
            output_path = os.path.join(self.static_dir, output_filename)
            img.save(output_path)

            return output_path
        except Exception as e:
            print(f"Error generating vibe card for {username}: {e}")
            raise

# Example usage (for testing purposes)
if __name__ == "__main__":
    image_service = ImageService()
    try:
        username = "JaneDoe"
        vibe = "Green Flag"
        user_stats = {
            "total_spend": "$1250",
            "favorite_category": "Sustainable Apparel",
            "loyalty_score": "A+"
        }
        card_path = image_service.generate_vibe_card(username, vibe, user_stats)
        print(f"Generated Vibe Card at: {card_path}")
    except Exception as e:
        print(f"Image service test failed: {e}")
