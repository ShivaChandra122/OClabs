from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- Configuration Models ---

class DBSettings(BaseModel):
    """
    Database connection settings.
    """
    mysql_user: str = Field(..., env="MYSQL_USER")
    mysql_password: str = Field(..., env="MYSQL_PASSWORD")
    mysql_host: str = Field(..., env="MYSQL_HOST")
    mysql_port: int = Field(3306, env="MYSQL_PORT")
    mysql_database: str = Field(..., env="MYSQL_DATABASE")

# --- Core Feature Models ---

class VibeReportOutput(BaseModel):
    """
    Output structure for the Vibe Report AI.
    """
    shopping_persona: str = Field(..., description="Identified shopping persona (e.g., 'Family Man', 'Green Flag')")
    key_behavioral_metrics: Dict[str, Any] = Field(..., description="Key behavioral metrics summary")
    key_purchase_metrics: Dict[str, Any] = Field(..., description="Key purchase metrics summary")
    color_palette_hints: List[str] = Field(..., description="Suggested color palette hints")

class BrandVoiceInput(BaseModel):
    """
    Input structure for the Brand Voice Cloner AI.
    """
    campaign_texts: List[str] = Field(..., description="List of past campaign texts to analyze")

class BrandVoiceOutput(BaseModel):
    """
    Output structure for the Brand Voice Cloner AI.
    """
    tone: str = Field(..., description="Extracted tone of voice")
    emoji_density: float = Field(..., description="Calculated emoji density")
    cta_style: str = Field(..., description="Extracted Call-to-Action style")
    body_style: str = Field(..., description="Extracted body paragraph style")
    predicted_score: int = Field(..., ge=0, le=100, description="Predicted success score (0-100)")
    new_campaign_body: str = Field(..., description="Generated new campaign body text")

class SmartReceiptInput(BaseModel):
    """
    Input structure for the Smart Receipts AI.
    """
    current_basket_items: List[str] = Field(..., description="List of items currently in the customer's basket")
    past_purchase_patterns: Dict[str, Any] = Field(..., description="Summary of customer's past purchase patterns")

class SmartReceiptOutput(BaseModel):
    """
    Output structure for the Smart Receipts AI.
    """
    next_best_item: str = Field(..., description="Recommended next best item for purchase")
    loyalty_incentive_text: str = Field(..., description="Personalized loyalty incentive text")
    coupons: List[str] = Field(..., description="List of relevant coupons")

# --- API Request/Response Models ---
# These will be more specific when defining FastAPI endpoints,
# but can refer to the core feature models.

# Example for Vibe Report API
class GetVibeReportResponse(BaseModel):
    user_id: str
    report: VibeReportOutput

# Example for Brand Voice API
class CloneBrandVoiceRequest(BrandVoiceInput):
    brand_id: str = Field(..., description="Identifier for the brand whose voice is to be cloned")

class CloneBrandVoiceResponse(BaseModel):
    brand_id: str
    cloned_voice: BrandVoiceOutput

# Example for Smart Receipt API
class GetSmartReceiptRequest(SmartReceiptInput):
    customer_id: str = Field(..., description="Identifier for the customer")

class GetSmartReceiptResponse(BaseModel):
    customer_id: str
    receipt_suggestions: SmartReceiptOutput