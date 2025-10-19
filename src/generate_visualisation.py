"""
generate_visualisation.py
Combines avatar and clothing descriptions, generates a styled image using image-1 API.
"""

import os
import sys
import base64
import datetime
import argparse
from openai import OpenAI
from dotenv import load_dotenv

def load_texts(paths):
    texts = []
    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            texts.append(f.read().strip())
    return texts

def generate_image(prompt, api_key):
    """Generates an image using OpenAI's DALL-E-3 model."""
    print("Generating image with DALL-E-3...")
    client = OpenAI(api_key=api_key)
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        print("API response:", response)
        if not response or not hasattr(response, "data") or not response.data:
            print("No data in API response. Full response:", response)
            sys.exit(1)
        if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
            image_base64 = response.data[0].b64_json
            return base64.b64decode(image_base64)
        else:
            # If no b64_json, the image might be available via URL
            print("No base64 image data found. Check if an image URL was returned instead.")
            if hasattr(response.data[0], 'url') and response.data[0].url:
                print(f"Image URL: {response.data[0].url}")
                # You would need to download the image from the URL
                # This is a placeholder for that functionality
                print("Please download the image from the URL manually.")
            sys.exit(1)
    except Exception as e:
        print(f"Error generating image: {e}")
        # Return None instead of exiting to allow graceful fallback
        return None

def sanitize_prompt(prompt):
    """Sanitize the prompt to avoid content moderation issues."""
    # Add a clear context that this is for digital fashion visualization
    safe_prefix = "This is a digital fashion visualization project. Create a professional, G-rated image of "
    
    # Remove potentially problematic words or phrases
    problematic_terms = ["nude", "naked", "explicit", "sexual", "revealing", "inappropriate"]
    sanitized_prompt = prompt
    for term in problematic_terms:
        sanitized_prompt = sanitized_prompt.replace(term, "appropriate")
    
    return safe_prefix + sanitized_prompt

def main(avatar_path, clothes_paths, output_dir="output"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: Please set the OPENAI_API_KEY environment variable.")
        print("Make sure your .env file contains: OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
        
    if not os.path.isfile(avatar_path):
        print(f"Error: Avatar file not found: {avatar_path}")
        sys.exit(1)
        
    for c in clothes_paths:
        if not os.path.isfile(c):
            print(f"Error: Clothing file not found: {c}")
            sys.exit(1)
            
    try:
        # Load and display the content of the files for debugging
        texts = load_texts([avatar_path] + clothes_paths)
        print("\nLoaded the following descriptions:")
        print(f"Avatar: {texts[0][:100]}...")
        for i, clothing in enumerate(texts[1:]):
            print(f"Clothing {i+1}: {clothing[:100]}...")
        
        # Combine all descriptions into a single prompt
        raw_prompt = "\n".join(texts)
        
        # Sanitize the prompt to avoid content moderation issues
        prompt = sanitize_prompt(raw_prompt)
        print("\nSending request to OpenAI API...")
        
        # Generate the image
        image_bytes = generate_image(prompt, api_key=api_key)
        
        # Save the image with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(output_dir, f"styled_avatar_{timestamp}.png")
        
        with open(out_path, "wb") as f:
            f.write(image_bytes)
        print(f"\nSuccess! Styled image saved to: {out_path}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check that your OpenAI API key is valid and has sufficient credits")
        print("2. Ensure your avatar and clothing descriptions don't violate content policies")
        print("3. Try using a different model like 'dall-e-2' or 'dall-e-3' by changing the model in the code")
        print("4. Check the OpenAI API status at https://status.openai.com")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a styled avatar image from text descriptions.')
    parser.add_argument('avatar', help='Path to the avatar description text file')
    parser.add_argument('clothes', nargs='+', help='Paths to clothing description text files')
    parser.add_argument('--output-dir', '-o', default='output', help='Directory to save the generated image (default: output)')
    
    args = parser.parse_args()
    
    load_dotenv()
    main(args.avatar, args.clothes, args.output_dir)