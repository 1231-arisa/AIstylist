"""
AIstylist - Main Application
Integrated frontend and backend web application
"""

import os
import sys
import base64
import datetime
import glob
import requests
import hashlib
import pytz
from flask import Flask, render_template, request, jsonify, send_from_directory, current_app, redirect, url_for, session
from werkzeug.utils import secure_filename
from openai import OpenAI
from dotenv import load_dotenv
from flask_dance.contrib.google import make_google_blueprint, google

# Import backend functionality
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from generate_item import analyze_image
from style_agent import select_outfit, load_closet_txts, select_multiple_outfits
from generate_visualisation import generate_image, sanitize_prompt

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")  # Use a secure key in production
    
    # Google OAuth setup (compatible with Hugging Face Spaces)
    google_bp = make_google_blueprint(
        client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        scope=["profile", "email"],
        redirect_url="/login/google/authorized"
    )
    app.register_blueprint(google_bp, url_prefix="/login")
    
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
    
    def get_vancouver_time():
        """Get current time in Vancouver timezone"""
        vancouver_tz = pytz.timezone('America/Vancouver')
        return datetime.datetime.now(vancouver_tz)
    
    def should_generate_daily_outfits():
        """Check if it's time to generate daily outfits (after 5 AM Vancouver time)"""
        vancouver_time = get_vancouver_time()
        five_am = vancouver_time.replace(hour=5, minute=0, second=0, microsecond=0)
        return vancouver_time >= five_am
    
    def get_daily_outfits_status():
        """Get status of daily outfit generation"""
        vancouver_time = get_vancouver_time()
        today_str = vancouver_time.strftime("%Y%m%d")
        output_dir = app.config['OUTPUT_FOLDER']
        
        # Check if today's outfits exist
        today_files = [
            f for f in os.listdir(output_dir)
            if f.startswith(f"daily_outfit_{today_str}_") and f.endswith(".png")
        ]
        
        five_am = vancouver_time.replace(hour=5, minute=0, second=0, microsecond=0)
        next_generation = five_am + datetime.timedelta(days=1)
        
        return {
            'vancouver_time': vancouver_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'today_generated': len(today_files) >= 4,
            'generated_count': len(today_files),
            'should_generate': should_generate_daily_outfits(),
            'next_generation': next_generation.strftime("%Y-%m-%d %H:%M:%S %Z")
        }
    
    def get_vancouver_weather():
        """Fetch current weather in Vancouver using WeatherAPI and return a simplified weather category."""
        api_key = os.getenv("WEATHER_API_KEY")
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": "Vancouver",
            "aqi": "no"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            weather_text = data["current"]["condition"]["text"].lower()
            # Map WeatherAPI condition to our categories
            if "rain" in weather_text:
                return "rainy"
            elif "snow" in weather_text:
                return "cold"
            elif "cloud" in weather_text or "overcast" in weather_text:
                return "cloudy"
            elif "sun" in weather_text or "clear" in weather_text:
                return "warm"
            else:
                return "warm"
        except Exception as e:
            print(f"Weather API error: {e}")
            return "warm"  # fallback
    
    def get_vancouver_weather_detail():
        api_key = os.getenv("WEATHER_API_KEY")
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": "Vancouver",
            "aqi": "no"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            weather_text = data["current"]["condition"]["text"]
            temp_f = data["current"]["temp_f"]
            temp_c = data["current"]["temp_c"]
            icon_url = data["current"]["condition"]["icon"]
            return {
                "text": weather_text,
                "temp_f": temp_f,
                "temp_c": temp_c,
                "icon_url": icon_url
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return {
                "text": "Sunny",
                "temp_f": 72,
                "temp_c": 22,
                "icon_url": ""
            }
    
    def get_outfit_key(files):
        """Generate a unique hash key for a combination of clothing files."""
        key = '_'.join(sorted(files))
        return hashlib.md5(key.encode()).hexdigest()
    
    def generate_daily_outfits(weather=None, force_generate=False):
        """
        List up to 4 daily outfit images generated at 5am (Vancouver time) from output/.
        If no images exist for today, display up to 4 most recent .png images from output/.
        Never call the image generation API here. Only use existing images.
        If no images exist at all, return a dummy image.
        """
        vancouver_time = get_vancouver_time()
        today_str = vancouver_time.strftime("%Y%m%d")
        output_dir = app.config['OUTPUT_FOLDER']

        # 1. Get today's daily outfit images
        today_files = sorted([
            f for f in os.listdir(output_dir)
            if "daily_outfit" in f and today_str in f and f.endswith(".png")
        ])

        # 2. If none, get up to 4 most recent .png images from output/
        if not today_files:
            all_pngs = [f for f in os.listdir(output_dir) if f.endswith(".png")]
            all_pngs = sorted(all_pngs, key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
            today_files = all_pngs[:4]

        outfits = []
        if today_files:
            for idx, filename in enumerate(today_files[:4]):
                outfits.append({
                    'name': f'Outfit {idx+1}',
                    'image': f'/output/{filename}',
                    'weather': 'Any',
                    'occasion': 'Any',
                    'files': []
                })
        else:
            outfits.append({
                'name': 'No Outfit',
                'image': '/static/images/avatar-placeholder.svg',
                'weather': 'Any',
                'occasion': 'Any',
                'files': []
            })
        return outfits
    
    def generate_single_outfit(weather=None):
        """Generate a single outfit recommendation manually"""
        vancouver_time = get_vancouver_time()
        timestamp = vancouver_time.strftime("%Y%m%d_%H%M%S")
        output_dir = app.config['OUTPUT_FOLDER']
        closet_dir = app.config['UPLOAD_FOLDER']
        avatar_path = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
                    
        # Select one outfit
        criteria = {'weather': weather} if weather else None
        outfit_files_list = select_multiple_outfits(num=1, closet_dir=closet_dir, criteria=criteria)
        
        return None
        
        files = outfit_files_list[0]
        outfit_key = get_outfit_key(files)
        manual_filename = f"manual_outfit_{timestamp}_{outfit_key[:8]}.png"
        manual_output_path = os.path.join(output_dir, manual_filename)
        
        # Check if we can reuse an existing outfit image
        existing_outfits = {}
        for f in os.listdir(output_dir):
            if f.startswith("outfit_") and f.endswith(".png"):
                key = f[len("outfit_"):-4]
                existing_outfits[key] = f
        
        if outfit_key in existing_outfits:
            existing_path = os.path.join(output_dir, existing_outfits[outfit_key])
            import shutil
            shutil.copy2(existing_path, manual_output_path)
            return {
                'name': 'Manual Outfit',
                'image': f'/output/{manual_filename}',
                'weather': weather.title() if weather else 'Any',
                'occasion': 'Any',
                'files': files
            }
        
        try:
            clothing_paths = [os.path.join(closet_dir, f) for f in files]
            texts = []
            for path in [avatar_path] + clothing_paths:
                with open(path, 'r', encoding='utf-8') as f:
                    texts.append(f.read().strip())
            raw_prompt = "\n".join(texts)
            prompt = sanitize_prompt(raw_prompt)
            image_bytes = generate_image(prompt, api_key)
            with open(manual_output_path, "wb") as f:
                f.write(image_bytes)
            return {
                'name': 'Manual Outfit',
                'image': f'/output/{manual_filename}',
                'weather': weather.title() if weather else 'Any',
                'occasion': 'Any',
                'files': files
            }
        except Exception as e:
            print(f"Failed to generate manual outfit: {e}")
            return None
    
    def manual_outfit_generated_today():
        vancouver_time = get_vancouver_time()
        today_str = vancouver_time.strftime("%Y%m%d")
        output_dir = app.config['OUTPUT_FOLDER']
        manual_files = [
            f for f in os.listdir(output_dir)
            if f.startswith(f"manual_outfit_{today_str}_") and f.endswith(".png")
        ]
        return len(manual_files) > 0
    
    @app.route('/')
    def index():
        """Main page"""
        outfits = generate_daily_outfits()
        weather_info = get_vancouver_weather_detail()
        return render_template('home.html', outfits=outfits, weather_info=weather_info)
    
    @app.route('/upload', methods=['POST'])
    def upload_clothing():
        """Upload clothing image only (no AI analysis)."""
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'Clothing image uploaded successfully'
            })
    
    @app.route('/generate-outfit', methods=['POST'])
    def generate_outfit():
        """
        Disabled: Image generation is only allowed at 5am or via the manual generation button.
        This endpoint no longer generates images to comply with the project rules.
        """
        return jsonify({'error': 'Outfit generation is only available via the daily (5am) or manual (1/day) feature.'}), 403
    
    @app.route('/closet')
    def get_closet():
        """Get closet contents with category info"""
        try:
            items = load_closet_txts(app.config['UPLOAD_FOLDER'])
            return jsonify({
                'success': True,
                'items': items
            })
        except Exception as e:
            return jsonify({'error': f'Failed to load closet: {str(e)}'}), 500
    
    @app.route('/delete-clothing', methods=['POST'])
    def delete_clothing():
        """Delete a clothing item (image and .txt) from the closet."""
        data = request.get_json()
        filename = data.get('file')
        if not filename or not filename.endswith('.txt'):
            return jsonify({'error': 'Invalid file name'}), 400
        base = filename[:-4]
        folder = app.config['UPLOAD_FOLDER']
        txt_path = os.path.join(folder, filename)
        deleted = []
        # Delete .txt
        if os.path.exists(txt_path):
            os.remove(txt_path)
            deleted.append(txt_path)
        # Delete associated image(s)
        for ext in ['.jpg', '.jpeg', '.png']:
            img_path = os.path.join(folder, base + ext)
            if os.path.exists(img_path):
                os.remove(img_path)
                deleted.append(img_path)
        if deleted:
            return jsonify({'success': True, 'deleted': deleted})
        else:
            return jsonify({'error': 'File not found'}), 404
    
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
    
    @app.route('/weather-outfits')
    def weather_outfits():
        weather_info = get_vancouver_weather_detail()
        outfits = generate_daily_outfits(weather=weather_info["text"].lower())
        return render_template('home.html', outfits=outfits, weather_info=weather_info)
    
    @app.route('/generate-single-outfit', methods=['POST'])
    def generate_single_outfit_endpoint():
        """Generate a single outfit recommendation manually (max 1 per day)"""
        try:
            if manual_outfit_generated_today():
                return jsonify({'error': 'Manual outfit already generated today. Try again tomorrow.'}), 400
            data = request.get_json() or {}
            weather = data.get('weather', None)
            outfit = generate_single_outfit(weather=weather)
            if outfit:
                return jsonify({
                    'success': True,
                    'outfit': outfit,
                    'message': 'Manual outfit generated successfully'
                })
            else:
                return jsonify({'error': 'Failed to generate outfit'}), 500
        except Exception as e:
            return jsonify({'error': f'Manual outfit generation failed: {str(e)}'}), 500
    
    @app.route('/daily-outfits-status')
    def daily_outfits_status():
        """Get status of daily outfit generation"""
        try:
            status = get_daily_outfits_status()
            return jsonify({
                'success': True,
                'status': status
            })
        except Exception as e:
            return jsonify({'error': f'Failed to get status: {str(e)}'}), 500
    
    @app.route('/force-generate-daily')
    def force_generate_daily():
        """Force generate daily outfits (admin function)"""
        try:
            outfits = generate_daily_outfits(force_generate=True)
            return jsonify({
                'success': True,
                'outfits': outfits,
                'message': 'Daily outfits force generated successfully'
            })
        except Exception as e:
            return jsonify({'error': f'Force generation failed: {str(e)}'}), 500
    
    @app.route('/chat', methods=['POST'])
    def chat():
        """Q&A chat endpoint: receives a user message or image and returns an AI reply or outfit recommendation."""
        try:
            data = request.get_json()
            user_message = data.get('message', '').strip() if data.get('message') else ''
            image_base64 = data.get('image_base64', None)

            if image_base64:
                # If an image is sent, analyze and recommend matching closet items
                import base64, tempfile
                from generate_item import analyze_image
                from style_agent import select_outfit, load_closet_txts

                # Save the image temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                    tmp.write(base64.b64decode(image_base64.split(',')[-1]))
                    tmp_path = tmp.name

                # Analyze the clothing item
                api_key = os.getenv("OPENAI_API_KEY")
                description = analyze_image(tmp_path, api_key=api_key)

                # Select recommended outfit from closet
                criteria = {}  # You can add weather/occasion info if needed
                outfit_files = select_outfit(criteria)
                closet_items = load_closet_txts(app.config['UPLOAD_FOLDER'])
                outfit_descs = [item['desc'] for item in closet_items if item['file'] in outfit_files]

                # Build the response text
                if outfit_descs:
                    reply = "Here are some items from your closet that would match this piece:\n" + "\n".join(outfit_descs)
                else:
                    reply = "Sorry, I couldn't find a matching outfit in your closet."

                return jsonify({'reply': reply})

            elif user_message:
                # If only text, use OpenAI chat as before
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    return jsonify({'error': 'OpenAI API key not set.'}), 500

                import openai
                openai.api_key = api_key
                try:
                    response = openai.ChatCompletion.create(
                        model='gpt-3.5-turbo',
                        messages=[{"role": "system", "content": "You are a helpful AI fashion stylist. Answer user questions about fashion, outfits, and style."},
                                  {"role": "user", "content": user_message}]
                    )
                    reply = response['choices'][0]['message']['content']
                except Exception as e:
                    reply = "Sorry, the AI stylist is temporarily unavailable. Please try again later."
                return jsonify({'reply': reply})
            else:
                return jsonify({'error': 'No message or image provided.'}), 400
        except Exception as e:
            return jsonify({'error': f'Chat endpoint error: {str(e)}'}), 500
    
    @app.route("/login")
    def login():
        return redirect(url_for("google.login"))

    @app.route("/login/google/authorized")
    def google_authorized():
        resp = google.get("/oauth2/v2/userinfo")
        if resp.ok:
            user_info = resp.json()
            session["user"] = {
                "name": user_info.get("name"),
                "email": user_info.get("email"),
                "picture": user_info.get("picture"),
                "initial": user_info.get("name", "?")[0].upper()
            }
            return redirect(url_for("index"))
        return "Failed to login", 401

    @app.route("/logout")
    def logout():
        session.pop("user", None)
        return redirect(url_for("index"))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000) 