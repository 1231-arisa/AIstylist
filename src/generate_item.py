"""
generate_item.py
Analyzes a clothing image using GPT-4o and outputs a detailed description as a .txt file.
"""

import sys
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

# Utility: encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_image(image_path, api_key=None):
    base64_image = encode_image(image_path)
    client = OpenAI(api_key=api_key)
    prompt = (
        "Describe the clothing item in detail, including color, style, texture, fabric, and fit. "
        "Focus only on the clothing, not the background or model."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]
    )
    return response.choices[0].message.content.strip()

def main(image_path):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)
    if not os.path.isfile(image_path):
        print(f"Error: File not found: {image_path}")
        sys.exit(1)
    try:
        description = analyze_image(image_path, api_key=api_key)
        # Save description to .txt file next to image
        base = os.path.splitext(os.path.basename(image_path))[0]
        out_path = os.path.join(os.path.dirname(image_path), f"{base}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(description)
        print(f"Description saved to {out_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_item.py <image_path>")
        sys.exit(1)
    load_dotenv()
    main(sys.argv[1]) 