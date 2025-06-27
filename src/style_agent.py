"""
style_agent.py
Selects multiple outfit combinations from /data/clothes based on user needs (tags, weather, occasion).
"""

import os
import random

def load_closet_txts(closet_dir):
    items = []
    for fname in os.listdir(closet_dir):
        if fname.endswith('.txt'):
            base = fname[:-4]
            img_path = None
            for ext in ['.jpg', '.jpeg', '.png']:
                candidate = os.path.join(closet_dir, base + ext)
                if os.path.exists(candidate):
                    # Flaskのstatic配下でなければ、/data/clothes/input/からの相対パスで返す
                    img_path = '/data/clothes/input/' + base + ext
                    break
            with open(os.path.join(closet_dir, fname), encoding='utf-8') as f:
                desc = f.read()
            items.append({'file': fname, 'desc': desc, 'image': img_path})
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

    # Classify by category
    dresses = [i for i in items if "dress" in i['desc'].lower()]
    tops = [i for i in items if any(word in i['desc'].lower() for word in ["blouse", "top", "shirt"])]
    bottoms = [i for i in items if any(word in i['desc'].lower() for word in ["pants", "skirt"])]

    outfits = []
    used = set()
    # Try to generate as many unique outfits as possible
    for _ in range(num):
        # Priority: dress > top+bottom
        outfit = []
        # Try to pick an unused dress
        available_dresses = [d for d in dresses if d['file'] not in used]
        if available_dresses:
            d = random.choice(available_dresses)
            outfit = [d['file']]
            used.add(d['file'])
        elif tops and bottoms:
            available_tops = [t for t in tops if t['file'] not in used]
            available_bottoms = [b for b in bottoms if b['file'] not in used]
            if available_tops and available_bottoms:
                t = random.choice(available_tops)
                b = random.choice(available_bottoms)
                outfit = [t['file'], b['file']]
                used.add(t['file'])
                used.add(b['file'])
        if outfit:
            outfits.append(outfit)
        else:
            break  # No more unique outfits possible
    return outfits

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
