"""
test_pipeline.py
Script to test pipeline operation (no API key required)
"""

import os
import sys
import glob
from pathlib import Path

# Settings
CLOTHES_IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'data', 'clothes', 'input')
CLOTHES_TXT_DIR = CLOTHES_IMAGE_DIR
AVATAR_TXT = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

def test_file_structure():
    """Test file structure"""
    print("=== File Structure Test ===")
    required_dirs = [CLOTHES_IMAGE_DIR, OUTPUT_DIR]
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} - exists")
        else:
            print(f"❌ {dir_path} - does not exist")
    if os.path.exists(AVATAR_TXT):
        print(f"✅ {AVATAR_TXT} - exists")
        with open(AVATAR_TXT, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"   Content: {len(content)} characters")
    else:
        print(f"❌ {AVATAR_TXT} - does not exist")

def test_clothing_files():
    """Test clothing files"""
    print("\n=== Clothing File Test ===")
    image_extensions = ['*.jpg', '*.jpeg', '*.png']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(CLOTHES_IMAGE_DIR, ext)))
    print(f"Image file count: {len(image_files)}")
    for img in image_files:
        print(f"  📷 {os.path.basename(img)}")
    txt_files = glob.glob(os.path.join(CLOTHES_TXT_DIR, '*.txt'))
    print(f"\nText file count: {len(txt_files)}")
    for txt in txt_files:
        print(f"  📄 {os.path.basename(txt)}")
        with open(txt, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"     Content: {len(content)} characters")

def test_style_agent_logic():
    """Test style_agent logic"""
    print("\n=== Style Agent Logic Test ===")
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    try:
        from style_agent import load_closet_txts, filter_by_weather, select_outfit
        items = load_closet_txts(CLOTHES_TXT_DIR)
        print(f"✅ Closet loaded: {len(items)} items")
        weather_conditions = ['warm', 'cold', 'rainy', None]
        for weather in weather_conditions:
            filtered = filter_by_weather(items, weather)
            print(f"  {weather or 'no weather'}: {len(filtered)} items")
        criteria = {'weather': 'warm', 'occasion': 'casual'}
        selected = select_outfit(criteria, CLOTHES_TXT_DIR)
        print(f"✅ Outfit selection: {selected}")
    except ImportError as e:
        print(f"❌ Module import error: {e}")
    except Exception as e:
        print(f"❌ Logic test error: {e}")

def test_pipeline_flow():
    """Test pipeline flow"""
    print("\n=== Pipeline Flow Test ===")
    image_files = glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.jpg')) + \
                  glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.jpeg')) + \
                  glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.png'))
    print(f"Step 1: Found {len(image_files)} image files")
    txt_files = []
    for img in image_files:
        txt_path = os.path.splitext(img)[0] + '.txt'
        if os.path.exists(txt_path):
            txt_files.append(txt_path)
    print(f"Step 2: Found {len(txt_files)} text files")
    if txt_files:
        selected_files = txt_files[:2]
        print(f"Step 3: Selected files: {[os.path.basename(f) for f in selected_files]}")
        if os.path.exists(OUTPUT_DIR):
            print(f"Step 4: Output directory {OUTPUT_DIR} exists")
        else:
            print(f"Step 4: Output directory {OUTPUT_DIR} needs to be created")
    else:
        print("❌ No text files found, cannot run pipeline")

def main():
    """Main function"""
    print("AIstylist Pipeline Test")
    print("=" * 50)
    test_file_structure()
    test_clothing_files()
    test_style_agent_logic()
    test_pipeline_flow()
    print("\n" + "=" * 50)
    print("Test complete")
    print("\nNext steps:")
    print("1. Create a .env file and set OPENAI_API_KEY")
    print("2. Run python run_full_pipeline.py")

if __name__ == '__main__':
    main() 