#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import get_user_images
import json

def check_all_items():
    items = get_user_images(1)
    print(f"Total items: {len(items)}")
    
    # Check all items with timestamps
    for i, item in enumerate(items):
        print(f"\n--- Item {i+1} ---")
        print(f"File: {item['filename']}")
        print(f"Original: {item['original_name']}")
        
        analysis = json.loads(item['analysis'])
        print(f"Name: {analysis.get('item_name', 'N/A')}")
        print(f"Category: {analysis.get('category', 'N/A')}")
        print(f"Color: {analysis.get('color', 'N/A')}")
        print(f"Style: {analysis.get('style', 'N/A')}")
        description = analysis.get('description', 'N/A')
        print(f"Description: {description[:50]}...")

if __name__ == "__main__":
    check_all_items()

