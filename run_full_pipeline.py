import os
import sys
import glob
import subprocess

# 設定
CLOTHES_IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'data', 'clothes', 'input')
CLOTHES_TXT_DIR = CLOTHES_IMAGE_DIR  # テキストも同じ場所に出力
AVATAR_TXT = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
STYLE_AGENT = os.path.join(os.path.dirname(__file__), 'src', 'style_agent.py')
GENERATE_ITEM = os.path.join(os.path.dirname(__file__), 'src', 'generate_item.py')
GENERATE_VIS = os.path.join(os.path.dirname(__file__), 'src', 'generate_visualisation.py')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

os.makedirs(OUTPUT_DIR, exist_ok=True)

def batch_generate_descriptions():
    # 画像ファイルをすべて取得
    image_files = glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.jpg')) + \
                  glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.jpeg')) + \
                  glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.png'))
    for img in image_files:
        txt_path = os.path.splitext(img)[0] + '.txt'
        if os.path.exists(txt_path):
            continue  # 既に説明があればスキップ
        print(f"[1/3] Generating description for {os.path.basename(img)}...")
        subprocess.run([sys.executable, GENERATE_ITEM, img], check=True)

def select_outfit():
    print("[2/3] Selecting outfit...")
    result = subprocess.run([sys.executable, STYLE_AGENT], capture_output=True, text=True, check=True)
    # 例: "Recommended outfit: ['blouse.txt', 'pants.txt']"
    for line in result.stdout.splitlines():
        if line.startswith('Recommended outfit:'):
            files = eval(line.split(':', 1)[1].strip())
            return [os.path.join(CLOTHES_TXT_DIR, f) for f in files]
    raise RuntimeError('No outfit selected.')

def generate_final_image(selected_txts):
    print("[3/3] Generating final styled image...")
    cmd = [sys.executable, GENERATE_VIS, AVATAR_TXT] + selected_txts + ['--output-dir', OUTPUT_DIR]
    subprocess.run(cmd, check=True)

def main():
    batch_generate_descriptions()
    selected_txts = select_outfit()
    generate_final_image(selected_txts)
    print("\nAll done! Check the output directory for results.")

if __name__ == '__main__':
    main() 