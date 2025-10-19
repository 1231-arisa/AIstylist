#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import get_user_images
import json

def check_chat_uploads():
    """Check chat uploads and their analysis"""
    items = get_user_images(1)
    print(f"Total items in database: {len(items)}")
    print("\nRecent items:")
    
    for item in items[-10:]:  # Show last 10 items
        print(f"\nFile: {item.get('filename', 'N/A')}")
        print(f"Original name: {item.get('original_name', 'N/A')}")
        
        analysis_data = item.get('analysis')
        if analysis_data:
            try:
                analysis = json.loads(analysis_data)
                print(f"Item name: {analysis.get('item_name', 'N/A')}")
                print(f"Category: {analysis.get('category', 'N/A')}")
                print(f"Color: {analysis.get('color', 'N/A')}")
                print(f"Style: {analysis.get('style', 'N/A')}")
                description = analysis.get('description', 'N/A')
                print(f"Description: {description[:100]}{'...' if len(description) > 100 else ''}")
            except Exception as e:
                print(f"Error parsing analysis: {e}")
                print(f"Raw analysis: {analysis_data[:100]}...")
        else:
            print("No analysis data")

if __name__ == "__main__":
    check_chat_uploads()
