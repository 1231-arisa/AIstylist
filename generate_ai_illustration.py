import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

# 1️⃣ Load Stable Diffusion model for style transformation
pipeline = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")

# Apply illustration-style transformation to clothing image
styled_clothing = pipeline(
    "segmented_clothing_output.png",
    prompt="anime style illustration, soft shading, clean lines"
)
styled_clothing.save("avatar_style_clothing.png")

# 2️⃣ Merge the styled clothing onto the avatar image
avatar = Image.open("avatar.png").convert("RGBA")
clothing = Image.open("avatar_style_clothing.png").convert("RGBA")

# Adjust position and overlay clothing onto avatar
avatar.paste(clothing, (50, 100), clothing)
avatar.save("final_styled_avatar.png")

print("🎨 AI-generated illustrated outfit applied to avatar successfully!")
