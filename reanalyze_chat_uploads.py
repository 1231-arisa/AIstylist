#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('src')

from database import get_user_images, save_uploaded_image
from generate_item import analyze_image
from app import extract_item_info
import json

def reanalyze_chat_uploads():
    """Re-analyze chat uploads that failed or have generic names"""
    items = get_user_images(1)
    
    for item in items:
        filename = item.get('filename', '')
        analysis_data = item.get('analysis', '{}')
        
        # Check if this is a chat upload or has generic analysis
        try:
            analysis = json.loads(analysis_data)
            item_name = analysis.get('item_name', '')
            category = analysis.get('category', '')
            description = analysis.get('description', '')
            
            # Re-analyze if it's a chat upload or has generic data
            should_reanalyze = (
                'chat_upload' in filename or
                item_name in ['Chat Upload', 'S__21733430_0', 'S__21733428_0'] or
                'analysis pending' in description or
                category == 'Clothing'
            )
            
            if should_reanalyze:
                print(f"\nRe-analyzing: {filename}")
                
                # Find the image file
                image_path = f"data/clothes/input/{filename}"
                if os.path.exists(image_path):
                    try:
                        # Analyze the image
                        analysis_text = analyze_image(image_path)
                        print(f"Analysis result: {analysis_text[:100]}...")
                        
                        # Extract item info
                        item_info = extract_item_info(analysis_text)
                        
                        # Create new analysis data
                        new_analysis = {
                            "item_name": item_info.get("item_name", "Clothing Item"),
                            "category": item_info.get("category", "Clothing"),
                            "color": item_info.get("color", "Unknown"),
                            "style": item_info.get("style", "Unknown"),
                            "description": analysis_text,
                            "image_url": item.get('url', '')
                        }
                        
                        # Save to database
                        save_uploaded_image(
                            user_id=1,
                            filename=filename,
                            original_name=item.get('original_name', filename),
                            url=item.get('url', ''),
                            analysis=json.dumps(new_analysis)
                        )
                        
                        # Save analysis text to file
                        txt_filename = filename.replace('.jpg', '.txt')
                        txt_path = f"data/clothes/input/{txt_filename}"
                        with open(txt_path, 'w', encoding='utf-8') as f:
                            f.write(analysis_text)
                        
                        print(f"✅ Updated: {item_info.get('item_name', 'N/A')} - {item_info.get('category', 'N/A')}")
                        
                    except Exception as e:
                        print(f"❌ Failed to analyze {filename}: {e}")
                else:
                    print(f"❌ Image file not found: {image_path}")
            else:
                print(f"✓ Skipping {filename} (already analyzed)")
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    reanalyze_chat_uploads()

