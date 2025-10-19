"""
style_agent.py
Selects multiple outfit combinations from /data/clothes based on user needs (tags, weather, occasion).
"""

import os
import random

def load_closet_txts(closet_dir):
    items = []
    # Get all image files
    image_files = [f for f in os.listdir(closet_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    txt_files = set(f for f in os.listdir(closet_dir) if f.endswith('.txt'))
    for img in image_files:
        base = os.path.splitext(img)[0]
        txt_name = base + '.txt'
        img_path = '/data/clothes/input/' + img
        if txt_name in txt_files:
            with open(os.path.join(closet_dir, txt_name), encoding='utf-8') as f:
                desc = f.read()
            desc_lower = desc.lower()
            if any(word in desc_lower for word in ['dress']):
                category = 'Dresses'
            elif any(word in desc_lower for word in ['blouse', 'top', 'shirt', 't-shirt', 'sweater', 'hoodie', 'tank', 'crop', 'blazer', 'cardigan', 'pullover', 'polo', 'camisole', 'tunic']):
                category = 'Tops'
            elif any(word in desc_lower for word in ['pants', 'skirt', 'jeans', 'shorts', 'trousers', 'leggings', 'capri', 'cargo', 'chinos', 'trousers']):
                category = 'Bottoms'
            elif any(word in desc_lower for word in ['shoes', 'sneaker', 'boot', 'sandals', 'loafer', 'heel', 'sneakers', 'boots', 'flats', 'pumps', 'oxfords', 'mules', 'clogs', 'slippers']):
                category = 'Shoes'
            elif any(word in desc_lower for word in ['jacket', 'coat', 'blazer', 'cardigan', 'sweater', 'hoodie', 'vest', 'windbreaker', 'trench', 'parka', 'bomber', 'denim jacket', 'leather jacket']):
                category = 'Outerwear'
            elif any(word in desc_lower for word in ['bag', 'handbag', 'backpack', 'purse', 'tote', 'clutch', 'satchel', 'hat', 'cap', 'scarf', 'belt', 'glove', 'accessory', 'jewelry', 'watch', 'sunglasses', 'necklace', 'bracelet', 'earrings', 'ring']):
                category = 'Accessories'
            else:
                category = 'Accessories'  # デフォルトをAccessoriesに変更
        else:
            desc = "Description not available yet."
            category = "Pending"
        items.append({'file': txt_name, 'desc': desc, 'image': img_path, 'category': category})
    return items

def filter_by_weather(items, weather):
    """Filter items based on weather conditions."""
    if not weather:
        return items

    weather = weather.lower()
    filtered_items = []

    for item in items:
        desc = item['desc'].lower()

        # For warm weather
        if weather in ['warm', 'hot', 'summer']:
            # Prioritize lightweight fabrics, short sleeves, thin clothing
            if any(word in desc for word in ['lightweight', 'cotton', 'linen', 'short-sleeved', 'sleeveless', 'flowy', 'breathable']):
                filtered_items.append(item)
            # Exclude thick materials
            elif any(word in desc for word in ['wool', 'thick', 'heavy', 'winter', 'warm']):
                continue
            else:
                filtered_items.append(item)  # Include other clothing by default

        # For cold weather
        elif weather in ['cold', 'winter', 'cool']:
            # Prioritize thick fabrics and long sleeves
            if any(word in desc for word in ['wool', 'thick', 'warm', 'long-sleeved', 'sweater', 'jacket', 'coat']):
                filtered_items.append(item)
            # Exclude thin materials
            elif any(word in desc for word in ['sleeveless', 'thin', 'lightweight']):
                continue
            else:
                filtered_items.append(item)

        # For rainy weather
        elif weather in ['rainy', 'wet']:
            # Prioritize waterproof materials
            if any(word in desc for word in ['waterproof', 'water-resistant', 'nylon', 'polyester']):
                filtered_items.append(item)
            else:
                filtered_items.append(item)

        else:
            # If weather is unspecified, include all items
            filtered_items.append(item)

    return filtered_items

def select_outfit(criteria, closet_dir="data/clothes/input"):
    items = load_closet_txts(closet_dir)

    # Filter by weather
    weather = criteria.get('weather') if criteria else None
    items = filter_by_weather(items, weather)

    print(f"Weather condition: {weather}")
    print(f"Available items after weather filtering: {len(items)}")

    # Classify by category
    dress = [i for i in items if "dress" in i['desc'].lower()]
    tops = [i for i in items if "blouse" in i['desc'].lower() or "top" in i['desc'].lower() or "shirt" in i['desc'].lower()]
    bottoms = [i for i in items if "pants" in i['desc'].lower() or "skirt" in i['desc'].lower()]

    print(f"Found {len(dress)} dresses, {len(tops)} tops, {len(bottoms)} bottoms")

    # Priority: dress > top + bottom
    if dress:
        selected = [dress[0]['file']]
        print(f"Selected dress: {selected[0]}")
        print(f"Recommended outfit: {selected}")
        return selected
    elif tops and bottoms:
        selected = [tops[0]['file'], bottoms[0]['file']]
        print(f"Selected outfit: {selected[0]} + {selected[1]}")
        print(f"Recommended outfit: {selected}")
        return selected
    else:
        print("No suitable outfit found")
        print("Recommended outfit: []")
        return []

def select_multiple_outfits(num=4, closet_dir="data/clothes/input", criteria=None):
    """
    Returns up to `num` unique outfit combinations (each as a list of filenames).
    Ensures variety by shuffling and picking different items.
    """
    items = load_closet_txts(closet_dir)
    # Filter by weather if criteria is provided
    weather = criteria.get('weather') if criteria else None
    items = filter_by_weather(items, weather)

    # Group items by category for balanced selection
    items_by_category = {}
    for item in items:
        category = item['category']
        if category not in items_by_category:
            items_by_category[category] = []
        items_by_category[category].append(item)

    outfits = []
    used = set()
    
    # Try to generate as many unique outfits as possible
    for _ in range(num):
        outfit = select_balanced_outfit(items_by_category, used)
        if outfit:
            outfits.append(outfit)
            used.update(outfit)
        else:
            break  # No more unique combinations possible
    
    return outfits

def select_balanced_outfit(items_by_category, used_items):
    """Select an outfit with smart color coordination and layering."""
    outfit = []
    
    # Priority order for categories
    category_priority = ['Dresses', 'Tops', 'Bottoms', 'Shoes', 'Outerwear', 'Accessories']
    
    # Try to select from each category with smart coordination
    for category in category_priority:
        if category in items_by_category:
            category_items = [item for item in items_by_category[category] if item['file'] not in used_items]
            if category_items:
                # For dresses, we might want to use only dress (not top+bottom)
                if category == 'Dresses' and len(outfit) == 0:
                    selected_item = smart_select_item(category_items, outfit, category)
                    if selected_item:
                        outfit.append(selected_item['file'])
                    break
                elif category != 'Dresses':
                    selected_item = smart_select_item(category_items, outfit, category)
                    if selected_item:
                        outfit.append(selected_item['file'])
    
    # Add layering items if appropriate
    outfit = add_layering_items(outfit, items_by_category, used_items)
    
    # If we don't have enough items, add more from any category
    all_available = []
    for category_items in items_by_category.values():
        for item in category_items:
            if item['file'] not in used_items and item['file'] not in outfit:
                all_available.append(item)
    
    while len(outfit) < 4 and len(outfit) < len(all_available):
        if all_available:
            selected_item = smart_select_item(all_available, outfit, 'Any')
            if selected_item:
                outfit.append(selected_item['file'])
                all_available.remove(selected_item)
            else:
                break
        else:
            break
    
    return outfit

def smart_select_item(candidates, current_outfit, category):
    """Select an item that coordinates well with the current outfit."""
    if not candidates:
        return None
    
    # If no items in outfit yet, select randomly
    if not current_outfit:
        return random.choice(candidates)
    
    # Score each candidate based on coordination
    scored_candidates = []
    for item in candidates:
        score = calculate_coordination_score(item, current_outfit, category)
        scored_candidates.append((item, score))
    
    # Sort by score (higher is better) and add some randomness
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Select from top 3 candidates with weighted randomness
    top_candidates = scored_candidates[:min(3, len(scored_candidates))]
    weights = [max(0.1, score) for _, score in top_candidates]
    
    if weights and sum(weights) > 0:
        selected = random.choices([item for item, _ in top_candidates], weights=weights)[0]
        return selected
    else:
        return random.choice(candidates)

def calculate_coordination_score(item, current_outfit, category):
    """Calculate how well an item coordinates with the current outfit."""
    score = 0
    
    # Extract color information from item description
    item_colors = extract_colors(item['desc'])
    
    # Check color coordination with existing items
    for outfit_item in current_outfit:
        # This is a simplified check - in a real system, you'd parse the actual item data
        outfit_colors = extract_colors_from_filename(outfit_item)  # Simplified
        color_score = calculate_color_harmony(item_colors, outfit_colors)
        score += color_score
    
    # Category-specific scoring
    if category == 'Tops':
        # Prefer versatile tops that can be layered
        if any(word in item['desc'].lower() for word in ['basic', 'solid', 'neutral', 'white', 'black', 'gray']):
            score += 2
        # Prefer layering-friendly items
        if any(word in item['desc'].lower() for word in ['tank', 'camisole', 't-shirt', 'blouse']):
            score += 1
    elif category == 'Outerwear':
        # Prefer outerwear that complements the base outfit
        if any(word in item['desc'].lower() for word in ['blazer', 'cardigan', 'jacket']):
            score += 1
    elif category == 'Accessories':
        # Prefer accessories that add interest without clashing
        score += 0.5  # Neutral score for accessories
    
    return score

def extract_colors(description):
    """Extract color information from item description."""
    colors = []
    color_keywords = {
        'black': ['black', 'dark', 'charcoal', 'ebony'],
        'white': ['white', 'cream', 'ivory', 'off-white'],
        'blue': ['blue', 'navy', 'royal blue', 'sky blue'],
        'red': ['red', 'crimson', 'burgundy', 'maroon'],
        'green': ['green', 'emerald', 'forest green', 'mint'],
        'yellow': ['yellow', 'gold', 'mustard', 'lemon'],
        'pink': ['pink', 'rose', 'magenta', 'fuchsia'],
        'purple': ['purple', 'violet', 'lavender', 'plum'],
        'brown': ['brown', 'tan', 'beige', 'khaki', 'camel'],
        'gray': ['gray', 'grey', 'silver', 'slate']
    }
    
    desc_lower = description.lower()
    for color, keywords in color_keywords.items():
        if any(keyword in desc_lower for keyword in keywords):
            colors.append(color)
    
    return colors

def extract_colors_from_filename(filename):
    """Simplified color extraction from filename (placeholder)."""
    # In a real implementation, you'd parse the actual item data
    return []

def calculate_color_harmony(colors1, colors2):
    """Calculate color harmony score between two sets of colors."""
    if not colors1 or not colors2:
        return 0
    
    # Basic color harmony rules
    harmony_rules = {
        'black': ['white', 'gray', 'red', 'blue', 'green', 'yellow', 'pink', 'purple'],
        'white': ['black', 'gray', 'blue', 'red', 'green', 'yellow', 'pink', 'purple'],
        'gray': ['black', 'white', 'blue', 'red', 'green', 'yellow', 'pink', 'purple'],
        'blue': ['white', 'gray', 'black', 'yellow', 'pink', 'green'],
        'red': ['white', 'black', 'gray', 'blue', 'green'],
        'green': ['white', 'black', 'gray', 'blue', 'red', 'yellow'],
        'yellow': ['black', 'gray', 'blue', 'green', 'purple'],
        'pink': ['white', 'gray', 'blue', 'green', 'purple'],
        'purple': ['white', 'gray', 'yellow', 'pink', 'green']
    }
    
    score = 0
    for color1 in colors1:
        for color2 in colors2:
            if color1 == color2:
                score += 3  # Same color
            elif color2 in harmony_rules.get(color1, []):
                score += 2  # Harmonious colors
            else:
                score += 0.5  # Neutral
    
    return score

def add_layering_items(outfit, items_by_category, used_items):
    """Add layering items like shirts under sweaters, tank tops under blouses."""
    layered_outfit = outfit.copy()
    
    # Check if we have a sweater or hoodie that could be layered
    for item_file in outfit:
        # This is simplified - in reality you'd check the actual item data
        if any(word in item_file.lower() for word in ['sweater', 'hoodie', 'cardigan']):
            # Look for a suitable base layer
            base_layer_candidates = []
            if 'Tops' in items_by_category:
                for item in items_by_category['Tops']:
                    if item['file'] not in used_items and item['file'] not in outfit:
                        if any(word in item['desc'].lower() for word in ['tank', 'camisole', 't-shirt', 'blouse']):
                            base_layer_candidates.append(item)
            
            if base_layer_candidates:
                # Select a base layer that coordinates well
                selected_base = smart_select_item(base_layer_candidates, layered_outfit, 'Tops')
                if selected_base:
                    layered_outfit.insert(0, selected_base['file'])  # Add as base layer
                    break
    
    return layered_outfit

if __name__ == "__main__":
    # Example usage with different weather conditions
    test_criteria = [
        {"weather": "warm", "occasion": "casual"},
        {"weather": "cold", "occasion": "formal"},
        {"weather": "rainy", "occasion": "casual"},
        {}  # No weather specified
    ]

    for criteria in test_criteria:
        print(f"\n--- Testing with criteria: {criteria} ---")
        selected = select_outfit(criteria)
