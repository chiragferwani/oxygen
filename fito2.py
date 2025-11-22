import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import os

# ---------------------------
# STREAMLIT PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="FitO2 – BMI & Fitness Guidance",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------
# GEMINI API INIT
# ---------------------------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyCc35Hm_Ed9l5Q6NLr0G-xm6TgAqBbMppk"))
model = genai.GenerativeModel("gemini-flash-latest")

# ---------------------------
# LOAD OXYGEN LOGO
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

logo = load_logo("https://oxygenai.vercel.app/assets/logo-text-white-B3XghXWf.png")

# ---------------------------
# CUSTOM CSS
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
</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------
col1, col2 = st.columns([1, 3])

with col1:
    if logo:
        st.image(logo, width=120)

with col2:
    st.markdown("<div class='title'>FitO2</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>BMI Tracking & Fitness Guidance</div>", unsafe_allow_html=True)

st.write("Enter your height and weight to check your BMI and get a personalized fitness plan.")

# ---------------------------
# USER INPUTS
# ---------------------------
height = st.number_input("Height (in centimeters)", min_value=50, max_value=250, step=1)
weight = st.number_input("Weight (in kilograms)", min_value=10, max_value=300, step=1)

# ---------------------------
# BMI CALCULATION
# ---------------------------
def calculate_bmi(h, w):
    h_m = h / 100
    return round(w / (h_m * h_m), 2)

# ---------------------------
# BUTTON HANDLER
# ---------------------------
if st.button("Analyze Fitness", use_container_width=True):

    if height == 0 or weight == 0:
        st.warning("Please enter valid height and weight values.")
    else:
        bmi = calculate_bmi(height, weight)

        st.markdown(f"### 🧮 Your BMI: **{bmi}**")

        # AI request
        with st.spinner("Generating AI-powered fitness guidance..."):

            prompt = f"""
You are FitO2, an AI fitness model.

User Details:
- Height: {height} cm
- Weight: {weight} kg
- BMI: {bmi}

Tasks:
1. Classify BMI category (Underweight, Normal, Overweight, Obese).
2. Explain what this BMI means for health.
3. Provide a structured fitness plan (workout, steps, activity levels).
4. Provide a structured diet plan for improvement.
5. Keep the tone helpful and easy to understand.
"""

            response = model.generate_content(prompt)

        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
        st.markdown("### 💡 FitO2 Recommendations")
        st.write(response.text)
        st.markdown("</div>", unsafe_allow_html=True)
