import cv2
import numpy as np
from PIL import Image
import os
from rembg import remove, new_session

# Global session for rembg to avoid re-loading model for each call
# Using "u2net_human_seg" for better human/clothing segmentation
session = new_session("u2net_human_seg")

def segment_and_crop_clothing(clothing_path):
    """
    Segments the clothing from its background, applies alpha matting,
    smooths edges, and crops the image to the bounding box of the clothing.
    """
    print(f"Starting clothing segmentation for: {clothing_path}...")
    try:
        original_clothing_img = Image.open(clothing_path).convert("RGBA")
        
        # Use rembg with alpha matting for better edge quality
        segmented_img = remove(
            original_clothing_img,
            session=session,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240, # Adjust for foreground sensitivity
            alpha_matting_background_threshold=10,  # Adjust for background sensitivity
            alpha_matting_erode_size=10             # Adjust for smoother edges
        )
        
        # Convert to numpy array for post-processing with OpenCV
        img_array = np.array(segmented_img)
        
        # Ensure background is fully transparent (set very low alpha values to 0)
        alpha = img_array[:, :, 3]
        alpha[alpha < 10] = 0
        
        # Apply slight Gaussian blur to alpha channel for smoother edges
        alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
        
        # Reconstruct the image with the processed alpha channel
        img_array[:, :, 3] = alpha
        processed_segmented_img = Image.fromarray(img_array)
        
        # --- Automatic Bounding Box Detection and Cropping ---
        # Find all non-transparent pixels to determine the bounding box
        coords = np.argwhere(np.array(processed_segmented_img)[:, :, 3] > 0)
        if len(coords) == 0:
            print("No clothing pixels detected after segmentation. Cannot crop.")
            return None
        
        # Get bounding box coordinates (min_row, min_col, max_row, max_col)
        y_min, x_min = coords.min(axis=0)[:2]
        y_max, x_max = coords.max(axis=0)[:2]
        
        # Crop the segmented clothing image to its bounding box
        cropped_clothing = processed_segmented_img.crop((x_min, y_min, x_max, y_max))
        print(f"Clothing segmentation and cropping complete. Cropped size: {cropped_clothing.size}")
        return cropped_clothing

    except FileNotFoundError:
        print(f"Error: Clothing image not found at {clothing_path}")
        return None
    except Exception as e:
        print(f"An error occurred during segmentation or cropping: {e}")
        return None

def composite_images(avatar_path, processed_clothing_img, output_path):
    """
    Overlays the processed (segmented and cropped) clothing image onto the avatar,
    resizing and positioning it naturally.
    """
    print(f"Starting image compositing for avatar: {avatar_path} and clothing...")
    try:
        avatar = Image.open(avatar_path).convert("RGBA") # Ensure avatar has an alpha channel
        
        if processed_clothing_img is None:
            print("Error: Processed clothing image is missing. Cannot composite.")
            return

        print(f"Avatar size: {avatar.size}")
        print(f"Processed clothing size before final resize: {processed_clothing_img.size}")
        
        avatar_width, avatar_height = avatar.size
        
        # --- Intelligent Resizing and Placement ---
        # Define target clothing width relative to avatar's body width (e.g., 45-55%)
        # These ratios are critical for natural fit and might need fine-tuning
        target_clothing_width_on_avatar = int(avatar_width * 0.5) # Example: 50% of avatar width
        
        # Calculate desired height maintaining aspect ratio of the cropped clothing
        original_cropped_width, original_cropped_height = processed_clothing_img.size
        if original_cropped_width == 0:
            print("Error: Cropped clothing width is zero. Cannot resize for composition.")
            return
        
        aspect_ratio = original_cropped_height / original_cropped_width
        target_clothing_height_on_avatar = int(target_clothing_width_on_avatar * aspect_ratio)
        
        # Resize clothing for final paste
        if target_clothing_width_on_avatar == 0 or target_clothing_height_on_avatar == 0:
            print("Error: Target clothing dimensions are zero. Cannot paste.")
            return
            
        clothing_to_paste = processed_clothing_img.resize(
            (target_clothing_width_on_avatar, target_clothing_height_on_avatar), Image.LANCZOS
        )
        print(f"Clothing resized for pasting. Final size: {clothing_to_paste.size}")
        
        # Calculate position to paste the clothing on the avatar
        # Center horizontally
        x_offset = (avatar_width - clothing_to_paste.size[0]) // 2
        # Position vertically (adjust this to fit on upper body/torso)
        # Example: 18% down from the top of the avatar
        y_offset = int(avatar_height * 0.18) 
        
        # Create a blank image with alpha channel for the composite (same size as avatar)
        composite = Image.new("RGBA", avatar.size)
        
        # Paste avatar onto the composite
        composite.paste(avatar, (0, 0))
        
        # Paste clothing onto the composite using its alpha channel as mask
        print("Pasting clothing onto avatar...")
        composite.paste(clothing_to_paste, (x_offset, y_offset), clothing_to_paste)
        
        # Save the final composite image
        print(f"Saving composite image to {output_path}...")
        composite.save(output_path, "PNG")
        print("Done! Composite image saved successfully.")

    except FileNotFoundError:
        print(f"Error: Avatar image not found at {avatar_path}")
    except Exception as e:
        print(f"An error occurred during compositing: {e}")

if __name__ == "__main__":
    # Define input and output paths
    # Make sure 'input/clothing.jpg' and 'input/avatar.png' exist
    # The 'output/' directory will be created if it doesn't exist
    clothing_image_path = "input/Navyshirt.jpg" # Using Navyshirt.jpg as input
    avatar_image_path = "input/avatar.png"
    output_composite_path = "output/avatar_with_clothing.png"

    # Ensure input files exist
    if not os.path.exists(clothing_image_path):
        print(f"Error: Clothing image not found at {clothing_image_path}")
        exit(1)
    
    if not os.path.exists(avatar_image_path):
        print(f"Error: Avatar image not found at {avatar_image_path}")
        exit(1)

    # Step 1: Segment and crop the clothing image
    processed_clothing = segment_and_crop_clothing(clothing_image_path)
    
    if processed_clothing:
        # Step 2: Composite the processed clothing onto the avatar
        composite_images(avatar_image_path, processed_clothing, output_composite_path)
    else:
        print("Clothing segmentation failed. Skipping compositing.")