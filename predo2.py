import streamlit as st
import google.generativeai as genai
from PIL import Image
from PIL import Image
import base64
import requests
import os
import io

# ---------------------------
# CONFIGURE PAGE
# ---------------------------
st.set_page_config(
    page_title="PredO2 – Disease Prediction",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------
# GEMINI API SETUP
# ---------------------------
genai.configure(api_key="AIzaSyCc35Hm_Ed9l5Q6NLr0G-xm6TgAqBbMppk")

model = genai.GenerativeModel("gemini-flash-latest")

# ---------------------------
# OXYGEN LOGO (OPTIONAL)
# ---------------------------
def load_logo(path):
    try:
        if path.startswith("http"):
            response = requests.get(path)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        else:
            return Image.open(path)
    except Exception as e:
        return None

logo = load_logo("https://oxygenai.vercel.app/assets/logo-text-white-B3XghXWf.png")   # ← Put your logo file in same folder


# ---------------------------
# UI CSS
# ---------------------------
st.markdown("""
<style>
    .title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: -5px;
    }
    .subtitle {
        font-size: 18px;
        color: #a9a9a9;
        margin-bottom: 25px;
    }
    .result-box {
        padding: 20px;
        border-radius: 12px;
        background-color: #1a1a1a;
        border: 1px solid #333;
        margin-top: 20px;
    }
    .stTextInput input {
        padding: 14px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER SECTION
# ---------------------------
col1, col2 = st.columns([1, 3])

with col1:
    if logo:
        st.image(logo, width=120)

with col2:
    st.markdown("<div class='title'>PredO2</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Disease Prediction & Risk Analysis</div>", unsafe_allow_html=True)

st.write("Provide symptoms or a short health description below:")

# ---------------------------
# USER INPUT
# ---------------------------
user_input = st.text_area(
    "Describe your symptoms:",
    placeholder="Example: fever, body pain, fatigue, sore throat...",
    height=120
)

# ---------------------------
# PREDICT BUTTON + GEMINI CALL
# ---------------------------
if st.button("Analyze Symptoms", use_container_width=True):

    if not user_input.strip():
        st.warning("Please enter some symptoms.")
    else:
        with st.spinner("Analyzing health data with PredO2..."):

            prompt = f"""
You are PredO2, an AI model specialized in disease prediction and risk analysis.

User provided symptoms or description:
{user_input}

Your tasks:
1. Predict the most likely diseases.
2. Provide explanations for each prediction.
3. Assess risk level: Low / Moderate / High.
4. Suggest when medical help is required.
5. Provide actionable steps for care.

Keep the answer structured, accurate, and easy to understand.
"""

            response = model.generate_content(prompt)

        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
        st.markdown("### 🧠 Predicted Conditions & Risk Analysis")
        st.write(response.text)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR - MODEL CHECK
# ---------------------------
with st.sidebar:
    st.header("Debug Info")
    if st.button("Check Available Models"):
        st.write("Fetching models...")
        api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyCc35Hm_Ed9l5Q6NLr0G-xm6TgAqBbMppk")
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                models = response.json().get('models', [])
                found_models = []
                for m in models:
                    if 'generateContent' in m.get('supportedGenerationMethods', []):
                        found_models.append(m['name'])
                
                if found_models:
                    st.success(f"Found {len(found_models)} models:")
                    for m in found_models:
                        st.code(m)
                else:
                    st.warning("No models found with generateContent support.")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to fetch models: {e}")

