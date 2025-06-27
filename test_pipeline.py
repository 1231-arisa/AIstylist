"""
test_pipeline.py
パイプラインの動作をテストするスクリプト（APIキー不要）
"""

import os
import sys
import glob
from pathlib import Path

# 設定
CLOTHES_IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'data', 'clothes', 'input')
CLOTHES_TXT_DIR = CLOTHES_IMAGE_DIR
AVATAR_TXT = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

def test_file_structure():
    """ファイル構造のテスト"""
    print("=== ファイル構造テスト ===")
    
    # 必要なディレクトリの存在確認
    required_dirs = [CLOTHES_IMAGE_DIR, OUTPUT_DIR]
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} - 存在")
        else:
            print(f"❌ {dir_path} - 存在しない")
    
    # アバターファイルの確認
    if os.path.exists(AVATAR_TXT):
        print(f"✅ {AVATAR_TXT} - 存在")
        with open(AVATAR_TXT, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"   内容: {len(content)} 文字")
    else:
        print(f"❌ {AVATAR_TXT} - 存在しない")

def test_clothing_files():
    """服のファイルのテスト"""
    print("\n=== 服のファイルテスト ===")
    
    # 画像ファイルの確認
    image_extensions = ['*.jpg', '*.jpeg', '*.png']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(CLOTHES_IMAGE_DIR, ext)))
    
    print(f"画像ファイル数: {len(image_files)}")
    for img in image_files:
        print(f"  📷 {os.path.basename(img)}")
    
    # テキストファイルの確認
    txt_files = glob.glob(os.path.join(CLOTHES_TXT_DIR, '*.txt'))
    print(f"\nテキストファイル数: {len(txt_files)}")
    for txt in txt_files:
        print(f"  📄 {os.path.basename(txt)}")
        with open(txt, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"    内容: {len(content)} 文字")

def test_style_agent_logic():
    """style_agentのロジックテスト"""
    print("\n=== Style Agent ロジックテスト ===")
    
    # srcディレクトリをパスに追加
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from style_agent import load_closet_txts, filter_by_weather, select_outfit
        
        # クローゼットの読み込みテスト
        items = load_closet_txts(CLOTHES_TXT_DIR)
        print(f"✅ クローゼット読み込み: {len(items)} アイテム")
        
        # 天候フィルタリングテスト
        weather_conditions = ['warm', 'cold', 'rainy', None]
        for weather in weather_conditions:
            filtered = filter_by_weather(items, weather)
            print(f"  {weather or 'no weather'}: {len(filtered)} アイテム")
        
        # アウトフィット選択テスト
        criteria = {'weather': 'warm', 'occasion': 'casual'}
        selected = select_outfit(criteria, CLOTHES_TXT_DIR)
        print(f"✅ アウトフィット選択: {selected}")
        
    except ImportError as e:
        print(f"❌ モジュールインポートエラー: {e}")
    except Exception as e:
        print(f"❌ ロジックテストエラー: {e}")

def test_pipeline_flow():
    """パイプラインフローのテスト"""
    print("\n=== パイプラインフローテスト ===")
    
    # ステップ1: 画像ファイルの確認
    image_files = glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.jpg')) + \
                  glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.jpeg')) + \
                  glob.glob(os.path.join(CLOTHES_IMAGE_DIR, '*.png'))
    
    print(f"ステップ1: {len(image_files)} 個の画像ファイルを確認")
    
    # ステップ2: 対応するテキストファイルの確認
    txt_files = []
    for img in image_files:
        txt_path = os.path.splitext(img)[0] + '.txt'
        if os.path.exists(txt_path):
            txt_files.append(txt_path)
    
    print(f"ステップ2: {len(txt_files)} 個のテキストファイルが存在")
    
    # ステップ3: アウトフィット選択のシミュレーション
    if txt_files:
        # 最初の2つのファイルを選択（実際のロジックをシミュレート）
        selected_files = txt_files[:2]
        print(f"ステップ3: 選択されたファイル: {[os.path.basename(f) for f in selected_files]}")
        
        # ステップ4: 出力ディレクトリの確認
        if os.path.exists(OUTPUT_DIR):
            print(f"ステップ4: 出力ディレクトリ {OUTPUT_DIR} が存在")
        else:
            print(f"ステップ4: 出力ディレクトリ {OUTPUT_DIR} を作成する必要があります")
    else:
        print("❌ テキストファイルが見つからないため、パイプラインを実行できません")

def main():
    """メイン関数"""
    print("AIstylist パイプラインテスト")
    print("=" * 50)
    
    test_file_structure()
    test_clothing_files()
    test_style_agent_logic()
    test_pipeline_flow()
    
    print("\n" + "=" * 50)
    print("テスト完了")
    print("\n次のステップ:")
    print("1. .envファイルを作成し、OPENAI_API_KEYを設定")
    print("2. python run_full_pipeline.py を実行")

if __name__ == '__main__':
    main() 