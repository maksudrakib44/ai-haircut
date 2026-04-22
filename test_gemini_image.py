import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

# Load your test image
image = Image.open("hairless.jpg")
prompt = "Change hairstyle to pixie cut. Keep face and background."

try:
    response = model.generate_content(
        [prompt, image],
        generation_config=genai.types.GenerationConfig(response_modalities=['IMAGE'])
    )
    
    # Check response
    print("Response received.")
    print("Candidates:", len(response.candidates))
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            print("Image data found, saving...")
            with open("output.jpg", "wb") as f:
                f.write(part.inline_data.data)
            print("Saved output.jpg")
        else:
            print("Part has text:", part.text)
except Exception as e:
    print("Error:", e)