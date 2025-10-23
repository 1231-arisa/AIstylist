"""
ai_style_agent.py
AI-powered outfit selection using GPT-4o for more sophisticated styling rules.
"""

import os
import json
import openai
from typing import List, Dict, Any, Optional

def load_closet_items(closet_dir: str) -> List[Dict[str, Any]]:
    """Load all clothing items with their descriptions."""
    items = []
    image_files = [f for f in os.listdir(closet_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    txt_files = set(f for f in os.listdir(closet_dir) if f.endswith('.txt'))
    
    for img in image_files:
        base = os.path.splitext(img)[0]
        txt_name = base + '.txt'
        img_path = os.path.join(closet_dir, img)
        
        if txt_name in txt_files:
            txt_path = os.path.join(closet_dir, txt_name)
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    description = f.read().strip()
                
                # Basic category detection (fallback)
                category = detect_category(description)
                
                items.append({
                    'filename': img,
                    'description': description,
                    'category': category,
                    'image_path': img_path
                })
            except Exception as e:
                print(f"Error loading {txt_name}: {e}")
                continue
    
    return items

def detect_category(description: str) -> str:
    """Basic category detection as fallback."""
    desc_lower = description.lower()
    
    if any(word in desc_lower for word in ['dress']):
        return 'Dresses'
    elif any(word in desc_lower for word in ['blouse', 'top', 'shirt', 't-shirt', 'sweater', 'hoodie', 'tank', 'crop', 'blazer', 'cardigan', 'pullover', 'polo', 'camisole', 'tunic']):
        return 'Tops'
    elif any(word in desc_lower for word in ['pants', 'skirt', 'jeans', 'shorts', 'trousers', 'leggings', 'capri', 'cargo', 'chinos']):
        return 'Bottoms'
    elif any(word in desc_lower for word in ['shoes', 'sneaker', 'boot', 'sandals', 'loafer', 'heel', 'sneakers', 'boots', 'flats', 'pumps', 'oxfords', 'mules', 'clogs', 'slippers']):
        return 'Shoes'
    elif any(word in desc_lower for word in ['jacket', 'coat', 'blazer', 'cardigan', 'sweater', 'hoodie', 'vest', 'windbreaker', 'trench', 'parka', 'bomber', 'denim jacket', 'leather jacket']):
        return 'Outerwear'
    else:
        return 'Accessories'

def create_outfit_selection_prompt(items: List[Dict[str, Any]], weather: Optional[str] = None, occasion: str = "casual") -> str:
    """Create a prompt for GPT-4o to select outfit combinations."""
    
    # Prepare items description
    items_text = ""
    for i, item in enumerate(items, 1):
        items_text += f"{i}. {item['filename']} ({item['category']}): {item['description'][:200]}...\n"
    
    prompt = f"""You are a professional fashion stylist. Select the best outfit combination from the available clothing items.

Available Items:
{items_text}

Context:
- Weather: {weather or 'Not specified'}
- Occasion: {occasion}
- Style: Modern, balanced, and well-coordinated

Please select 1-4 items that work well together as a complete outfit. Consider:
1. Color harmony and coordination
2. Weather appropriateness
3. Occasion suitability
4. Style balance and proportion
5. Layering opportunities (only suggest layering if it enhances the outfit - e.g., shirt under sweater, tank under blouse, or jacket over top)

Guidelines for layering:
- Only suggest layering if it makes the outfit more stylish or weather-appropriate
- Consider if the weather calls for layering (cooler temperatures)
- Ensure layered items complement each other in color and style
- Don't force layering if a single item works better alone

Respond with a JSON array containing the filenames of selected items, like this:
["filename1.jpg", "filename2.jpg", "filename3.jpg"]

Only include the filenames, no additional text."""

    return prompt

def select_outfit_with_ai(items: List[Dict[str, Any]], weather: Optional[str] = None, occasion: str = "casual", api_key: str = None) -> Optional[List[str]]:
    """Use GPT-4o to select an outfit combination."""
    
    if not api_key:
        print("Error: OpenAI API key not provided")
        return None
    
    if not items:
        print("Error: No clothing items available")
        return None
    
    try:
        # Set up OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Create prompt
        prompt = create_outfit_selection_prompt(items, weather, occasion)
        
        # Call GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional fashion stylist with expertise in color coordination, layering, and outfit composition."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response
        if response_text.startswith('[') and response_text.endswith(']'):
            selected_filenames = json.loads(response_text)
        else:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\[.*?\]', response_text)
            if json_match:
                selected_filenames = json.loads(json_match.group())
            else:
                print(f"Could not parse AI response: {response_text}")
                return None
        
        # Validate selected filenames
        available_filenames = {item['filename'] for item in items}
        valid_selections = [f for f in selected_filenames if f in available_filenames]
        
        if not valid_selections:
            print("No valid selections found in AI response")
            return None
        
        print(f"AI selected outfit: {valid_selections}")
        return valid_selections
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"AI outfit selection error: {e}")
        return None

def select_multiple_outfits_ai(num: int = 1, closet_dir: str = "data/clothes/input", weather: Optional[str] = None, api_key: str = None) -> List[List[str]]:
    """Select multiple outfit combinations using AI."""
    
    # Load items
    items = load_closet_items(closet_dir)
    
    if not items:
        print("No clothing items found")
        return []
    
    outfits = []
    
    for i in range(num):
        # Create a copy of items for this selection
        available_items = items.copy()
        
        # Remove items already used in previous outfits
        used_filenames = {filename for outfit in outfits for filename in outfit}
        available_items = [item for item in available_items if item['filename'] not in used_filenames]
        
        if not available_items:
            print(f"Not enough items for outfit {i+1}")
            break
        
        # Select outfit using AI
        selected_filenames = select_outfit_with_ai(available_items, weather, api_key=api_key)
        
        if selected_filenames:
            outfits.append(selected_filenames)
        else:
            print(f"Failed to select outfit {i+1}")
            break
    
    return outfits

def fallback_to_original_selection(num: int = 1, closet_dir: str = "data/clothes/input", weather: Optional[str] = None) -> List[List[str]]:
    """Fallback to original selection method if AI fails."""
    try:
        from style_agent import select_multiple_outfits
        criteria = {'weather': weather} if weather else None
        return select_multiple_outfits(num=num, closet_dir=closet_dir, criteria=criteria)
    except Exception as e:
        print(f"Fallback selection also failed: {e}")
        return []
