# app.py
"""
MedO2 Streamlit App (MedO2 = medicine assistant under Project Oxygen)

Features:
- Accepts free-form input: either symptoms OR medicine name
- Uses a generative model (Gemini preferred) to:
    - If symptoms: infer likely conditions and propose medicines + alternatives
    - If medicine name: provide medicine info + generic/alternative suggestions
- Displays results in a polished, minimal UI with light/dark mode toggle
- Uses a logo image included in the conversation

Before running:
1) pip install streamlit google-generative-ai openai pillow
   (You only need one provider; google lib for Gemini, or openai as fallback.)
2) Put the logo image at: /mnt/data/A_logo_is_centered_on_a_dark_gray_to_nearly_black_.png
   (This is the path provided earlier in the conversation.)
3) Set env var:
   - For Gemini (Google): export GOOGLE_API_KEY="YOUR_KEY"
   - For OpenAI fallback: export OPENAI_API_KEY="YOUR_KEY"
4) Run: streamlit run app.py
"""

import os
import json
from typing import Dict, Any
import streamlit as st
from PIL import Image
from functools import lru_cache
import requests
import io

# -------------------------
# CONFIG
# -------------------------
# Logo path (from conversation)
LOGO_PATH = "https://oxygenai.vercel.app/assets/logo-white-BnXjc4Zw.png"

# UI strings
PROJECT_NAME = "Project Oxygen"
DEVICE_NAME = "OxyOne"
APP_TITLE = "MedO2 — Medicine Information & Alternatives"
TAGLINE = "MedO2 helps with medicine info and alternative suggestions (Not medical advice)."

# Model configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCc35Hm_Ed9l5Q6NLr0G-xm6TgAqBbMppk")

# -------------------------
# GENERATIVE API ABSTRACTION
# -------------------------
def send_to_generative_model(system_prompt: str, user_prompt: str, max_tokens=512) -> str:
    """
    Try Google Generative AI (Gemini) via REST API.
    Returns the text output from the model.
    """
    if GOOGLE_API_KEY:
        try:
            import requests
            
            # Combine prompts
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{
                    "parts": [{"text": combined_prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.1
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                 return f"Error: {response.status_code} - {response.text}"

            result = response.json()
            
            # Extract text
            # Response structure: candidates[0].content.parts[0].text
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0]["text"]
            
            return "No response generated (possibly blocked by safety filters)."
            
        except Exception as e:
            st.error(f"Google Gemini call failed: {e}")
            return f"ERROR: {e}"

    # If no API keys configured
    st.error("No generative API configured. Set GOOGLE_API_KEY in environment.")
    return ""

# -------------------------
# PROMPTS
# -------------------------
SYSTEM_PROMPT = (
    "You are MedO2, a concise medical assistant. Provide a short, helpful suggestion based on the user's input. "
    "If symptoms are provided, suggest possible conditions and general medicine classes. "
    "If a medicine is named, provide a brief summary and alternatives. "
    "Keep the response short and easy to read. Do not use JSON."
)

# Example user prompt will be programmatically created below depending on input

# -------------------------
# PARSING
# -------------------------
@lru_cache(maxsize=256)
def query_med2_cached(user_input: str) -> str:
    # Build user prompt dynamically
    user_prompt = (
        f"User input: {user_input}\n"
        "Provide a concise medical suggestion."
    )
    return send_to_generative_model(SYSTEM_PROMPT, user_prompt, max_tokens=700)

# -------------------------
# STREAMLIT UI
# -------------------------
st.set_page_config(page_title="MedO2 — Project Oxygen", page_icon="🫁", layout="wide")

# Light/Dark mode toggle (simple)
mode = st.sidebar.selectbox("Mode", ["Dark", "Light"])
if mode == "Dark":
    st.markdown(
        """
        <style>
        .stApp { background-color: #0b0f13; color: #e6eef3; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .stApp { background-color: #f7fbfc; color: #0b1720; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Top hero layout
col1, col2 = st.columns([1, 2])

with col1:
    # show logo if exists
    try:
        if LOGO_PATH.startswith("http"):
            response = requests.get(LOGO_PATH)
            response.raise_for_status()
            logo_img = Image.open(io.BytesIO(response.content))
        else:
            logo_img = Image.open(LOGO_PATH)
        st.image(logo_img, width=160)
    except Exception as e:
        st.write(f"")  # nothing if missing

with col2:
    st.title(APP_TITLE)
    st.markdown(f"**{TAGLINE}**")
    st.caption("Type symptoms (e.g. 'fever, cough, breathlessness') or a medicine name (e.g. 'paracetamol').")

st.divider()

# Input box at bottom-ish style
user_input = st.text_input("Enter symptoms or medicine name", placeholder="e.g. fever, dry cough, tiredness OR paracetamol")

if st.button("Analyze"):
    if not user_input or user_input.strip() == "":
        st.warning("Please enter symptoms or a medicine name.")
    else:
        with st.spinner("Analyzing with MedO2..."):
            result = query_med2_cached(user_input.strip())

        # Display result
        st.subheader("Suggestion")
        st.write(result)

        st.info("Disclaimer: MedO2 provides informational suggestions only. This is not medical advice. Consult a qualified healthcare professional.")

# Section: quick examples


# Footer
st.divider()
st.markdown(f"© {PROJECT_NAME} — {DEVICE_NAME} • Built with MedO2.  ")

