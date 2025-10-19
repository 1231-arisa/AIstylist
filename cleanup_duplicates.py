#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import get_user_images, delete_uploaded_image
import json

def cleanup_duplicates():
    """Remove duplicate entries, keeping the ones with proper analysis"""
    items = get_user_images(1)
    
    # Group by filename
    filename_groups = {}
    for item in items:
        filename = item['filename']
        if filename not in filename_groups:
            filename_groups[filename] = []
        filename_groups[filename].append(item)
    
    # For each group, keep the best entry and delete others
    for filename, group in filename_groups.items():
        if len(group) > 1:
            print(f"\nFound {len(group)} entries for {filename}")
            
            # Find the best entry (with proper analysis)
            best_entry = None
            for entry in group:
                analysis = json.loads(entry['analysis'])
                item_name = analysis.get('item_name', '')
                category = analysis.get('category', '')
                
                # Prefer entries with proper names and categories
                if (item_name not in ['Chat Upload', 'S__21733430_0', 'S__21733428_0'] and 
                    category != 'Clothing' and 
                    'analysis pending' not in analysis.get('description', '')):
                    best_entry = entry
                    break
            
            # If no good entry found, keep the first one
            if not best_entry:
                best_entry = group[0]
            
            print(f"Keeping: {best_entry['filename']} - {json.loads(best_entry['analysis']).get('item_name', 'N/A')}")
            
            # Delete the others
            for entry in group:
                if entry != best_entry:
                    print(f"Deleting: {entry['filename']} - {json.loads(entry['analysis']).get('item_name', 'N/A')}")
                    try:
                        delete_uploaded_image(1, entry['filename'])  # user_id = 1
                    except Exception as e:
                        print(f"Error deleting {entry['filename']}: {e}")

if __name__ == "__main__":
    cleanup_duplicates()
