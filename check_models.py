import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCc35Hm_Ed9l5Q6NLr0G-xm6TgAqBbMppk")

def list_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f"Name: {m['name']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    list_models()
