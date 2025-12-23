import streamlit as st
import requests
import json
import base64
from io import BytesIO
import os

from schemas.models import (
    GetVibeReportResponse, VibeReportOutput,
    CloneBrandVoiceRequest, CloneBrandVoiceResponse,
    GetSmartReceiptRequest, SmartReceiptOutput
)

# --- Configuration ---
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000") # Assuming FastAPI runs locally

st.set_page_config(
    page_title="Optic Pulse",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Dark Mode feel and consumer product aesthetic ---
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3em;
        font-weight: bold;
        color: #FF69B4; /* Hot Pink */
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .subheader {
        font-size: 1.8em;
        font-weight: bold;
        color: #87CEEB; /* Sky Blue */
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2em;
    }
    .report-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #FF69B4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 1.1em;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #FF1493; /* Deeper Pink */
        transform: translateY(-2px);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Optic Pulse Navigation")
page = st.sidebar.radio(
    "Choose a feature:",
    ("Vibe Report", "Brand Voice Cloner", "Smart Receipts")
)

st.markdown('<p class="main-header">✨ Optic Pulse ✨</p>', unsafe_allow_html=True)

# --- Feature: Vibe Report ---
if page == "Vibe Report":
    st.markdown('<p class="subheader">🌟 Discover Your Shopping Vibe 🌟</p>', unsafe_allow_html=True)
    st.write("Unlock personalized insights into your shopping habits and receive your unique Vibe Card!")

    user_id = st.text_input("Enter Customer ID for Vibe Report:", "customer_123")

    if st.button("Generate My Vibe Report"):
        if user_id:
            with st.spinner("Generating your personalized Vibe Report..."):
                try:
                    response = requests.post(f"{FASTAPI_BASE_URL}/vibe-report?user_id={user_id}")
                    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    report_data = GetVibeReportResponse.model_validate(response.json())
                    
                    st.success("Vibe Report Generated Successfully!")
                    st.balloons()

                    st.markdown(f"### Your Shopping Persona: {report_data.report.shopping_persona} 🛍️")
                    st.write(f"Dive deep into what makes your shopping unique. You are a **{report_data.report.shopping_persona}**!")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Key Behavioral Metrics:")
                        st.json(report_data.report.key_behavioral_metrics)
                    with col2:
                        st.markdown("#### Key Purchase Metrics:")
                        st.json(report_data.report.key_purchase_metrics)
                    
                    st.markdown("#### Color Palette Hints:")
                    st.write(", ".join(report_data.report.color_palette_hints))

                    if "vibe_card_image" in report_data.report.key_behavioral_metrics:
                        image_path = report_data.report.key_behavioral_metrics["vibe_card_image"]
                        if os.path.exists(image_path):
                            st.markdown("#### Your Exclusive Vibe Card:")
                            # Read the image and encode to base64 for display
                            with open(image_path, "rb") as f:
                                image_bytes = f.read()
                                encoded_image = base64.b64encode(image_bytes).decode("utf-8")
                                st.image(f"data:image/png;base64,{encoded_image}", use_column_width=True)
                            st.download_button(
                                label="Download Vibe Card",
                                data=image_bytes,
                                file_name=os.path.basename(image_path),
                                mime="image/png"
                            )
                        else:
                            st.warning(f"Vibe Card image not found at {image_path}. Ensure FastAPI server is running and path is correct.")

                except requests.exceptions.ConnectionError:
                    st.error(f"Could not connect to FastAPI server at {FASTAPI_BASE_URL}. Please ensure it is running.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"Error from FastAPI: {e.response.status_code} - {e.response.text}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please enter a Customer ID.")

# --- Feature: Brand Voice Cloner ---
elif page == "Brand Voice Cloner":
    st.markdown('<p class="subheader">✍️ Clone Your Brand\'s Voice ✍️</p>', unsafe_allow_html=True)
    st.write("Analyze past campaigns to understand your brand's unique voice and generate new content that matches!")

    brand_id = st.text_input("Enter Brand ID:", "optic_culture")
    campaign_texts_input = st.text_area(
        "Enter 10 past campaign texts (one per line):",
        "Hey there, fashionista! ✨ Our new collection just dropped. Shop now and sparkle! #NewArrivals #Fashion\n"
        "Don't miss out! Get 20% off all dresses this weekend. Tap to shop! 🛍️ Limited stock!\n"
        "Feeling chic? Our latest blog post has tips on styling your spring wardrobe. Link in bio! 🌸\n"
        "Exclusive offer: Use code SAVEBIG at checkout for 15% off your entire order!\n"
        "New arrivals just landed! Refresh your look with our stunning pieces.\n"
        "Your style, elevated. Discover our premium collection now.\n"
        "Flash sale alert! Up to 50% off select items for a limited time.\n"
        "Trendsetter? We've got your next favorite outfit. Shop the collection.\n"
        "Behind the scenes: Get a peek at how we create magic. Link in story!\n"
        "Join our loyalty program and earn points with every purchase. Sign up today!"
    )
    campaign_texts = [text.strip() for text in campaign_texts_input.split('\n') if text.strip()]

    if st.button("Analyze & Generate Brand Voice"):
        if brand_id and len(campaign_texts) >= 5: # Require at least 5 for a decent sample
            with st.spinner("Cloning brand voice and generating new campaign..."):
                try:
                    request_payload = CloneBrandVoiceRequest(brand_id=brand_id, campaign_texts=campaign_texts).model_dump_json()
                    response = requests.post(
                        f"{FASTAPI_BASE_URL}/brand-voice",
                        headers={"Content-Type": "application/json"},
                        data=request_payload
                    )
                    response.raise_for_status()
                    voice_data = CloneBrandVoiceResponse.model_validate(response.json())
                    
                    st.success("Brand Voice Cloned and Campaign Generated!")

                    st.markdown(f"### Brand Voice Analysis for {voice_data.brand_id}:")
                    st.markdown(f"**Tone:** {voice_data.cloned_voice.tone}")
                    st.markdown(f"**Emoji Density:** {voice_data.cloned_voice.emoji_density:.2f}")
                    st.markdown(f"**CTA Style:** {voice_data.cloned_voice.cta_style}")
                    st.markdown(f"**Body Style:** {voice_data.cloned_voice.body_style}")
                    st.markdown(f"**Predicted Success Score:** {voice_data.cloned_voice.predicted_score}/100")

                    st.markdown("#### Generated New Campaign Body:")
                    st.info(voice_data.cloned_voice.new_campaign_body)

                except requests.exceptions.ConnectionError:
                    st.error(f"Could not connect to FastAPI server at {FASTAPI_BASE_URL}. Please ensure it is running.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"Error from FastAPI: {e.response.status_code} - {e.response.text}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please enter a Brand ID and at least 5 campaign texts.")

# --- Feature: Smart Receipts ---
elif page == "Smart Receipts":
    st.markdown('<p class="subheader">💡 Hyper-Personalized Smart Receipts 💡</p>', unsafe_allow_html=True)
    st.write("Get intelligent recommendations and loyalty incentives tailored just for you at checkout!")

    customer_id = st.text_input("Enter Customer ID for Smart Receipt:", "customer_123")
    current_basket_items_input = st.text_area(
        "Current Basket Items (one per line):",
        "Organic Coffee Beans\nAlmond Milk\nArtisan Bread"
    )
    current_basket_items = [item.strip() for item in current_basket_items_input.split('\n') if item.strip()]

    past_purchase_patterns_json = st.text_area(
        "Past Purchase Patterns (JSON format):",
        json.dumps({"last_purchase_category": "Beverages", "favorite_brand": "EcoBrew", "total_visits": 15}, indent=2)
    )
    try:
        past_purchase_patterns = json.loads(past_purchase_patterns_json)
    except json.JSONDecodeError:
        past_purchase_patterns = {}
        st.error("Invalid JSON for past purchase patterns. Please correct it.")


    if st.button("Generate Smart Receipt"):
        if customer_id and current_basket_items:
            with st.spinner("Generating smart receipt recommendations..."):
                try:
                    request_payload = GetSmartReceiptRequest(
                        customer_id=customer_id,
                        current_basket_items=current_basket_items,
                        past_purchase_patterns=past_purchase_patterns
                    ).model_dump_json()
                    
                    response = requests.post(
                        f"{FASTAPI_BASE_URL}/smart-receipt",
                        headers={"Content-Type": "application/json"},
                        data=request_payload
                    )
                    response.raise_for_status()
                    receipt_data = GetSmartReceiptResponse.model_validate(response.json())
                    
                    st.success("Smart Receipt Recommendations Generated!")

                    st.markdown(f"### Personalized Suggestions for {receipt_data.customer_id}:")
                    st.markdown(f"**Next Best Item:** {receipt_data.receipt_suggestions.next_best_item} ✨")
                    st.markdown(f"**Loyalty Incentive:** {receipt_data.receipt_suggestions.loyalty_incentive_text} 🎁")
                    
                    st.markdown("#### Exclusive Coupons:")
                    if receipt_data.receipt_suggestions.coupons:
                        for coupon in receipt_data.receipt_suggestions.coupons:
                            st.success(f"- {coupon}")
                    else:
                        st.info("No specific coupons available at this time.")

                except requests.exceptions.ConnectionError:
                    st.error(f"Could not connect to FastAPI server at {FASTAPI_BASE_URL}. Please ensure it is running.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"Error from FastAPI: {e.response.status_code} - {e.response.text}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please enter Customer ID and current basket items.")

# --- How to run ---
st.sidebar.markdown("---")
st.sidebar.markdown("### How to Run")
st.sidebar.markdown(
    """
    1. **Start FastAPI Backend:**
       Navigate to the `opt-pulse` directory in your terminal and run:
       `uvicorn main:app --reload`
    2. **Start Streamlit Frontend:**
       Open another terminal in the `opt-pulse` directory and run:
       `streamlit run streamlit_app.py`
    """
)
