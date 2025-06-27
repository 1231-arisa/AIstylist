"""
AIstylist - Main Application
Integrated frontend and backend web application
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

# Import backend functionality
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from generate_item import analyze_image
from style_agent import select_outfit, load_closet_txts
from generate_visualisation import generate_image, sanitize_prompt

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'data', 'clothes', 'input')
    app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'output')
    
    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables")
    
    def generate_daily_outfits():
        """Generate daily outfit recommendations"""
        outfits = []
        
        # Weather and occasion combinations
        weather_occasions = [
            ('warm', 'casual'),
            ('cold', 'formal'),
            ('rainy', 'casual'),
            ('warm', 'work')
        ]
        
        for weather, occasion in weather_occasions:
            try:
                # Style selection
                criteria = {'weather': weather, 'occasion': occasion}
                selected_items = select_outfit(criteria, app.config['UPLOAD_FOLDER'])
                
                if selected_items:
                    # Avatar file path
                    avatar_path = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
                    
                    # Selected clothing paths
                    clothing_paths = [os.path.join(app.config['UPLOAD_FOLDER'], item) for item in selected_items]
                    
                    # Image generation (only if API key is available)
                    if api_key:
                        try:
                            # Read text file contents
                            texts = []
                            for path in [avatar_path] + clothing_paths:
                                with open(path, 'r', encoding='utf-8') as f:
                                    texts.append(f.read().strip())
                            
                            # Combine and sanitize prompt
                            raw_prompt = "\n".join(texts)
                            prompt = sanitize_prompt(raw_prompt)
                            
                            # Generate image
                            image_bytes = generate_image(prompt, api_key)
                            
                            # Save image
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            output_filename = f"daily_outfit_{weather}_{occasion}_{timestamp}.png"
                            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                            
                            with open(output_path, "wb") as f:
                                f.write(image_bytes)
                            
                            outfits.append({
                                'name': f'{weather.title()} {occasion.title()} Look',
                                'image': f'/output/{output_filename}',
                                'weather': weather.title(),
                                'occasion': occasion.title()
                            })
                            
                        except Exception as e:
                            print(f"Failed to generate image for {weather}/{occasion}: {e}")
                            # Fallback: default avatar
                            outfits.append({
                                'name': f'{weather.title()} {occasion.title()} Look',
                                'image': '/static/images/avatar-placeholder.svg',
                                'weather': weather.title(),
                                'occasion': occasion.title()
                            })
                    else:
                        # Fallback when no API key
                        outfits.append({
                            'name': f'{weather.title()} {occasion.title()} Look',
                            'image': '/static/images/avatar-placeholder.svg',
                            'weather': weather.title(),
                            'occasion': occasion.title()
                        })
                        
            except Exception as e:
                print(f"Failed to generate outfit for {weather}/{occasion}: {e}")
        
        return outfits
    
    @app.route('/')
    def index():
        """Main page"""
        # 4つのおすすめコーデを生成
        outfits = generate_daily_outfits()
        return render_template('home.html', outfits=outfits)
    
    @app.route('/upload', methods=['POST'])
    def upload_clothing():
        """Upload and analyze clothing image"""
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
                # Analyze image
                description = analyze_image(filepath, api_key)
                
                # Save description as text file
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
        """Generate outfit based on weather and occasion"""
        data = request.get_json()
        weather = data.get('weather', '')
        occasion = data.get('occasion', '')
        
        try:
            # Style selection
            criteria = {'weather': weather, 'occasion': occasion}
            selected_items = select_outfit(criteria, app.config['UPLOAD_FOLDER'])
            
            if not selected_items:
                return jsonify({'error': 'No suitable outfit found'}), 404
            
            # Avatar file path
            avatar_path = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
            
            # Selected clothing paths
            clothing_paths = [os.path.join(app.config['UPLOAD_FOLDER'], item) for item in selected_items]
            
            # Image generation
            try:
                # Read text file contents
                texts = []
                for path in [avatar_path] + clothing_paths:
                    with open(path, 'r', encoding='utf-8') as f:
                        texts.append(f.read().strip())
                
                # Combine and sanitize prompt
                raw_prompt = "\n".join(texts)
                prompt = sanitize_prompt(raw_prompt)
                
                # Generate image
                image_bytes = generate_image(prompt, api_key)
                
                # Save image
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
        """Get closet contents"""
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
        """Serve generated images"""
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files"""
        return send_from_directory('static', filename)
    
    @app.route('/avatar')
    def get_avatar():
        """Get avatar information"""
        try:
            avatar_path = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
            if os.path.exists(avatar_path):
                with open(avatar_path, 'r', encoding='utf-8') as f:
                    avatar_description = f.read().strip()
                return jsonify({
                    'success': True,
                    'description': avatar_description
                })
            else:
                return jsonify({'error': 'Avatar file not found'}), 404
        except Exception as e:
            return jsonify({'error': f'Failed to load avatar: {str(e)}'}), 500
    
    @app.route('/data/clothes/input/<filename>')
    def serve_closet_image(filename):
        folder = os.path.join(os.path.dirname(__file__), 'data', 'clothes', 'input')
        return send_from_directory(folder, filename)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000) 