"""
generate_item.py
Analyzes a clothing image using GPT-4o and outputs a detailed description as a .txt file.
"""

import sys
import os
import base64
import hashlib
import json
from openai import OpenAI
from dotenv import load_dotenv

# Cache directory for analysis results
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Utility: encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_image_hash(image_path):
    """Generate a hash for the image file to use as cache key"""
    with open(image_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def get_cached_analysis(image_path):
    """Check if analysis is already cached"""
    image_hash = get_image_hash(image_path)
    cache_file = os.path.join(CACHE_DIR, f"{image_hash}.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def cache_analysis(image_path, analysis_result):
    """Cache the analysis result"""
    image_hash = get_image_hash(image_path)
    cache_file = os.path.join(CACHE_DIR, f"{image_hash}.json")
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: Could not cache analysis: {e}")

def analyze_image(image_path, api_key=None):
    # Check cache first
    cached_result = get_cached_analysis(image_path)
    if cached_result:
        print(f"Using cached analysis for {os.path.basename(image_path)}")
        return cached_result
    
    print(f"Analyzing image {os.path.basename(image_path)} with GPT-4o...")
    base64_image = encode_image(image_path)
    client = OpenAI(api_key=api_key)
    prompt = (
        "Describe the clothing item in detail, including its type (e.g., dress, shirt, pants, bag, shoes, etc.), color, style, texture, fabric, and fit. "
        "Start the description with: 'This item is a ...'. Focus only on the clothing, not the background or model."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ]
        )
        result = response.choices[0].message.content.strip()
        
        # Cache the result
        cache_analysis(image_path, result)
        return result
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return f"Analysis failed: {str(e)}"

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