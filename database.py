"""
Database module for AIstylist
Handles all database operations including user management, image storage, and chat messages
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'aistylist.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            name TEXT,
            subscription_type TEXT DEFAULT 'free',
            subscription_status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Uploaded images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            original_name TEXT,
            url TEXT,
            analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            reply TEXT,
            message_type TEXT DEFAULT 'text',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Outfits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outfits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            outfit_name TEXT,
            outfit_data TEXT,
            weather_condition TEXT,
            occasion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Collections table for avatar outfit photos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            collection_name TEXT,
            collection_type TEXT,
            avatar_image_url TEXT,
            outfit_description TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def create_user(email: str, name: str, subscription_type: str = 'free') -> int:
    """Create a new user and return user ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (email, name, subscription_type)
            VALUES (?, ?, ?)
        ''', (email, name, subscription_type))
        
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        # User already exists, get existing user ID
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        return result['id'] if result else None
    finally:
        conn.close()

def get_user_subscription(user_id: int) -> Dict[str, Any]:
    """Get user subscription information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT subscription_type, subscription_status, created_at, updated_at
        FROM users WHERE id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'subscription_type': result['subscription_type'],
            'subscription_status': result['subscription_status'],
            'created_at': result['created_at'],
            'updated_at': result['updated_at']
        }
    return None

def save_chat_message(user_id: int, message: str, reply: str, message_type: str = 'text') -> int:
    """Save chat message and reply"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chat_messages (user_id, message, reply, message_type)
        VALUES (?, ?, ?, ?)
    ''', (user_id, message, reply, message_type))
    
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return message_id

def get_chat_messages(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get chat messages for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, message, reply, message_type, created_at
        FROM chat_messages
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def save_uploaded_image(user_id: int, filename: str, original_name: str, url: str, analysis: str) -> int:
    """Save uploaded image information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO uploaded_images (user_id, filename, original_name, url, analysis)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, filename, original_name, url, analysis))
    
    image_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return image_id

def get_user_images(user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    """Get user's uploaded images"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, original_name, url, analysis, created_at
        FROM uploaded_images
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def save_outfit(user_id: int, outfit_name: str, outfit_data: str, weather_condition: str = None, occasion: str = None) -> int:
    """Save outfit recommendation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO outfits (user_id, outfit_name, outfit_data, weather_condition, occasion)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, outfit_name, outfit_data, weather_condition, occasion))
    
    outfit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return outfit_id

def get_user_outfits(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user's saved outfits"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, outfit_name, outfit_data, weather_condition, occasion, created_at
        FROM outfits
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def delete_uploaded_image(user_id: int, filename: str) -> bool:
    """Delete uploaded image from database and filesystem"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First get the file info to delete the actual file
        cursor.execute('''
            SELECT filename, url FROM uploaded_images 
            WHERE user_id = ? AND filename = ?
        ''', (user_id, filename))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        
        # Delete from database
        cursor.execute('''
            DELETE FROM uploaded_images
            WHERE user_id = ? AND filename = ?
        ''', (user_id, filename))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        # Delete the actual file from filesystem
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'data', 'clothes', 'input', filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {filename}: {e}")
        
        return deleted_count > 0
        
    except Exception as e:
        print(f"Error deleting image from database: {e}")
        conn.rollback()
        conn.close()
        return False

def update_user_subscription(user_id: int, subscription_type: str, subscription_status: str = 'active') -> bool:
    """Update user subscription"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users
        SET subscription_type = ?, subscription_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (subscription_type, subscription_status, user_id))
    
    updated_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return updated_count > 0

def save_collection(user_id: int, collection_name: str, collection_type: str, avatar_image_url: str, outfit_description: str, tags: str = "") -> int:
    """Save a new collection item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO collections (user_id, collection_name, collection_type, avatar_image_url, outfit_description, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, collection_name, collection_type, avatar_image_url, outfit_description, tags))
    
    collection_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return collection_id

def get_user_collections(user_id: int) -> List[Dict[str, Any]]:
    """Get all collections for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, collection_name, collection_type, avatar_image_url, outfit_description, tags, created_at
        FROM collections 
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    
    collections = []
    for row in cursor.fetchall():
        collections.append({
            'id': row['id'],
            'collection_name': row['collection_name'],
            'collection_type': row['collection_type'],
            'avatar_image_url': row['avatar_image_url'],
            'outfit_description': row['outfit_description'],
            'tags': row['tags'],
            'created_at': row['created_at']
        })
    
    conn.close()
    return collections

def delete_collection(user_id: int, collection_id: int) -> bool:
    """Delete a collection item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM collections
        WHERE user_id = ? AND id = ?
    ''', (user_id, collection_id))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_count > 0

def cache_weather(location: str, weather_data: Dict[str, Any]) -> None:
    """Cache weather data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create weather cache table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            location TEXT PRIMARY KEY,
            weather_data TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert or update weather data
    cursor.execute('''
        INSERT OR REPLACE INTO weather_cache (location, weather_data)
        VALUES (?, ?)
    ''', (location, json.dumps(weather_data)))
    
    conn.commit()
    conn.close()

def get_cached_weather(location: str, max_age_hours: int = 1) -> Optional[Dict[str, Any]]:
    """Get cached weather data if it's not too old"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create weather cache table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            location TEXT PRIMARY KEY,
            weather_data TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Get cached data
    cursor.execute('''
        SELECT weather_data, cached_at
        FROM weather_cache
        WHERE location = ?
    ''', (location,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    # Check if cache is still valid (within max_age_hours)
    cached_at = datetime.fromisoformat(result['cached_at'])
    age_hours = (datetime.now() - cached_at).total_seconds() / 3600
    
    if age_hours > max_age_hours:
        return None
    
    return json.loads(result['weather_data'])

def clear_weather_cache(location: str = None) -> None:
    """Clear weather cache for a specific location or all locations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if location:
        cursor.execute('DELETE FROM weather_cache WHERE location = ?', (location,))
    else:
        cursor.execute('DELETE FROM weather_cache')
    
    conn.commit()
    conn.close()
