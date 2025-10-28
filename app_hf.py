"""
AIstylist - Hugging Face Spaces Version
Simplified version for Hugging Face Spaces deployment
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

# Import backend functionality
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from generate_item import analyze_image, get_image_hash
from style_agent import select_outfit, load_closet_txts, select_multiple_outfits
from generate_visualisation import generate_image, sanitize_prompt

# Import services
from database import init_database, create_user, get_user_subscription, save_chat_message, get_chat_messages, save_uploaded_image, get_user_images, save_outfit, get_user_outfits
from weather_service import get_weather_data, get_weather_recommendation, get_weekly_forecast
from chat_service import process_chat_message, get_recommended_outfits_from_closet

# Occasion types for outfit recommendations
OCCASION_TYPES = [
    'Casual',      # Everyday wear, relaxed atmosphere
    'Business',     # Office, meetings
    'Smart Casual',# Neat casual, polished everyday look
    'Formal',      # Formal wear, ceremonies
    'Sporty',      # Active, athletic
    'Chic',        # Sophisticated, elegant
    'Bohemian',    # Free-spirited, ethnic style
    'Street',      # Urban, trendy
    'Romantic',    # Feminine, soft
    'Minimalist',  # Simple, refined
    'Vintage',     # Retro, classic
    'Preppy',      # Clean, preppy casual
]

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "hf_spaces_secret_key")
    
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
        return now.strftime("%b %d")

    def generate_daily_outfits():
        """Generate daily outfit recommendations"""
        output_dir = app.config['OUTPUT_FOLDER']
        
        # Get existing outfit images
        all_pngs = [f for f in os.listdir(output_dir) if f.endswith(".png")]
        all_pngs = sorted(all_pngs, key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
        
        # Get weather information
        weather_info = get_weather_data()
        weather_condition = weather_info.get('condition', 'Sunny') if weather_info else 'Sunny'
        weather_temp = weather_info.get('temperature', 22) if weather_info else 22

        # Select diverse occasions for variety
        import random
        selected_occasions = random.sample(OCCASION_TYPES, min(4, len(OCCASION_TYPES)))

        outfits = []
        for idx, filename in enumerate(all_pngs[:4]):
            occasion = selected_occasions[idx] if idx < len(selected_occasions) else 'Casual'
            outfits.append({
                'name': f'Outfit {idx+1}',
                'image': f'/output/{filename}',
                'weather': weather_condition,
                'temperature': weather_temp,
                'occasion': occasion,
                'files': []
            })
        
        # If no outfits, create placeholder
        if not outfits:
            outfits.append({
                'name': 'Welcome to AIstylist',
                'image': '/static/images/female-avatar.png',
                'weather': weather_condition,
                'temperature': weather_temp,
                'occasion': 'Casual',
                'files': []
            })
        
        return outfits

    @app.route('/')
    def index():
        """Main page"""
        outfits = generate_daily_outfits()
        weather_info = get_weather_data('Vancouver')
        
        # Get closet items from database
        user_id = session.get('user_id', 1)
        
        try:
            closet_items = get_user_images(user_id)
        except Exception as e:
            print(f"Error loading closet items: {e}")
            closet_items = []
        
        return render_template('home.html', outfits=outfits, weather_info=weather_info, closet_items=closet_items)

    @app.route('/api/weather')
    def api_weather():
        """Get weather data API"""
        location = request.args.get('location', 'Vancouver')
        weather_data = get_weather_data(location)
        return jsonify(weather_data)

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
            user_id = session.get('user_id', 1)
            
            # Process chat message
            ai_response = process_chat_message(user_id, message, image_data, weather, occasion)
            
            return jsonify({
                'success': True,
                'reply': ai_response
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

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

    return app

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

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=7860)
