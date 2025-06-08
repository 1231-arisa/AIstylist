import cv2
import numpy as np
from PIL import Image
import os
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, EulerAncestralDiscreteScheduler
from transformers import set_seed

# --- Configuration ---
# Path to your background-removed clothing image (e.g., output from u2net_clothing_compositor.py)
CLOTHING_IMAGE_PATH = "segmented_clothing_output.png"

OUTPUT_DIR = "output/"
OUTPUT_FILENAME = "anime_clothing_illustration.png"

# Stable Diffusion and ControlNet Models
# These will be downloaded the first time the script runs.
# Ensure you have enough disk space (several GBs).
CONTROLNET_MODEL_PATH = "lllyasviel/sd-controlnet-canny"
STABLE_DIFFUSION_MODEL_PATH = "runwayml/stable-diffusion-v1-5" # A general-purpose SD model

# Generation Prompts
PROMPT = "A flat, cute anime-style illustration of a navy short-sleeve shirt, clean lines, 2D pastel color style, front view, no wrinkles, worn by an invisible mannequin."
NEGATIVE_PROMPT = "realistic photo, face, background, shadows, body, photorealism, low quality"

# Image dimensions for Stable Diffusion (ControlNet often works best with square inputs)
# This will be the output resolution as well.
IMAGE_DIM = 1024 

# Canny Edge Detector Thresholds (optimized for general use)
CANNY_LOW_THRESHOLD = 100
CANNY_HIGH_THRESHOLD = 200

# --- Functions ---

def load_diffusion_pipeline():
    """
    Loads the ControlNet and Stable Diffusion models, and sets the scheduler.
    """
    print("Loading ControlNet and Stable Diffusion models...")
    
    # Load ControlNet model
    controlnet = ControlNetModel.from_pretrained(CONTROLNET_MODEL_PATH, torch_dtype=torch.float16)

    # Load Stable Diffusion pipeline with ControlNet
    # safety_checker=None is used to bypass the NSFW filter, useful for debugging.
    # For production, consider keeping it or implementing your own content moderation.
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        STABLE_DIFFUSION_MODEL_PATH,
        controlnet=controlnet,
        torch_dtype=torch.float16,
        safety_checker=None
    )

    # Set Euler A scheduler for high-quality generation
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

    # Move pipeline to GPU if available for faster generation
    if torch.cuda.is_available():
        pipe.to("cuda")
        print("Models loaded to GPU (CUDA).")
    else:
        print("CUDA not available. Models loaded to CPU (generation will be significantly slower). A GPU is highly recommended.")

    return pipe

def extract_canny_edges(image: Image.Image) -> Image.Image:
    """
    Extracts Canny edges from a PIL image. The image is resized to IMAGE_DIM x IMAGE_DIM.
    """
    print(f"Extracting Canny edges with thresholds ({CANNY_LOW_THRESHOLD}, {CANNY_HIGH_THRESHOLD})...")
    
    # Resize image to square dimensions for ControlNet input
    image = image.resize((IMAGE_DIM, IMAGE_DIM))

    # Convert PIL Image to OpenCV format (numpy array).
    # Ensure it's in BGR format and remove alpha channel if present.
    img_np = np.array(image.convert("RGB")) # Convert to RGB first
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detector
    canny_output = cv2.Canny(img_gray, CANNY_LOW_THRESHOLD, CANNY_HIGH_THRESHOLD)

    # Convert back to PIL Image
    canny_image = Image.fromarray(canny_output)
    print("Canny edge extraction complete.")
    return canny_image

def generate_clothing_illustration(canny_image: Image.Image, diffusion_pipeline, prompt: str, negative_prompt: str) -> Image.Image:
    """
    Generates a 2D anime illustration using Stable Diffusion with ControlNet guidance.
    """
    print("Generating anime illustration...")
    set_seed(42) # For reproducibility

    # Generate image using the loaded pipeline and Canny image as control input
    # num_inference_steps: higher values usually result in better quality but take longer
    # guidance_scale: controls how strongly the image adheres to the prompt (higher = stronger)
    generated_images = diffusion_pipeline(
        prompt=prompt,
        image=canny_image,
        negative_prompt=negative_prompt,
        num_inference_steps=30, # A good balance for quality and speed
        guidance_scale=7.5    # Strong adherence to the prompt
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
        print("Please ensure your background-removed clothing image (e.g., segmented_clothing_output.png) is at the specified path.")
        exit(1)

    try:
        # Open the image and ensure it has an alpha channel for potential transparency
        clothing_image = Image.open(clothing_path).convert("RGBA") 
        print(f"Loaded clothing image from: {clothing_path}")
    except Exception as e:
        print(f"Error loading clothing image: {e}")
        exit(1)

    # --- Step 2: Load ControlNet and Stable Diffusion models ---
    diffusion_pipeline = load_diffusion_pipeline()

    # --- Step 3: Extract clothing silhouette using Canny edge detector ---
    canny_output_image = extract_canny_edges(clothing_image)

    # Optional: Save the Canny edge image for verification
    # canny_output_image.save(os.path.join(OUTPUT_DIR, "canny_edges.png"))
    # print(f"Canny edges saved to {os.path.join(OUTPUT_DIR, "canny_edges.png")}")

    # --- Step 4: Run extracted edges through Stable Diffusion for illustration generation ---
    final_illustration = generate_clothing_illustration(
        canny_output_image,
        diffusion_pipeline,
        PROMPT,
        NEGATIVE_PROMPT
    )

    # --- Step 5: Save the resulting image as a transparent PNG ---
    output_full_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    # Ensure the output image is RGBA for transparency
    final_illustration.save(output_full_path, "PNG")
    print(f"Final anime clothing illustration saved to: {output_full_path}")

    print("\nProcess finished.")
    print("Note: The Stable Diffusion and ControlNet models will download a large amount of data on the first run (several GBs).")
    print("Subsequent runs will be faster as models are cached.")
    print("If you encounter CUDA out of memory errors, try reducing IMAGE_DIM or running on CPU (by setting torch_dtype to torch.float32 and removing .to('cuda')).")

    # --- Post-processing Suggestions (Optional) ---
    print("\n--- Post-processing Suggestions for Output Quality ---")
    print("1. Upscaling: If the 1024x1024 output is not high enough resolution, consider using an image upscaling tool (e.g., Real-ESRGAN, SwinIR, or online AI upscalers) on the generated image.")
    print("2. Refinement with Image Editors: For minor imperfections or artistic touches, a graphic editor like Photoshop, GIMP, or Krita can be used to clean up edges, adjust colors, or add details.")
    print("3. Adjusting Prompts/Parameters: Experiment with the PROMPT, NEGATIVE_PROMPT, num_inference_steps, and guidance_scale in the script to find a style that best fits your needs.")
    print("4. Different Models: Explore other Stable Diffusion or ControlNet models on Hugging Face that specialize in anime or specific art styles for varied results.") 