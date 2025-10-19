"""
Chat service for AIstylist
Handles chat message processing and outfit recommendations
"""

import os
import json
from typing import List, Dict, Any, Optional
from database import save_chat_message, get_chat_messages, get_user_images

def process_chat_message(user_id: int, message: str, message_type: str = 'text') -> str:
    """Process chat message and return AI response"""
    try:
        # Get user's closet items for context
        closet_items = get_user_images(user_id, limit=10)
        closet_context = ""
        if closet_items:
            closet_context = "\n\nUser's closet items:\n"
            for item in closet_items:
                if item.get('analysis'):
                    try:
                        analysis = json.loads(item['analysis'])
                        closet_context += f"- {analysis.get('item_name', 'Item')}: {analysis.get('description', '')}\n"
                    except:
                        closet_context += f"- {item.get('original_name', 'Item')}\n"
        
        # Get recent chat history for context
        recent_messages = get_chat_messages(user_id, limit=5)
        chat_history = ""
        if recent_messages:
            chat_history = "\n\nRecent conversation:\n"
            for msg in recent_messages[:3]:  # Last 3 messages
                chat_history += f"User: {msg['message']}\n"
                chat_history += f"AI: {msg['reply']}\n"
        
        # Create system prompt
        system_prompt = f"""You are AIstylist, a personal fashion consultant. Help users with styling advice, outfit coordination, and fashion questions.

{closet_context}{chat_history}

Guidelines:
- Be friendly, honest, and supportive
- Give specific, actionable advice
- Consider the user's existing wardrobe
- Keep responses concise (2-4 sentences)
- Use phrases like "I'd suggest...", "Try pairing...", "This would work well because..."
- Avoid generic compliments or saying everything looks great
- Be encouraging but honest about what works and what doesn't"""

        # Try OpenAI first
        openai_key = os.getenv("OPENAI_API_KEY")
        print(f"🔍 Chat API Key loaded: {'Yes' if openai_key else 'No'}")
        if openai_key and openai_key != "your-openai-key":
            try:
                print(f"🤖 Sending chat request to OpenAI...")
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                response = client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                reply = response.choices[0].message.content
                print(f"✅ Chat response received: {reply[:50]}...")
                
                # Save the conversation
                save_chat_message(user_id, message, reply, message_type)
                return reply
                
            except Exception as e:
                print(f"❌ OpenAI chat error: {e}")
        else:
            print(f"⚠️  OpenAI API key not available or invalid")
        
        # Final fallback
        fallback_reply = "I'm here to help with your fashion questions! Feel free to ask about styling advice, outfit coordination, or anything fashion-related."
        save_chat_message(user_id, message, fallback_reply, message_type)
        return fallback_reply
        
    except Exception as e:
        print(f"Chat processing error: {e}")
        return "I'm sorry, I'm having trouble processing your message right now. Please try again!"

def get_recommended_outfits_from_closet(user_id: int, occasion: str = None, weather: str = None) -> List[Dict[str, Any]]:
    """Get outfit recommendations based on user's closet items"""
    try:
        # Get user's closet items
        closet_items = get_user_images(user_id, limit=20)
        
        if not closet_items:
            return []
        
        # Analyze items and create outfit combinations
        outfits = []
        
        # Group items by category
        tops = []
        bottoms = []
        shoes = []
        accessories = []
        
        for item in closet_items:
            if item.get('analysis'):
                try:
                    analysis = json.loads(item['analysis'])
                    category = analysis.get('category', '').lower()
                    
                    if any(word in category for word in ['shirt', 'blouse', 'top', 'sweater', 'jacket', 'blazer']):
                        tops.append({
                            'item': item,
                            'analysis': analysis
                        })
                    elif any(word in category for word in ['pants', 'jeans', 'skirt', 'shorts', 'trousers']):
                        bottoms.append({
                            'item': item,
                            'analysis': analysis
                        })
                    elif any(word in category for word in ['shoes', 'boots', 'sneakers', 'heels', 'sandals']):
                        shoes.append({
                            'item': item,
                            'analysis': analysis
                        })
                    else:
                        accessories.append({
                            'item': item,
                            'analysis': analysis
                        })
                except:
                    continue
        
        # Create outfit combinations
        outfit_count = 0
        max_outfits = 5
        
        for top in tops[:3]:  # Limit to 3 tops
            for bottom in bottoms[:3]:  # Limit to 3 bottoms
                if outfit_count >= max_outfits:
                    break
                
                outfit = {
                    'id': outfit_count + 1,
                    'name': f"Outfit {outfit_count + 1}",
                    'items': [top['item'], bottom['item']],
                    'description': f"Pair {top['analysis'].get('item_name', 'top')} with {bottom['analysis'].get('item_name', 'bottom')}"
                }
                
                # Add shoes if available
                if shoes:
                    outfit['items'].append(shoes[outfit_count % len(shoes)]['item'])
                    outfit['description'] += f" and {shoes[outfit_count % len(shoes)]['analysis'].get('item_name', 'shoes')}"
                
                # Add accessories if available
                if accessories:
                    outfit['items'].append(accessories[outfit_count % len(accessories)]['item'])
                
                outfits.append(outfit)
                outfit_count += 1
        
        return outfits
        
    except Exception as e:
        print(f"Outfit recommendation error: {e}")
        return []

def get_chat_history(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Get user's chat history"""
    try:
        return get_chat_messages(user_id, limit)
    except Exception as e:
        print(f"Chat history error: {e}")
        return []

def clear_chat_history(user_id: int) -> bool:
    """Clear user's chat history"""
    try:
        # This would need to be implemented in database.py
        # For now, return True as placeholder
        return True
    except Exception as e:
        print(f"Clear chat history error: {e}")
        return False
