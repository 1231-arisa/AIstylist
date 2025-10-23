"""
AIstylist - Main Application
Integrated frontend and backend web application
"""

import os
import sys
import base64
from datetime import datetime
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
from generate_item import analyze_image, get_image_hash

def extract_item_info(analysis_text):
    """Extract item name and category from analysis text with detailed features."""
    if not analysis_text:
        return "Unknown Item", "Accessories"
    
    text_lower = analysis_text.lower()
    
    # Extract detailed features
    color = extract_color(text_lower)
    material = extract_material(text_lower)
    style_details = extract_style_details(text_lower)
    item_type = extract_item_type(text_lower)
    
    # Create a detailed name
    name_parts = []
    
    if color and color != "Unknown":
        name_parts.append(color)
    
    if material and material != "Unknown":
        name_parts.append(material)
    
    if style_details and style_details != "Unknown":
        name_parts.append(style_details)
    
    if item_type:
        name_parts.append(item_type)
    
    if not name_parts:
        item_name = "Clothing Item"
    else:
        item_name = " ".join(name_parts)
    
    # Determine category
    if any(word in text_lower for word in ['dress']):
        category = 'Dresses'
    elif any(word in text_lower for word in ['blouse', 'top', 'shirt', 't-shirt', 'sweater', 'hoodie', 'tank', 'crop', 'blazer', 'cardigan', 'pullover', 'polo', 'camisole', 'tunic']):
        category = 'Tops'
    elif any(word in text_lower for word in ['pants', 'skirt', 'jeans', 'shorts', 'trousers', 'leggings', 'capri', 'cargo', 'chinos']):
        category = 'Bottoms'
    elif any(word in text_lower for word in ['shoes', 'sneaker', 'boot', 'sandals', 'loafer', 'heel', 'sneakers', 'boots', 'flats', 'pumps', 'oxfords', 'mules', 'clogs', 'slippers']):
        category = 'Shoes'
    elif any(word in text_lower for word in ['jacket', 'coat', 'blazer', 'cardigan', 'sweater', 'hoodie', 'vest', 'windbreaker', 'trench', 'parka', 'bomber', 'denim jacket', 'leather jacket']):
        category = 'Outerwear'
    elif any(word in text_lower for word in ['bag', 'handbag', 'backpack', 'purse', 'tote', 'clutch', 'satchel', 'hat', 'cap', 'scarf', 'belt', 'glove', 'accessory', 'jewelry', 'watch', 'sunglasses', 'necklace', 'bracelet', 'earrings', 'ring']):
        category = 'Accessories'
    else:
        category = 'Accessories'
    
    return {
        "item_name": item_name,
        "category": category,
        "color": color,
        "style": style_details
    }

def extract_color(text_lower):
    """Extract color information from analysis text."""
    color_keywords = {
        'black': ['black', 'dark', 'charcoal', 'ebony'],
        'white': ['white', 'cream', 'ivory', 'off-white'],
        'blue': ['blue', 'navy', 'royal blue', 'sky blue', 'light blue', 'dark blue', 'powder blue', 'cobalt'],
        'red': ['red', 'crimson', 'burgundy', 'maroon', 'scarlet', 'cherry'],
        'green': ['green', 'emerald', 'forest green', 'mint', 'olive', 'sage', 'lime'],
        'yellow': ['yellow', 'gold', 'mustard', 'lemon', 'amber'],
        'pink': ['pink', 'rose', 'magenta', 'fuchsia', 'salmon'],
        'purple': ['purple', 'violet', 'lavender', 'plum', 'mauve'],
        'orange': ['orange', 'peach', 'coral', 'tangerine', 'apricot'],
        'brown': ['brown', 'tan', 'beige', 'khaki', 'taupe', 'camel', 'mocha', 'chocolate'],
        'gray': ['gray', 'grey', 'silver', 'slate', 'ash', 'pewter'],
        'denim': ['denim', 'jean', 'indigo']
    }
    
    for color, keywords in color_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return color.capitalize()
    
    return "Unknown"

def extract_material(text_lower):
    """Extract material information from analysis text."""
    material_keywords = {
        'Cotton': ['cotton', 'cotton blend'],
        'Wool': ['wool', 'woolen', 'wool blend'],
        'Silk': ['silk', 'silk blend'],
        'Denim': ['denim', 'jean'],
        'Leather': ['leather', 'leather-like'],
        'Knit': ['knit', 'knitted', 'knitwear'],
        'Linen': ['linen', 'linen blend'],
        'Polyester': ['polyester', 'poly blend'],
        'Cashmere': ['cashmere'],
        'Velvet': ['velvet', 'velvety'],
        'Suede': ['suede', 'sueded'],
        'Chiffon': ['chiffon'],
        'Satin': ['satin', 'satin-like'],
        'Mesh': ['mesh', 'net'],
        'Fleece': ['fleece', 'fleecy']
    }
    
    for material, keywords in material_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return material
    
    return "Unknown"

def extract_style_details(text_lower):
    """Extract specific style details from analysis text."""
    style_keywords = {
        'Striped': ['striped', 'stripes', 'pinstriped'],
        'Polka Dot': ['polka dot', 'dotted', 'spots'],
        'Floral': ['floral', 'flower', 'botanical'],
        'Plaid': ['plaid', 'tartan', 'checkered'],
        'Solid': ['solid', 'plain'],
        'Cropped': ['cropped', 'crop'],
        'Oversized': ['oversized', 'oversize', 'loose'],
        'Fitted': ['fitted', 'tailored', 'slim'],
        'Long Sleeve': ['long sleeve', 'long-sleeve'],
        'Short Sleeve': ['short sleeve', 'short-sleeve'],
        'Sleeveless': ['sleeveless', 'tank'],
        'Button-up': ['button-up', 'button up', 'buttoned'],
        'Hoodie': ['hoodie', 'hooded'],
        'Turtleneck': ['turtleneck', 'mock neck'],
        'V-neck': ['v-neck', 'v neck'],
        'Crew Neck': ['crew neck', 'crew-neck'],
        'High Waist': ['high waist', 'high-waist'],
        'Low Rise': ['low rise', 'low-rise'],
        'Wide Leg': ['wide leg', 'wide-leg'],
        'Skinny': ['skinny', 'slim fit'],
        'Bootcut': ['bootcut', 'boot cut'],
        'Straight': ['straight', 'straight leg'],
        'A-line': ['a-line', 'a line'],
        'Pencil': ['pencil', 'pencil skirt'],
        'Maxi': ['maxi', 'long'],
        'Mini': ['mini', 'short'],
        'Midi': ['midi', 'mid-length']
    }
    
    for style, keywords in style_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return style
    
    return "Unknown"

def extract_item_type(text_lower):
    """Extract specific item type from analysis text."""
    item_keywords = {
        'Shirt': ['shirt', 'button-up', 'button up', 'dress shirt', 'blouse'],
        'T-shirt': ['t-shirt', 'tee', 't shirt'],
        'Sweater': ['sweater', 'pullover', 'jumper'],
        'Hoodie': ['hoodie', 'hooded sweatshirt'],
        'Cardigan': ['cardigan'],
        'Blazer': ['blazer', 'sport coat'],
        'Tank Top': ['tank top', 'tank', 'camisole'],
        'Crop Top': ['crop top', 'crop'],
        'Jeans': ['jeans', 'denim'],
        'Pants': ['pants', 'trousers'],
        'Skirt': ['skirt'],
        'Shorts': ['shorts'],
        'Dress': ['dress'],
        'Jacket': ['jacket', 'coat'],
        'Sneakers': ['sneakers', 'sneaker', 'athletic shoes'],
        'Boots': ['boots', 'boot'],
        'Heels': ['heels', 'high heels', 'pumps'],
        'Flats': ['flats', 'flat shoes'],
        'Sandals': ['sandals', 'sandal'],
        'Bag': ['bag', 'handbag', 'purse', 'tote'],
        'Hat': ['hat', 'cap'],
        'Scarf': ['scarf'],
        'Belt': ['belt']
    }
    
    for item_type, keywords in item_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return item_type
    
    return "Item"

def get_weather_icon(weather_condition):
    """Get appropriate weather icon based on condition"""
    if not weather_condition:
        return "☀️"
    
    weather_lower = weather_condition.lower()
    
    if any(word in weather_lower for word in ['sunny', 'clear', 'sun']):
        return "☀️"
    elif any(word in weather_lower for word in ['cloudy', 'overcast', 'cloud']):
        return "☁️"
    elif any(word in weather_lower for word in ['rainy', 'rain', 'shower']):
        return "🌧️"
    elif any(word in weather_lower for word in ['snowy', 'snow']):
        return "❄️"
    elif any(word in weather_lower for word in ['stormy', 'thunder', 'storm']):
        return "⛈️"
    elif any(word in weather_lower for word in ['foggy', 'fog', 'mist']):
        return "🌫️"
    elif any(word in weather_lower for word in ['windy', 'wind']):
        return "💨"
    else:
        return "🌤️"  # Default to partly cloudy

def get_current_date():
    """Get current date in a user-friendly format"""
    now = datetime.now()
    
    # Format: "Oct 16" (without year)
    return now.strftime("%b %d")

def get_category_name(text_lower):
    """Get a simple category name for the item."""
    if any(word in text_lower for word in ['dress']):
        return "Dress"
    elif any(word in text_lower for word in ['blouse', 'top', 'shirt', 't-shirt', 'sweater', 'hoodie', 'tank', 'crop', 'blazer', 'cardigan', 'pullover', 'polo', 'camisole', 'tunic']):
        return "Top"
    elif any(word in text_lower for word in ['pants', 'skirt', 'jeans', 'shorts', 'trousers', 'leggings', 'capri', 'cargo', 'chinos']):
        return "Bottom"
    elif any(word in text_lower for word in ['shoes', 'sneaker', 'boot', 'sandals', 'loafer', 'heel', 'sneakers', 'boots', 'flats', 'pumps', 'oxfords', 'mules', 'clogs', 'slippers']):
        return "Shoes"
    elif any(word in text_lower for word in ['jacket', 'coat', 'blazer', 'cardigan', 'sweater', 'hoodie', 'vest', 'windbreaker', 'trench', 'parka', 'bomber', 'denim jacket', 'leather jacket']):
        return "Jacket"
    elif any(word in text_lower for word in ['bag', 'handbag', 'backpack', 'purse', 'tote', 'clutch', 'satchel', 'hat', 'cap', 'scarf', 'belt', 'glove', 'accessory', 'jewelry', 'watch', 'sunglasses', 'necklace', 'bracelet', 'earrings', 'ring']):
        return "Accessory"
    else:
        return "Item"

def find_similar_outfit_in_collections(outfit_items, collections):
    """Find similar outfit in collections based on item combinations"""
    if not collections or not outfit_items:
        return None
    
    # Convert outfit items to a set of filenames for comparison
    outfit_filenames = set(outfit_items)
    
    for collection in collections:
        try:
            # Parse collection description to extract outfit information
            description = collection.get('outfit_description', '').lower()
            
            # Simple similarity check based on key clothing terms
            similarity_score = 0
            total_terms = 0
            
            # Check for common clothing categories in description
            clothing_terms = ['top', 'shirt', 'blouse', 'sweater', 'bottom', 'pants', 'skirt', 'jeans', 'dress', 'shoes', 'boots', 'sneakers', 'jacket', 'coat']
            
            for term in clothing_terms:
                if term in description:
                    total_terms += 1
                    # Check if this term matches any of our outfit items
                    for item in outfit_items:
                        if term in item.lower():
                            similarity_score += 1
                            break
            
            # If we have a reasonable similarity (at least 50% of terms match)
            if total_terms > 0 and similarity_score / total_terms >= 0.5:
                return collection
                
        except Exception as e:
            print(f"Error checking collection similarity: {e}")
            continue
    
    return None
from style_agent import select_outfit, load_closet_txts, select_multiple_outfits
from generate_visualisation import generate_image, sanitize_prompt




# Import new services
from database import init_database, create_user, get_user_subscription, save_chat_message, get_chat_messages, save_uploaded_image, get_user_images, save_outfit, get_user_outfits
from weather_service import get_weather_data, get_weather_recommendation, get_weekly_forecast
from chat_service import process_chat_message, get_recommended_outfits_from_closet
from payment_service import create_checkout_session, get_subscription_status

# Occasion types for outfit recommendations
OCCASION_TYPES = [
    'Casual',      # カジュアル - 日常着、リラックスした雰囲気
    'Business',    # ビジネス - オフィス、会議
    'Smart Casual',# スマートカジュアル - きれいめカジュアル
    'Formal',      # フォーマル - 正装、式典
    'Sporty',      # スポーティ - アクティブ、運動
    'Chic',        # シック - 洗練された、エレガント
    'Bohemian',    # ボヘミアン - 自由奔放、民族調
    'Street',      # ストリート - 都会的、トレンド
    'Romantic',    # ロマンティック - 女性らしい、柔らかい
    'Minimalist',  # ミニマリスト - シンプル、洗練
    'Vintage',     # ヴィンテージ - レトロ、クラシック
    'Preppy',      # プレッピー - 清潔感、上品カジュアル
]

# Load environment variables - prioritize .env.local
# Get the directory where this app.py file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(BASE_DIR, '.env.local')
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Load .env.local first if it exists
if os.path.exists(ENV_LOCAL_PATH):
    print(f"Loading environment from: {ENV_LOCAL_PATH}")
    load_dotenv(ENV_LOCAL_PATH, override=True)
else:
    print(f".env.local not found at: {ENV_LOCAL_PATH}")

# Then load .env as fallback
if os.path.exists(ENV_PATH):
    print(f"Loading environment from: {ENV_PATH}")
    load_dotenv(ENV_PATH, override=False)  # Don't override .env.local values

# Debug: Check if Weather API key is loaded
weather_api_key = os.getenv("WEATHER_API_KEY")
if weather_api_key:
    print(f"✓ Weather API Key loaded: {weather_api_key[:10]}...")
else:
    print("✗ Weather API Key NOT loaded!")

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")  # Use a secure key in production
    

    # Initialize database
    init_database()
    
    # Add custom Jinja filters
    import json as json_module
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Parse JSON string to dict"""
        if isinstance(value, str):
            try:
                return json_module.loads(value)
            except:
                return {}
        return value
    
    # Register template functions
    app.jinja_env.globals.update(
        get_weather_icon=get_weather_icon,
        get_current_date=get_current_date
    )
    
    # Google OAuth setup
    google_bp = make_google_blueprint(

        client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID", "your-client-id"),
        client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "your-client-secret"),
        scope=["profile", "email"],

        redirect_to="google_authorized"
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
        return datetime.now(vancouver_tz)
    
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

                "condition": weather_text,
                "temperature": temp_c,
                "text": weather_text,
                "temp_f": temp_f,
                "temp_c": temp_c,
                "icon_url": icon_url
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return {

                "condition": "Sunny",
                "temperature": 22,
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

        # 1. Get today's outfit images (both daily_outfit and bonus_outfit)
        today_files = sorted([
            f for f in os.listdir(output_dir)
            if (("daily_outfit" in f or "bonus_outfit" in f) and today_str in f and f.endswith(".png"))
        ])

        # 2. If none, get up to 4 most recent .png images from output/
        if not today_files:
            all_pngs = [f for f in os.listdir(output_dir) if f.endswith(".png")]
            all_pngs = sorted(all_pngs, key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
            today_files = all_pngs[:4]



        # Get weather information
        weather_info = get_weather_data()
        weather_condition = weather_info.get('condition', 'Sunny') if weather_info else 'Sunny'
        weather_temp = weather_info.get('temperature', 22) if weather_info else 22

        # Select diverse occasions for variety
        import random
        selected_occasions = random.sample(OCCASION_TYPES, min(4, len(OCCASION_TYPES)))

        outfits = []
        if today_files:
            for idx, filename in enumerate(today_files[:4]):

                occasion = selected_occasions[idx] if idx < len(selected_occasions) else 'Casual'
                outfits.append({
                    'name': f'Outfit {idx+1}',
                    'image': f'/output/{filename}',

                    'weather': weather_condition,
                    'temperature': weather_temp,
                    'occasion': occasion,
                    'files': []
                })
        else:
            outfits.append({
                'name': 'No Outfit',
                'image': '/static/images/avatar-placeholder.svg',

                'weather': weather_condition,
                'temperature': weather_temp,
                'occasion': 'Casual',
                'files': []
            })
        return outfits
    

    def generate_single_outfit(weather=None, outfit_type="manual"):
        """Generate a single outfit recommendation"""
        vancouver_time = get_vancouver_time()
        timestamp = vancouver_time.strftime("%Y%m%d_%H%M%S")
        output_dir = app.config['OUTPUT_FOLDER']
        closet_dir = app.config['UPLOAD_FOLDER']
        avatar_path = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
                    

        # Check if there are any clothes in the closet
        closet_files = [f for f in os.listdir(closet_dir) if f.endswith(('.txt', '.jpg', '.jpeg', '.png'))]
        if len(closet_files) < 2:  # Need at least avatar.txt and one clothing item
            print("Not enough items in closet to generate outfit")
            return None
                    
        # Select one outfit based on weather
        criteria = {'weather': weather} if weather else None

        try:
            outfit_files_list = select_multiple_outfits(num=1, closet_dir=closet_dir, criteria=criteria)

            if not outfit_files_list or len(outfit_files_list) == 0:
                print("No outfits selected")
                return None
                
            files = outfit_files_list[0]
            outfit_key = get_outfit_key(files)
        except Exception as e:
            print(f"Error selecting outfits: {e}")
            return None

        outfit_filename = f"{outfit_type}_outfit_{timestamp}_{outfit_key[:8]}.png"
        outfit_output_path = os.path.join(output_dir, outfit_filename)
        

        # Check if we can reuse an existing outfit image with same combination
        existing_outfits = {}
        for f in os.listdir(output_dir):

            if f.endswith(".png") and "_outfit_" in f:
                # Extract the outfit key from filename
                parts = f.split("_")
                if len(parts) >= 4:
                    key = parts[-1].replace(".png", "")
                existing_outfits[key] = f
        

        # Reuse existing image if same outfit combination exists
        if outfit_key[:8] in existing_outfits:
            existing_path = os.path.join(output_dir, existing_outfits[outfit_key[:8]])
            import shutil

            shutil.copy2(existing_path, outfit_output_path)
            print(f"Reusing existing outfit image: {existing_outfits[outfit_key[:8]]}")
            weather_display = weather.title() if weather else (get_weather_data().get('condition', 'Sunny') if get_weather_data() else 'Sunny')
            import random
            occasion = random.choice(OCCASION_TYPES)
            return {

                'name': f'{outfit_type.title()} Outfit',
                'image': f'/output/{outfit_filename}',
                'weather': weather_display,
                'temperature': get_weather_data().get('temperature', 22) if get_weather_data() else 22,
                'occasion': occasion,
                'files': files
            }
        

        # Generate new outfit image
        try:
            # Get OpenAI API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your-openai-key":
                print("Warning: OpenAI API key not set, cannot generate outfit image")
                return None
            
            # Read clothing description files
            clothing_paths = []
            for f in files:
                # For image files, look for corresponding .txt file
                base_name = os.path.splitext(f)[0]
                txt_file = f"{base_name}.txt"
                txt_path = os.path.join(closet_dir, txt_file)
                
                if os.path.exists(txt_path):
                    clothing_paths.append(txt_path)
                elif f.endswith('.txt'):
                    clothing_paths.append(os.path.join(closet_dir, f))
            
            if not clothing_paths:
                print("No clothing descriptions found")
                return None
            
            # Combine avatar and clothing descriptions
            texts = []

            if os.path.exists(avatar_path):
                with open(avatar_path, 'r', encoding='utf-8') as f:
                    texts.append(f.read().strip())
            
            for path in clothing_paths:
                with open(path, 'r', encoding='utf-8') as f:
                    texts.append(f.read().strip())

            
            raw_prompt = "\n".join(texts)
            prompt = sanitize_prompt(raw_prompt)

            
            print(f"Generating outfit image with prompt length: {len(prompt)}")
            image_bytes = generate_image(prompt, api_key)

            
            with open(outfit_output_path, "wb") as f:
                f.write(image_bytes)

            
            print(f"Successfully generated outfit: {outfit_filename}")
            weather_display = weather.title() if weather else (get_weather_data().get('condition', 'Sunny') if get_weather_data() else 'Sunny')
            import random
            occasion = random.choice(OCCASION_TYPES)
            
            return {

                'name': f'{outfit_type.title()} Outfit',
                'image': f'/output/{outfit_filename}',
                'weather': weather_display,
                'temperature': get_weather_data().get('temperature', 22) if get_weather_data() else 22,
                'occasion': occasion,
                'files': files
            }
        except Exception as e:

            print(f"Failed to generate outfit: {e}")
            import traceback
            traceback.print_exc()
            return None
    

    def generate_daily_outfits_task():
        """Generate 4 daily outfit recommendations based on current weather"""
        print("=" * 50)
        print("Starting daily outfit generation task...")
        print("=" * 50)
        
        vancouver_time = get_vancouver_time()
        today_str = vancouver_time.strftime("%Y%m%d")
        output_dir = app.config['OUTPUT_FOLDER']
        
        # Check if already generated today
        today_files = [
            f for f in os.listdir(output_dir)
            if f.startswith(f"daily_outfit_{today_str}_") and f.endswith(".png")
        ]
        
        if len(today_files) >= 4:
            print(f"Daily outfits already generated today ({len(today_files)} found)")
            return
        
        # Get current weather
        weather_data = get_weather_data('Vancouver')
        weather_condition = weather_data.get('condition', 'Sunny').lower() if weather_data else 'sunny'
        weather_temp = weather_data.get('temperature', 22) if weather_data else 22
        
        print(f"Weather: {weather_condition}, {weather_temp}°C")
        
        # Generate 4 outfits
        generated_count = 0
        for i in range(4):
            print(f"\nGenerating outfit {i+1}/4...")
            outfit = generate_single_outfit(weather=weather_condition, outfit_type=f"daily_{today_str}")
            
            if outfit:
                generated_count += 1
                print(f"✓ Outfit {i+1} generated successfully")
            else:
                print(f"✗ Failed to generate outfit {i+1}")
        
        print("\n" + "=" * 50)
        print(f"Daily outfit generation complete: {generated_count}/4 outfits generated")
        print("=" * 50)
        
        return generated_count
    
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

        weather_info = get_weather_data('Vancouver')
        
        # Get closet items from database
        # For now, use a dummy user_id=1 (will be replaced with actual user authentication)
        user_id = session.get('user_id', 1)
        
        # Try to get user images from database
        try:
            from database import get_user_images
            closet_items = get_user_images(user_id)
        except Exception as e:
            print(f"Error loading closet items: {e}")
            closet_items = []
        
        return render_template('home.html', outfits=outfits, weather_info=weather_info, closet_items=closet_items)
    
    @app.route('/landing')
    def landing():
        """Landing page"""
        return render_template('landing.html')
    
    @app.route('/api/weather')
    def api_weather():
        """Get weather data API"""
        location = request.args.get('location', 'Vancouver')
        weather_data = get_weather_data(location)
        return jsonify(weather_data)
    
    @app.route('/api/weather/forecast')
    def api_weather_forecast():
        """Get 7-day weather forecast API"""
        location = request.args.get('location', 'Vancouver')
        forecast_data = get_weekly_forecast(location)
        return jsonify({
            'success': True,
            'forecast': forecast_data
        })
    
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        """Chat API endpoint"""
        try:
            data = request.get_json()
            message = data.get('message', '')
            image_data = data.get('image_base64')
            weather = data.get('weather')
            occasion = data.get('occasion')
            
            # Get user ID from session
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'User not authenticated'}), 401
            
            # Process chat message
            ai_response = process_chat_message(user_id, message, image_data, weather, occasion)
            
            return jsonify({
                'success': True,
                'reply': ai_response
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/outfits')
    def api_outfits():
        """Get outfit recommendations API"""
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'User not authenticated'}), 401
            
            weather = request.args.get('weather', 'moderate')
            occasion = request.args.get('occasion', 'casual')
            
            # Get outfit recommendations
            outfits = get_recommended_outfits_from_closet(user_id, weather, occasion)
            
            return jsonify({
                'success': True,
                'outfits': outfits
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/subscription/status')
    def api_subscription_status():
        """Get subscription status API"""
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'User not authenticated'}), 401
            
            status = get_subscription_status(user_id)
            return jsonify(status)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/payment/checkout', methods=['POST'])
    def api_payment_checkout():
        """Create payment checkout session"""
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'User not authenticated'}), 401
            
            session_obj = create_checkout_session(user_id)
            if session_obj:
                return jsonify({
                    'success': True,
                    'url': session_obj.url
                })
            else:
                return jsonify({'error': 'Failed to create checkout session'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/payment/success')
    def payment_success():
        """Payment success page"""
        return render_template('payment_success.html')
    
    @app.route('/payment/cancel')
    def payment_cancel():
        """Payment cancel page"""
        return render_template('payment_cancel.html')
    
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
        """Get closet contents with category info from database"""
        try:
            user_id = session.get('user_id', 1)
            items = get_user_images(user_id)
            
            # Convert database items to the format expected by frontend
            formatted_items = []
            for item in items:
                try:
                    analysis = json.loads(item.get('analysis', '{}'))
                    formatted_items.append({
                        'id': item.get('id'),
                        'filename': item.get('filename'),
                        'original_name': item.get('original_name'),
                        'image_url': item.get('url'),
                        'analysis': item.get('analysis'),
                        'name': analysis.get('item_name', item.get('original_name', 'Clothing Item')),
                        'category': analysis.get('category', 'Clothing'),
                        'description': analysis.get('description', 'Clothing item')
                    })
                except Exception as e:
                    # Fallback for items without proper analysis
                    formatted_items.append({
                        'id': item.get('id'),
                        'filename': item.get('filename'),
                        'original_name': item.get('original_name'),
                        'image_url': item.get('url'),
                        'analysis': item.get('analysis'),
                        'name': item.get('original_name', 'Clothing Item'),
                        'category': 'Clothing',
                        'description': 'Clothing item'
                    })
            
            return jsonify({
                'success': True,
                'items': formatted_items
            })
        except Exception as e:
            return jsonify({'error': f'Failed to load closet: {str(e)}'}), 500
    
    
    @app.route('/output/<filename>')
    def serve_output(filename):
        """Serve generated images"""
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    

    @app.route('/data/clothes/input/<path:filename>')
    def serve_uploaded_clothes(filename):
        """Serve uploaded clothing images"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
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

        weather_info = get_weather_data('Vancouver')
        outfits = generate_daily_outfits(weather=weather_info.get("condition", "Sunny").lower())
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

        """Force generate daily outfits (admin function) - triggers the 5AM task manually"""
        try:

            generated_count = generate_daily_outfits_task()
            outfits = generate_daily_outfits()
            return jsonify({
                'success': True,

                'generated_count': generated_count if generated_count else 0,
                'outfits': outfits,

                'message': f'Daily outfits generated: {generated_count if generated_count else 0}/4 successful'
            })
        except Exception as e:

            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Force generation failed: {str(e)}'}), 500
    
    @app.route('/chat', methods=['POST'])
    def chat():
        """Q&A chat endpoint: receives a user message or image and returns an AI reply or outfit recommendation."""
        try:
            data = request.get_json()
            user_message = data.get('message', '').strip() if data.get('message') else ''
            image_base64 = data.get('image_base64', None)

            if image_base64:


                # If an image is sent, analyze and automatically add to closet
                import base64, tempfile, time
                from generate_item import analyze_image
                from style_agent import select_outfit, load_closet_txts


                from PIL import Image
                import io

                try:
                    # Decode base64 image
                    image_data = base64.b64decode(image_base64.split(',')[-1])
                    
                    # Generate unique filename
                    timestamp = int(time.time())
                    unique_filename = f"{timestamp}_chat_upload.jpg"
                    
                    # Process image with PIL
                    img = Image.open(io.BytesIO(image_data))
                    
                    # Handle EXIF orientation
                    try:
                        from PIL import ImageOps
                        img = ImageOps.exif_transpose(img)
                    except:
                        pass
                    
                    # Convert to RGB
                    if img.mode == 'RGBA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    elif img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    
                    # Resize if too large
                    max_size = 2000
                    if max(img.size) > max_size:
                        ratio = max_size / max(img.size)
                        new_size = tuple(int(dim * ratio) for dim in img.size)
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Save to closet folder
                    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    img.save(upload_path, 'JPEG', quality=90, optimize=True)
                    
                    # Create URL for accessing the image
                    image_url = f"/data/clothes/input/{unique_filename}"
                except Exception as e:
                    print(f"Image processing failed: {e}")
                    return jsonify({'error': 'Image processing failed'}), 500

                # Analyze the clothing item
                api_key = os.getenv("OPENAI_API_KEY")
                clothing_info = {}
                
                try:
                    analysis_text = analyze_image(upload_path)
                    print(f"Chat upload analysis result: {analysis_text}")
                    
                    # Extract item info from analysis text
                    item_info = extract_item_info(analysis_text)
                    
                    clothing_info = {
                        "item_name": item_info.get("item_name", "Chat Upload"),
                        "category": item_info.get("category", "Clothing"),
                        "color": item_info.get("color", "Unknown"),
                        "style": item_info.get("style", "Unknown"),
                        "description": analysis_text,
                        "image_url": image_url
                    }
                    
                    # Save analysis text to file
                    txt_filename = unique_filename.replace('.jpg', '.txt')
                    txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(analysis_text)
                    print(f"✅ Analysis text saved to: {txt_filename}")
                    
                except Exception as e:
                    print(f"Analysis failed: {e}")
                    clothing_info = {
                        "item_name": "Chat Upload",
                        "category": "Clothing",
                        "description": "Item uploaded from chat",
                        "image_url": image_url
                    }
                    
                    # Save to database
                    user_id = session.get("user_id", 1)
                    import json
                    save_uploaded_image(
                        user_id=user_id,
                        filename=unique_filename,
                        original_name="chat_upload.jpg",
                        url=image_url,
                        analysis=json.dumps(clothing_info)
                    )
                    
                    print(f"✅ Image saved to closet: {unique_filename}")
                    
                    # Use the analysis result as context for AI chat advice
                    # This allows us to use text-to-text model (gpt-3.5-turbo) instead of vision model
                    
                    # Get analysis description for chat context
                    analysis_description = clothing_info.get('description', f"A {clothing_info.get('category', 'clothing')} item in {clothing_info.get('color', 'unknown')} color")
                    
                    # Build context about user's closet
                    user_id = session.get("user_id", 1)
                    closet_items_data = get_user_images(user_id)
                    closet_context = ""
                    if closet_items_data and len(closet_items_data) > 1:  # More than just the uploaded item
                        closet_context = "\n\nUser's existing closet items:\n"
                        for item in closet_items_data[-10:]:  # Last 10 items
                            if item.get('analysis'):
                                import json
                                analysis = json.loads(item['analysis'])
                                closet_context += f"- {analysis.get('item_name', 'Item')}: {analysis.get('description', '')}\n"
                    
                    # Get weather context
                    weather_data = get_weather_data('Vancouver')
                    weather_context = ""
                    if weather_data:
                        weather_context = f"\n\nCurrent weather: {weather_data.get('temperature', 22)}°C, {weather_data.get('condition', 'Sunny')}"
                    
                    # Use gpt-3.5-turbo to generate styling advice based on the analyzed image
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key and api_key != "your-openai-key":
                        try:
                            from openai import OpenAI
                            client = OpenAI(api_key=api_key)
                            
                            styling_prompt = f"""You are AIstylist, a personal fashion consultant. A user just uploaded this item to their closet:

{analysis_description}

Item details:
- Name: {clothing_info.get('item_name', 'Clothing item')}
- Category: {clothing_info.get('category', 'Clothing')}
- Color: {clothing_info.get('color', 'Unknown')}
{closet_context}{weather_context}

Task:
1. Welcome the item to their closet
2. Give honest styling advice - what this item pairs well with
3. If they have existing items, suggest 2-3 specific outfit combinations
4. Consider current weather if relevant
5. Be encouraging but honest

Keep response to 3-4 sentences, friendly and actionable."""

                            response = client.chat.completions.create(
                                model='gpt-3.5-turbo',
                                messages=[
                                    {"role": "system", "content": "You are AIstylist, an honest and kind fashion consultant."},
                                    {"role": "user", "content": styling_prompt}
                                ],
                                temperature=0.7,
                                max_tokens=250
                            )
                            reply = response.choices[0].message.content
                            
                        except Exception as chat_error:
                            print(f"Chat API error: {chat_error}")
                            # Fallback to simple message
                            item_name = clothing_info.get('item_name', 'this item')
                            reply = f"Great! I've added '{item_name}' to your closet. This {clothing_info.get('category', 'item')} will be a nice addition to your wardrobe!"
                    else:
                        # No API key - simple confirmation
                        item_name = clothing_info.get('item_name', 'this item')
                        reply = f"Great! I've added '{item_name}' to your closet. Upload more items to build your wardrobe!"

                    return jsonify({
                        'reply': reply,
                        'item_added': True,
                        'item_info': clothing_info
                    })
                    
                except Exception as e:
                    print(f"Error processing chat image: {e}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({'error': f'Failed to process image: {str(e)}'}), 500

            elif user_message:
                # If only text, use OpenAI chat for fashion advice
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key or api_key == "your-openai-key":
                    return jsonify({'error': 'OpenAI API key not set.'}), 500


                try:
                    # Get user's closet context for personalized advice
                    user_id = session.get("user_id", 1)
                    closet_items = get_user_images(user_id)
                    
                    # Build closet context
                    closet_context = ""
                    if closet_items and len(closet_items) > 0:
                        closet_context = f"\n\nThe user has {len(closet_items)} items in their closet: "
                        item_descriptions = []
                        for item in closet_items[:10]:  # Limit to 10 items to avoid token limit
                            if item.get('analysis'):
                                import json
                                analysis = json.loads(item['analysis'])
                                item_desc = f"{analysis.get('item_name', 'Item')} ({analysis.get('category', 'Clothing')})"
                                item_descriptions.append(item_desc)
                        closet_context += ", ".join(item_descriptions)
                    
                    # Get current weather for context
                    weather_data = get_weather_data('Vancouver')
                    weather_context = ""
                    if weather_data:
                        weather_context = f"\n\nCurrent weather in Vancouver: {weather_data.get('temperature', 22)}°C, {weather_data.get('condition', 'Sunny')}"
                    
                    # Enhanced system prompt
                    system_prompt = f"""You are AIstylist, a personalized AI fashion consultant with access to the user's virtual closet.

Your role:
- Provide HONEST, expert fashion advice tailored to the user's existing wardrobe
- Give truthful opinions about outfit combinations - if something doesn't work well, explain why gently and suggest alternatives
- Consider current weather conditions for practical recommendations
- Offer constructive style tips for various occasions (Casual, Business, Chic, Formal, etc.)
- Help users maximize their existing wardrobe while maintaining authenticity

Important principles:
- Be HONEST but KIND: If a combination doesn't work well, say so politely and explain why (e.g., "The colors might clash, but you could try..." or "While this is a bold mix, I'd suggest...")
- Offer ALTERNATIVES: When giving constructive feedback, always suggest 2-3 better options from their closet
- Be ENCOURAGING: Frame feedback positively - focus on what WILL work rather than dwelling on what won't
- Be SPECIFIC: Explain your reasoning with fashion principles (color theory, proportions, occasion appropriateness)
- Respect PERSONAL STYLE: If something is unconventional but could work with confidence, acknowledge that

Key features you can reference:
- The user's closet items and their details
- Current weather conditions
- Occasion-based styling (Casual, Business, Smart Casual, Formal, Sporty, Chic, etc.)
{closet_context}{weather_context}

Response style:
- Be friendly and supportive, never condescending
- Keep answers concise (2-4 sentences for simple questions)
- Use phrases like: "I'd suggest...", "A better option might be...", "Consider trying...", "This would work better because..."
- Avoid: fake compliments, saying everything looks great, or being overly critical

Remember: Your goal is to help users look their best while building their confidence and fashion knowledge."""

                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    
                    response = client.chat.completions.create(
                        model='gpt-3.5-turbo',
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        temperature=0.7,
                        max_tokens=300
                    )
                    reply = response.choices[0].message.content
                    
                except Exception as e:
                    print(f"Chat API error: {e}")
                    reply = "Sorry, I'm having trouble connecting right now. Please try again in a moment!"
                    
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


            
            # Create or get user from database
            user_id = create_user(
                email=user_info.get("email"),
                name=user_info.get("name"),
                picture=user_info.get("picture"),
                google_id=user_info.get("id")
            )
            
            # Store user info in session
            session["user"] = {

                "id": user_id,
                "name": user_info.get("name"),
                "email": user_info.get("email"),
                "picture": user_info.get("picture"),
                "initial": user_info.get("name", "?")[0].upper()
            }

            session["user_id"] = user_id
            
            return redirect(url_for("landing"))
        return "Failed to login", 401

    @app.route("/logout")
    def logout():
        session.pop("user", None)
        return redirect(url_for("index"))



    @app.route("/api/analyze-clothing", methods=["POST"])
    def analyze_clothing():
        """Analyze uploaded clothing image and return text description"""
        try:
            data = request.get_json()
            image_base64 = data.get('image')
            filename = data.get('filename', 'unknown')
            
            if not image_base64:
                return jsonify({"success": False, "error": "No image provided"}), 400
            
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            
            # Generate unique filename with timestamp
            import time
            from PIL import Image
            import io
            
            # Register HEIF opener for iPhone images
            try:
                from pillow_heif import register_heif_opener
                register_heif_opener()
                print("HEIF/HEIC support enabled")
            except ImportError:
                print("Warning: pillow-heif not installed, HEIC files from iPhone may not work")
            
            timestamp = int(time.time())
            
            # Process image with PIL to handle mobile formats and orientation
            try:
                # Load image from bytes
                img = Image.open(io.BytesIO(image_data))
                print(f"Image loaded: format={img.format}, mode={img.mode}, size={img.size}")
                
                # Handle EXIF orientation (common issue with iPhone/Android photos)
                try:
                    from PIL import ImageOps
                    img = ImageOps.exif_transpose(img)
                except Exception as e:
                    print(f"Could not process EXIF orientation: {e}")
                
                # Convert RGBA to RGB if necessary (for PNG with transparency)
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Resize if image is too large (max 2000px on longest side)
                max_size = 2000
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"Resized image from {image_data.__sizeof__()} to smaller size")
                
                # Save as JPEG (universal format)
                safe_filename = secure_filename(filename)
                # Replace extension with .jpg
                name_parts = safe_filename.rsplit('.', 1)
                if len(name_parts) > 1:
                    safe_filename = f"{name_parts[0]}.jpg"
                else:
                    safe_filename = f"{safe_filename}.jpg"
                
                unique_filename = f"{timestamp}_{safe_filename}"
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Save as JPEG with good quality
                img.save(upload_path, 'JPEG', quality=90, optimize=True)
                print(f"Successfully saved image: {unique_filename}")
                
            except Exception as img_error:
                print(f"Image processing error: {img_error}, saving raw data")
                # Fallback: save raw data if PIL processing fails
                unique_filename = f"{timestamp}_{secure_filename(filename)}"
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                with open(upload_path, 'wb') as f:
                    f.write(image_data)
            
            # Create URL path for accessing the image
            image_url = f"/data/clothes/input/{unique_filename}"
            
            # Duplicate detection: compare hash with existing files
            try:
                new_hash = get_image_hash(upload_path)
                closet_dir = app.config['UPLOAD_FOLDER']
                import json
                from database import get_user_images
                user_id = session.get("user_id", 1)
                existing = get_user_images(user_id) or []
                for item in existing:
                    try:
                        # Compare against file content in closet
                        existing_path = os.path.join(closet_dir, item.get('filename', ''))
                        if os.path.exists(existing_path):
                            if get_image_hash(existing_path) == new_hash:
                                # Duplicate found: remove newly saved file and return duplicate flag
                                try:
                                    os.remove(upload_path)
                                except Exception:
                                    pass
                                existing_analysis = {}
                                if item.get('analysis'):
                                    try:
                                        existing_analysis = json.loads(item['analysis'])
                                    except Exception:
                                        existing_analysis = {}
                                return jsonify({
                                    "success": True,
                                    "duplicate": True,
                                    "analysis": existing_analysis,
                                    "existing_filename": item.get('filename')
                                })
                    except Exception:
                        continue
            except Exception as dup_err:
                print(f"Duplicate check error: {dup_err}")
            
            try:
                # Try to analyze the image using existing analyze_image function
                try:
                    analysis_result = analyze_image(upload_path)
                    
                    # Extract clothing information using improved function
                    if isinstance(analysis_result, str):
                        item_info = extract_item_info(analysis_result)
                        clothing_info = {
                            "item_name": item_info.get("item_name", filename.split('.')[0]),
                            "category": item_info.get("category", "Clothing"),
                            "color": item_info.get("color", "Unknown"),
                            "style": item_info.get("style", "Unknown"),
                            "description": analysis_result,
                            "image_url": image_url
                        }
                    else:
                        clothing_info = {
                        "item_name": analysis_result.get("item_name", filename.split('.')[0]),
                        "category": analysis_result.get("category", "Clothing"),
                        "color": analysis_result.get("color", "Unknown"),
                        "style": analysis_result.get("style", "Unknown"),
                        "description": analysis_result.get("description", "Clothing item"),
                        "image_url": image_url
                    }
                    
                    # Save analysis text to file
                    txt_filename = unique_filename.replace('.jpg', '.txt').replace('.jpeg', '.txt').replace('.png', '.txt')
                    txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(analysis_result)
                    
                    # Save to database if user is logged in
                    user_id = session.get("user_id", 1)  # Default to user_id=1 for now
                    import json
                    save_uploaded_image(
                        user_id=user_id,
                        filename=unique_filename,
                        original_name=filename,
                        url=image_url,
                        analysis=json.dumps(clothing_info)
                    )
                    
                    return jsonify({
                        "success": True,
                        "analysis": clothing_info
                    })
                    
                except Exception as api_error:
                    print(f"API analysis failed: {str(api_error)}")
                    # Return fallback analysis even if API fails
                    clothing_info = {
                        "item_name": filename.split('.')[0],
                        "category": "Clothing",
                        "color": "Unknown",
                        "style": "Unknown",
                        "description": "Clothing item (analysis pending)",
                        "image_url": image_url,
                        "pending_analysis": True
                    }
                    
                    # Still save to database with fallback info
                    user_id = session.get("user_id", 1)
                    import json
                    save_uploaded_image(
                        user_id=user_id,
                        filename=unique_filename,
                        original_name=filename,
                        url=image_url,
                        analysis=json.dumps(clothing_info)
                    )
                    
                    return jsonify({
                        "success": False,
                        "analysis": clothing_info,
                        "error": "API analysis failed, item saved for later analysis"
                    })
                
            except Exception as save_error:
                print(f"Error saving image: {str(save_error)}")
                # If database save fails, at least return the analysis
                clothing_info = {
                    "item_name": filename.split('.')[0],
                    "category": "Clothing",
                    "image_url": image_url,
                    "pending_analysis": True
                }
                return jsonify({
                    "success": False,
                    "analysis": clothing_info,
                    "error": "Failed to save to database"
                })
                    
        except Exception as e:
            print(f"Error processing clothing: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Failed to process image"
            }), 500

    @app.route("/api/delete-clothing", methods=["POST"])
    def delete_clothing():
        """Delete clothing item from database and filesystem"""
        try:
            data = request.get_json()
            filename = data.get('filename')
            
            if not filename:
                return jsonify({"success": False, "error": "No filename provided"}), 400
            
            # Delete from database if user is logged in
            user_id = session.get("user_id", 1)  # Default to user_id=1 for now
            
            # Import the delete function
            from database import delete_uploaded_image
            
            success = delete_uploaded_image(user_id, filename)
            
            if success:
                print(f"Successfully deleted clothing item: {filename} for user: {user_id}")
                return jsonify({
                    "success": True,
                    "message": "Item deleted successfully"
                })
            else:
                print(f"Failed to delete clothing item: {filename} for user: {user_id}")
                return jsonify({
                    "success": False,
                    "error": "Item not found or already deleted"
                }), 404
            
        except Exception as e:
            print(f"Error deleting clothing: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Failed to delete item"
            }), 500

    @app.route("/api/collections")
    def get_collections():
        """Get user's collections"""
        try:
            user_id = session.get("user_id", 1)
            from database import get_user_collections
            
            collections = get_user_collections(user_id)
            return jsonify({
                "success": True,
                "collections": collections
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to load collections: {str(e)}"
            }), 500

    @app.route('/api/save-outfit', methods=['POST'])
    def save_outfit():
        """Save current outfit to collections"""
        try:
            data = request.get_json()
            user_id = session.get('user_id', 1)
            
            # Get current outfit data
            outfit_name = data.get('name', f"Saved Outfit {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            outfit_image_url = data.get('image_url')
            weather_condition = data.get('weather', 'moderate')
            occasion = data.get('occasion', 'casual')
            
            if not outfit_image_url:
                return jsonify({'error': 'No outfit image provided'}), 400
            
            # Save to collections
            from database import save_collection
            collection_id = save_collection(
                user_id=user_id,
                collection_name=outfit_name,
                collection_type="manual_save",
                avatar_image_url=outfit_image_url,
                outfit_description=f"Manually saved outfit for {weather_condition} weather",
                tags=f"manual,{weather_condition},{occasion}"
            )
            
            return jsonify({
                'success': True,
                'message': 'Outfit saved successfully',
                'collection_id': collection_id
            })
        except Exception as e:
            return jsonify({'error': f'Failed to save outfit: {str(e)}'}), 500

    @app.route("/api/save-collection", methods=["POST"])
    def save_collection():
        """Save a new collection item"""
        try:
            data = request.get_json()
            collection_name = data.get('collection_name')
            collection_type = data.get('collection_type')
            avatar_image_url = data.get('avatar_image_url')
            outfit_description = data.get('outfit_description')
            tags = data.get('tags', '')
            
            if not all([collection_name, collection_type, avatar_image_url, outfit_description]):
                return jsonify({
                    "success": False,
                    "error": "Missing required fields"
                }), 400
            
            user_id = session.get("user_id", 1)
            from database import save_collection
            
            collection_id = save_collection(
                user_id, collection_name, collection_type, 
                avatar_image_url, outfit_description, tags
            )
            
            return jsonify({
                "success": True,
                "collection_id": collection_id,
                "message": "Collection saved successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to save collection: {str(e)}"
            }), 500

    @app.route("/api/delete-collection", methods=["POST"])
    def delete_collection():
        """Delete a collection item"""
        try:
            data = request.get_json()
            collection_id = data.get('collection_id')
            
            if not collection_id:
                return jsonify({
                    "success": False,
                    "error": "No collection ID provided"
                }), 400
            
            user_id = session.get("user_id", 1)
            from database import delete_collection
            
            success = delete_collection(user_id, collection_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Collection deleted successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Collection not found or already deleted"
                }), 404
                
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to delete collection: {str(e)}"
            }), 500

    @app.route("/api/reuse-outfit", methods=["POST"])
    def reuse_outfit():
        """Reuse outfit from collection with duplicate detection"""
        try:
            data = request.get_json()
            collection_id = data.get('collection_id')
            collection_name = data.get('collection_name')
            collection_type = data.get('collection_type')
            outfit_description = data.get('outfit_description')
            tags = data.get('tags', '')
            
            if not all([collection_id, collection_name, outfit_description]):
                return jsonify({
                    "success": False,
                    "error": "Missing required fields"
                }), 400
            
            user_id = session.get("user_id", 1)
            
            # Check for duplicate outfits based on description similarity
            from database import get_user_outfits
            existing_outfits = get_user_outfits(user_id, limit=100)
            
            # Simple duplicate detection based on outfit description similarity
            for outfit in existing_outfits:
                try:
                    outfit_data = json.loads(outfit.get('outfit_data', '{}'))
                    existing_description = outfit_data.get('description', '')
                    
                    # Check if descriptions are similar (simple similarity check)
                    if existing_description and outfit_description:
                        # Convert to lowercase and remove common words for comparison
                        def normalize_text(text):
                            common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
                            words = text.lower().split()
                            return ' '.join([w for w in words if w not in common_words])
                        
                        normalized_existing = normalize_text(existing_description)
                        normalized_new = normalize_text(outfit_description)
                        
                        # Simple similarity check (if 80% of words match, consider it duplicate)
                        existing_words = set(normalized_existing.split())
                        new_words = set(normalized_new.split())
                        
                        if existing_words and new_words:
                            intersection = existing_words.intersection(new_words)
                            union = existing_words.union(new_words)
                            similarity = len(intersection) / len(union) if union else 0
                            
                            if similarity > 0.8:  # 80% similarity threshold
                                return jsonify({
                                    "success": True,
                                    "duplicate": True,
                                    "message": "Similar outfit already exists"
                                })
                except Exception:
                    continue
            
            # No duplicate found, create new outfit
            from database import save_outfit
            import json
            
            outfit_data = {
                "name": collection_name,
                "type": collection_type,
                "description": outfit_description,
                "tags": tags,
                "source": "collection_reuse",
                "collection_id": collection_id
            }
            
            outfit_id = save_outfit(
                user_id=user_id,
                outfit_name=collection_name,
                outfit_data=json.dumps(outfit_data),
                weather_condition="Reused from collection",
                occasion=collection_type
            )
            
            return jsonify({
                "success": True,
                "duplicate": False,
                "outfit_id": outfit_id,
                "message": "Outfit reused successfully"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to reuse outfit: {str(e)}"
            }), 500

    @app.route("/api/generate-manual-outfit", methods=["POST"])
    def generate_manual_outfit():
        """Generate a manual outfit (1 per day) with automatic collection reuse"""
        try:
            user_id = session.get("user_id", 1)
            
            # Check if user already generated today
            from database import get_user_outfits
            today = datetime.now().strftime("%Y-%m-%d")
            today_outfits = get_user_outfits(user_id, limit=10)
            
            for outfit in today_outfits:
                if outfit.get('created_at', '').startswith(today):
                    return jsonify({
                        "success": False,
                        "error": "You have already generated your bonus outfit today. Come back tomorrow!"
                    }), 403
            
            # Check collections for similar outfits first
            from database import get_user_collections
            collections = get_user_collections(user_id)
            
            # Check if we can reuse an existing saved outfit first
            existing_collections = collections
            
            # Look for similar weather/occasion outfits
            weather_condition = weather_info.condition if weather_info else 'moderate'
            similar_outfits = [
                col for col in existing_collections 
                if col.get('collection_type') == 'daily_outfit' and 
                weather_condition.lower() in col.get('tags', '').lower()
            ]
            
            if similar_outfits:
                # Reuse existing outfit
                reused_outfit = similar_outfits[0]
                print(f"Reusing existing outfit: {reused_outfit['collection_name']}")
                return jsonify({
                    "success": True,
                    "message": "Outfit generated successfully (reused from saved collection)",
                    "avatar_image_url": reused_outfit['avatar_image_url'],
                    "reused": True
                })
        except Exception as e:
            print(f"Error checking existing collections: {e}")
        
        # If no suitable existing outfit found, generate new one
        try:
            from ai_style_agent import select_multiple_outfits_ai, fallback_to_original_selection
            api_key = os.getenv("OPENAI_API_KEY")
            outfits = select_multiple_outfits_ai(num=1, closet_dir=app.config['UPLOAD_FOLDER'], weather=weather_info.condition if weather_info else None, api_key=api_key)
            
            # If AI selection fails, use fallback
            if not outfits:
                print("AI selection failed, using fallback method")
                outfits = fallback_to_original_selection(num=1, closet_dir=app.config['UPLOAD_FOLDER'], weather=weather_info.condition if weather_info else None)
        except Exception as e:
            print(f"AI outfit selection error: {e}, using fallback method")
            from style_agent import select_multiple_outfits
            outfits = select_multiple_outfits(num=1, closet_dir=app.config['UPLOAD_FOLDER'])
            
            if not outfits:
                return jsonify({
                    "success": False,
                    "error": "No suitable outfit combinations found. Add more items to your closet!"
                }), 400
            
            # Check if similar outfit exists in collections
            similar_collection = find_similar_outfit_in_collections(outfits[0], collections)
            
            if similar_collection:
                # Reuse existing collection outfit
                from database import save_outfit
                import json
                
                outfit_data = {
                    "outfit_items": outfits[0],
                    "generated_at": datetime.now().isoformat(),
                    "type": "manual_generation",
                    "reused_from_collection": True,
                    "collection_id": similar_collection['id'],
                    "collection_name": similar_collection['collection_name'],
                    "avatar_image_url": similar_collection['avatar_image_url']
                }
                
                outfit_id = save_outfit(
                    user_id=user_id,
                    outfit_name=f"Bonus Outfit {datetime.now().strftime('%Y-%m-%d')} (Reused)",
                    outfit_data=json.dumps(outfit_data),
                    weather_condition="Manual Generation",
                    occasion="Daily Bonus"
                )
                
                return jsonify({
                    "success": True,
                    "message": f"✨ Your bonus outfit has been generated! (Reused from collection: {similar_collection['collection_name']})",
                    "outfit_id": outfit_id,
                    "reused": True,
                    "collection_name": similar_collection['collection_name'],
                    "avatar_image_url": similar_collection['avatar_image_url']
                })
            else:
                # Generate new outfit with image
                from database import save_outfit
                from generate_visualisation import generate_image
                import json
                
                # Generate outfit image
                try:
                    vancouver_time = get_vancouver_time()
                    timestamp = vancouver_time.strftime("%Y%m%d_%H%M%S")
                    output_filename = f"bonus_outfit_{timestamp}.png"
                    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                    
                    # Load avatar description
                    avatar_path = os.path.join(os.path.dirname(__file__), 'data', 'avatar.txt')
                    
                    # Load clothing descriptions for selected outfit
                    clothes_paths = []
                    for item_filename in outfits[0]:
                        # Find corresponding .txt file
                        txt_filename = item_filename.replace('.jpg', '.txt').replace('.jpeg', '.txt').replace('.png', '.txt')
                        txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
                        if os.path.exists(txt_path):
                            clothes_paths.append(txt_path)
                        else:
                            print(f"Warning: Description file not found for {item_filename}")
                    
                    if not clothes_paths:
                        return jsonify({
                            "success": False,
                            "error": "No clothing descriptions found for selected outfit"
                        }), 400
                    
                    # Load texts and create combined prompt
                    from generate_visualisation import load_texts, sanitize_prompt
                    texts = load_texts([avatar_path] + clothes_paths)
                    raw_prompt = "\n".join(texts)
                    prompt = sanitize_prompt(raw_prompt)
                    
                    print(f"Generated prompt: {prompt[:200]}...")
                    
                    # Generate the image
                    api_key = os.getenv("OPENAI_API_KEY")
                    image_bytes = generate_image(
                        prompt=prompt,
                        api_key=api_key
                    )
                    
                    # Save the image to file
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    
                    image_url = f"/output/{output_filename}"
                    
                    # Automatically save to collections (View Saved Outfits)
                    try:
                        from database import save_collection
                        user_id = session.get('user_id', 1)
                        
                        # Create outfit description
                        outfit_description = f"Weather-appropriate outfit for {weather or 'moderate'} weather"
                        tags = f"daily,{weather or 'moderate'},{occasion or 'casual'}"
                        
                        # Save to collections
                        collection_id = save_collection(
                            user_id=user_id,
                            collection_name=f"Daily Outfit {datetime.now().strftime('%Y-%m-%d')}",
                            collection_type="daily_outfit",
                            avatar_image_url=image_url,
                            outfit_description=outfit_description,
                            tags=tags
                        )
                        print(f"Automatically saved outfit to collections: {collection_id}")
                    except Exception as e:
                        print(f"Failed to auto-save outfit to collections: {e}")
                    
                    outfit_data = {
                        "outfit_items": outfits[0],
                        "generated_at": datetime.now().isoformat(),
                        "type": "manual_generation",
                        "avatar_image_url": f"/output/{output_filename}"
                    }
                    
                except Exception as e:
                    print(f"Image generation failed: {e}")
                    # Fallback without image
                    outfit_data = {
                        "outfit_items": outfits[0],
                        "generated_at": datetime.now().isoformat(),
                        "type": "manual_generation"
                    }
                    image_url = None
                
                outfit_id = save_outfit(
                    user_id=user_id,
                    outfit_name=f"Bonus Outfit {datetime.now().strftime('%Y-%m-%d')}",
                    outfit_data=json.dumps(outfit_data),
                    weather_condition="Manual Generation",
                    occasion="Daily Bonus"
                )
                
                return jsonify({
                    "success": True,
                    "message": f"✨ Your bonus outfit has been generated! Check your home screen.",
                    "outfit_id": outfit_id,
                    "reused": False,
                    "avatar_image_url": image_url
                })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to generate outfit: {str(e)}"
            }), 500
    
    # Setup scheduled tasks (only in main process, not reloader)
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = BackgroundScheduler(timezone='America/Vancouver')
        
        # Schedule daily outfit generation at 5:00 AM Vancouver time
        scheduler.add_job(
            func=generate_daily_outfits_task,
            trigger=CronTrigger(hour=5, minute=0, timezone='America/Vancouver'),
            id='daily_outfits',
            name='Generate daily outfit recommendations',
            replace_existing=True
        )
        
        scheduler.start()
        print("\n" + "=" * 60)
        print("📅 Scheduler started: Daily outfits will be generated at 5:00 AM")
        print("=" * 60 + "\n")
        
        # Cleanup scheduler on app shutdown
        import atexit
        atexit.register(lambda: scheduler.shutdown())
    
    return app

if __name__ == '__main__':
    app = create_app()


    app.run(debug=True, host='0.0.0.0', port=8080) 