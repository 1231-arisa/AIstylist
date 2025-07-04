import os
import sys
import glob
import subprocess

# Settings
CLOTHES_IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'data', 'clothes', 'input')
CLOTHES_TXT_DIR = CLOTHES_IMAGE_DIR  # Output text files in the same location
AVATAR_TXT = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
STYLE_AGENT = os.path.join(os.path.dirname(__file__), 'src', 'style_agent.py')
GENERATE_ITEM = os.path.join(os.path.dirname(__file__), 'src', 'generate_item.py')
GENERATE_VIS = os.path.join(os.path.dirname(__file__), 'src', 'generate_visualisation.py')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

os.makedirs(OUTPUT_DIR, exist_ok=True)

def batch_generate_descriptions():
    """Generate descriptions from image files"""
    print("=== Step 1: Generating clothing descriptions ===")
    image_files = glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.jpg')) + \
                  glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.jpeg')) + \
                  glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.png'))
    if not image_files:
        print("No image files found in", CLOTHES_IMAGE_DIR)
        return
    print(f"Found {len(image_files)} image files")
    for img in image_files:
        txt_path = os.path.splitext(img)[0] + '.txt'
        if os.path.exists(txt_path):
            print(f"Skipping {os.path.basename(img)} - description already exists")
            continue  # Skip if description already exists
        print(f"Generating description for {os.path.basename(img)}...")
        try:
            result = subprocess.run([sys.executable, GENERATE_ITEM, img], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Successfully generated description for {os.path.basename(img)}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate description for {os.path.basename(img)}")
            print(f"Error: {e.stderr}")
            # Continue even if error occurs
        except Exception as e:
            print(f"❌ Unexpected error for {os.path.basename(img)}: {e}")

def select_multiple_outfits(num=4):
    """
    Call select_multiple_outfits from style_agent.py as a subprocess,
    and return up to num outfit combinations (each as a list of .txt filenames)
    """
    print(f"\n=== Step 2: Selecting {num} outfit patterns ===")
    try:
        code = (
            "import sys; "
            "from style_agent import select_multiple_outfits; "
            f"outfits = select_multiple_outfits(num={num}); "
            "print('Recommended outfits:', outfits)"
        )
        result = subprocess.run([sys.executable, '-c', code],
                                cwd=os.path.join(os.path.dirname(__file__), 'src'),
                                capture_output=True, text=True, check=True)
        print("Style agent output:")
        print(result.stdout)
        for line in result.stdout.splitlines():
            if line.startswith('Recommended outfits:'):
                outfits_str = line.split(':', 1)[1].strip()
                try:
                    outfits = eval(outfits_str)  # [[...], [...], ...]
                    selected_paths = []
                    for files in outfits:
                        selected_paths.append([os.path.join(CLOTHES_TXT_DIR, f) for f in files])
                    print(f"✅ Selected outfit files: {selected_paths}")
                    return selected_paths
                except Exception as e:
                    print(f"❌ Error parsing outfit selection: {e}")
                    return []
        print("❌ No outfit selection found in output")
        return []
    except subprocess.CalledProcessError as e:
        print(f"❌ Style agent failed: {e}")
        print(f"Error output: {e.stderr}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error in outfit selection: {e}")
        return []

def generate_final_images(multi_selected_txts):
    """
    Generate final styled images for multiple outfits
    """
    print("\n=== Step 3: Generating final styled images ===")
    if not multi_selected_txts:
        print("❌ No clothing files selected for image generation")
        return
    for idx, selected_txts in enumerate(multi_selected_txts):
        print(f"Generating image for outfit {idx+1} with {len(selected_txts)} clothing items")
        print(f"Avatar file: {AVATAR_TXT}")
        print(f"Clothing files: {[os.path.basename(f) for f in selected_txts]}")
        try:
            cmd = [sys.executable, GENERATE_VIS, AVATAR_TXT] + selected_txts + ['--output-dir', OUTPUT_DIR]
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Image generation for outfit {idx+1} completed successfully")
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Image generation failed for outfit {idx+1}: {e}")
            print(f"Error output: {e.stderr}")
        except Exception as e:
            print(f"❌ Unexpected error in image generation for outfit {idx+1}: {e}")

def check_environment():
    """Check environment setup"""
    print("=== Environment Check ===")
    required_dirs = [CLOTHES_IMAGE_DIR, OUTPUT_DIR]
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - creating...")
            os.makedirs(dir_path, exist_ok=True)
    if os.path.exists(AVATAR_TXT):
        print(f"✅ {AVATAR_TXT}")
    else:
        print(f"❌ {AVATAR_TXT} - missing!")
        return False
    scripts = [STYLE_AGENT, GENERATE_ITEM, GENERATE_VIS]
    for script in scripts:
        if os.path.exists(script):
            print(f"✅ {script}")
        else:
            print(f"❌ {script} - missing!")
            return False
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY not set - some features may not work")
    return True

def main():
    """Main function"""
    print("AIstylist Pipeline")
    print("=" * 50)
    if not check_environment():
        print("❌ Environment check failed. Please fix the issues above.")
        return
    print("\nStarting pipeline...")
    batch_generate_descriptions()
    multi_selected_txts = select_multiple_outfits(num=4)
    if not multi_selected_txts:
        print("❌ No outfit selected. Pipeline cannot continue.")
        return
    generate_final_images(multi_selected_txts)
    print("\n" + "=" * 50)
    print("Pipeline completed!")
    print(f"Check the output directory: {OUTPUT_DIR}")

if __name__ == '__main__':
    main() 