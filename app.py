"""
AIstylist - Main Application
統合されたフロントエンドとバックエンドのWebアプリケーション
"""

import os
import sys
import base64
import datetime
import glob
from flask import Flask, render_template, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from openai import OpenAI
from dotenv import load_dotenv

# バックエンド機能のインポート
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from generate_item import analyze_image
from style_agent import select_outfit, load_closet_txts
from generate_visualisation import generate_image, sanitize_prompt

# 環境変数の読み込み
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # 設定
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'data', 'clothes', 'input')
    app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'output')
    
    # ディレクトリの作成
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # OpenAI APIキーの確認
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables")
    
    @app.route('/')
    def index():
        """メインページ"""
        return render_template('home.html')
    
    @app.route('/upload', methods=['POST'])
    def upload_clothing():
        """服の画像をアップロードして分析"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # 画像を分析
                description = analyze_image(filepath, api_key)
                
                # 説明をテキストファイルとして保存
                txt_filename = os.path.splitext(filename)[0] + '.txt'
                txt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
                with open(txt_filepath, 'w', encoding='utf-8') as f:
                    f.write(description)
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'description': description,
                    'message': 'Clothing item analyzed successfully'
                })
                
            except Exception as e:
                return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
    
    @app.route('/generate-outfit', methods=['POST'])
    def generate_outfit():
        """天候とシーンに基づいてアウトフィットを生成"""
        data = request.get_json()
        weather = data.get('weather', '')
        occasion = data.get('occasion', '')
        
        try:
            # スタイル選択
            criteria = {'weather': weather, 'occasion': occasion}
            selected_items = select_outfit(criteria, app.config['UPLOAD_FOLDER'])
            
            if not selected_items:
                return jsonify({'error': 'No suitable outfit found'}), 404
            
            # アバターファイルのパス
            avatar_path = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
            
            # 選択された服のパス
            clothing_paths = [os.path.join(app.config['UPLOAD_FOLDER'], item) for item in selected_items]
            
            # 画像生成
            try:
                # テキストファイルの内容を読み込み
                texts = []
                for path in [avatar_path] + clothing_paths:
                    with open(path, 'r', encoding='utf-8') as f:
                        texts.append(f.read().strip())
                
                # プロンプトを組み合わせてサニタイズ
                raw_prompt = "\n".join(texts)
                prompt = sanitize_prompt(raw_prompt)
                
                # 画像生成
                image_bytes = generate_image(prompt, api_key)
                
                # 画像を保存
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"styled_avatar_{timestamp}.png"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                
                return jsonify({
                    'success': True,
                    'image_url': f'/output/{output_filename}',
                    'selected_items': selected_items,
                    'message': 'Outfit generated successfully'
                })
                
            except Exception as e:
                return jsonify({'error': f'Image generation failed: {str(e)}'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Outfit generation failed: {str(e)}'}), 500
    
    @app.route('/closet')
    def get_closet():
        """クローゼットの内容を取得"""
        try:
            items = load_closet_txts(app.config['UPLOAD_FOLDER'])
            return jsonify({
                'success': True,
                'items': items
            })
        except Exception as e:
            return jsonify({'error': f'Failed to load closet: {str(e)}'}), 500
    
    @app.route('/output/<filename>')
    def serve_output(filename):
        """生成された画像を提供"""
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """静的ファイルを提供"""
        return send_from_directory('static', filename)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000) 