"""
generate_visualisation.py
Combines avatar and clothing descriptions, generates a styled image using image-1 API.
"""

import os
import sys
import base64
from openai import OpenAI
from dotenv import load_dotenv

def load_texts(paths):
    texts = []
    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            texts.append(f.read().strip())
    return texts

def generate_image(prompt, api_key=None):
    client = OpenAI(api_key=api_key)
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt
    )
    image_base64 = response.data[0].b64_json
    return base64.b64decode(image_base64)

def main(avatar_path, clothes_paths):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)
    if not os.path.isfile(avatar_path):
        print(f"Error: Avatar file not found: {avatar_path}")
        sys.exit(1)
    for c in clothes_paths:
        if not os.path.isfile(c):
            print(f"Error: Clothing file not found: {c}")
            sys.exit(1)
    try:
        texts = load_texts([avatar_path] + clothes_paths)
        # Combine all descriptions into a single prompt
        prompt = "\n".join(texts)
        image_bytes = generate_image(prompt, api_key=api_key)
        out_path = "styled_avatar.png"
        with open(out_path, "wb") as f:
            f.write(image_bytes)
        print(f"Styled image saved to {out_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_visualisation.py <avatar.txt> <clothes1.txt> [<clothes2.txt> ...]")
        sys.exit(1)
    load_dotenv()
    main(sys.argv[1], sys.argv[2:]) 