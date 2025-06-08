import cv2
import numpy as np
from PIL import Image
import os
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from transformers import pipeline, set_seed

# --- Configuration ---
CLOTHING_IMAGE_PATH = "segmented_clothing_output.png" # Path to your background-removed clothing image
OUTPUT_DIR = "output/"
OUTPUT_FILENAME = "anime_clothing_illustration.png"

# Stable Diffusion and ControlNet Models
# These will be downloaded the first time the script runs.
# Ensure you have enough disk space (several GBs).
CONTROLNET_MODEL_PATH = "lllyasviel/sd-controlnet-canny"
STABLE_DIFFUSION_MODEL_PATH = "runwayml/stable-diffusion-v1-5" # A general-purpose SD model

# Generation Prompts
PROMPT = "A flat cute anime-style illustration of a navy short-sleeve shirt, clean lines, 2D flat pastel color style, front view, no wrinkles, worn by a mannequin or invisible figure."
NEGATIVE_PROMPT = "realistic photo, face, background, shadows, body, photorealism, low quality"

# Image dimensions for Stable Diffusion (ControlNet often works best with square inputs)
IMAGE_DIM = 512 # Standard for many Stable Diffusion models

# --- Functions ---

def load_models():
    """
    Loads the ControlNet and Stable Diffusion models.
    """
    print("Loading ControlNet and Stable Diffusion models...")
    # Load ControlNet model with Canny preprocessor
    controlnet = ControlNetModel.from_pretrained(CONTROLNET_MODEL_PATH, torch_dtype=torch.float16)

    # Load Stable Diffusion pipeline with ControlNet
    # safety_checker=None is used to bypass the NSFW filter, useful for debugging
    # For production, consider keeping it or implementing your own content moderation
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        STABLE_DIFFUSION_MODEL_PATH,
        controlnet=controlnet,
        torch_dtype=torch.float16,
        safety_checker=None
    )

    # Move pipeline to GPU if available for faster generation
    if torch.cuda.is_available():
        pipe.to("cuda")
        print("Models loaded to GPU (CUDA).")
    else:
        print("CUDA not available. Models loaded to CPU (generation will be slower).")

    return pipe

def extract_canny_edges(image: Image.Image, low_threshold: int = 100, high_threshold: int = 200) -> Image.Image:
    """
    Extracts Canny edges from a PIL image.
    The image is first resized to IMAGE_DIM x IMAGE_DIM for consistent ControlNet input.
    """
    print("Extracting Canny edges...")
    # Resize image to square dimensions for ControlNet
    image = image.resize((IMAGE_DIM, IMAGE_DIM))

    # Convert PIL Image to OpenCV format (numpy array)
    # Ensure it's in BGR format for OpenCV and remove alpha channel if present
    img_np = np.array(image.convert("RGB")) # Convert to RGB to ensure no alpha before BGR conversion
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detector
    canny_output = cv2.Canny(img_gray, low_threshold, high_threshold)

    # Convert back to PIL Image
    canny_image = Image.fromarray(canny_output)
    print("Canny edge extraction complete.")
    return canny_image

def generate_illustration(canny_image: Image.Image, pipe, prompt: str, negative_prompt: str) -> Image.Image:
    """
    Generates a 2D anime illustration using Stable Diffusion with ControlNet.
    """
    print("Generating anime illustration...")
    set_seed(42) # For reproducibility

    # Generate image
    # num_inference_steps: higher values usually result in better quality but take longer
    # guidance_scale: controls how strongly the image adheres to the prompt (higher = stronger)
    generated_images = pipe(
        prompt=prompt,
        image=canny_image,
        negative_prompt=negative_prompt,
        num_inference_steps=30,
        guidance_scale=7.5
    ).images

    print("Illustration generation complete.")
    return generated_images[0]

# --- Main execution ---
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Step 1: Load background-removed clothing image ---
    clothing_path = CLOTHING_IMAGE_PATH
    if not os.path.exists(clothing_path):
        print(f"Error: Clothing image not found at {clothing_path}")
        print("Please ensure your background-removed clothing image is at the specified path.")
        exit(1)

    try:
        clothing_image = Image.open(clothing_path).convert("RGBA") # Ensure it has an alpha channel
        print(f"Loaded clothing image from: {clothing_path}")
    except Exception as e:
        print(f"Error loading clothing image: {e}")
        exit(1)

    # --- Step 2: Load ControlNet and Stable Diffusion models ---
    diffusion_pipeline = load_models()

    # --- Step 3: Extract clothing silhouette using Canny edge detector ---
    canny_image = extract_canny_edges(clothing_image)

    # Save the Canny edge image for verification (optional)
    # canny_image.save(os.path.join(OUTPUT_DIR, "canny_edges.png"))
    # print(f"Canny edges saved to {os.path.join(OUTPUT_DIR, "canny_edges.png")}")

    # --- Step 4: Run extracted edges through Stable Diffusion ---
    final_illustration = generate_illustration(canny_image, diffusion_pipeline, PROMPT, NEGATIVE_PROMPT)

    # --- Step 5: Save the resulting image ---
    output_full_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    final_illustration.save(output_full_path)
    print(f"Final anime clothing illustration saved to: {output_full_path}")

    print("\nProcess finished.")
    print("Note: The Stable Diffusion models will download a large amount of data on the first run.")
    print("If you encounter CUDA out of memory errors, try reducing IMAGE_DIM or running on CPU (by removing .to('cuda')).") 