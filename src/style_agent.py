"""
style_agent.py
Selects outfit combinations from /data/clothes based on user needs (tags, weather, occasion).
"""

import os

def load_closet_txts(closet_dir):
    items = []
    for fname in os.listdir(closet_dir):
        if fname.endswith('.txt'):
            with open(os.path.join(closet_dir, fname), encoding='utf-8') as f:
                desc = f.read()
            items.append({'file': fname, 'desc': desc})
    return items

def select_outfit(criteria, closet_dir="data/clothes/input"):
    items = load_closet_txts(closet_dir)
    # Prioritize dress, otherwise top + bottom
    dress = [i for i in items if "dress" in i['desc'].lower()]
    tops = [i for i in items if "blouse" in i['desc'].lower() or "top" in i['desc'].lower()]
    bottoms = [i for i in items if "pants" in i['desc'].lower() or "skirt" in i['desc'].lower()]
    if dress:
        return [dress[0]['file']]
    elif tops and bottoms:
        return [tops[0]['file'], bottoms[0]['file']]
    else:
        return []

if __name__ == "__main__":
    # Example usage
    selected = select_outfit({"weather": "warm", "occasion": "casual"})
    print("Recommended outfit:", selected) 