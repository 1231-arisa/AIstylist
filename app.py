from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import sqlite3
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE = 'items.db'
OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', 'YOUR_API_KEY_HERE')  # Replace with your API key or set as env var

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image TEXT NOT NULL,
        short_name TEXT NOT NULL,
        short_desc TEXT,
        long_desc TEXT
    )''')
    conn.commit()
    conn.close()

def insert_sample_items():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    sample_items = [
        ('20250612190908_images.jpg', 'Red Dress', 'A stylish red dress.', 'A beautiful, elegant red dress perfect for evening occasions.'),
        ('20250612191101_photo.jpg', 'Blue Jeans', 'Classic blue jeans.', 'Comfortable and durable blue jeans for everyday wear.'),
    ]
    for img, short, short_desc, long_desc in sample_items:
        c.execute('SELECT COUNT(*) FROM items WHERE image=?', (img,))
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO items (image, short_name, short_desc, long_desc) VALUES (?, ?, ?, ?)', (img, short, short_desc, long_desc))
    conn.commit()
    conn.close()

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            weather = data['weather'][0]['main']
            temp = data['main']['temp']
            return {'weather': weather, 'temp': temp}
        else:
            return None
    except Exception:
        return None

init_db()
insert_sample_items()

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/add_to_library')
def add_to_library():
    return render_template('add_to_library.html')

@app.route('/upload', methods=['POST'])
def upload():
    image = request.files.get('image')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    if image:
        filename = datetime.now().strftime('%Y%m%d%H%M%S_') + secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        return jsonify({'status': 'success', 'filename': filename, 'lat': lat, 'lon': lon})
    return jsonify({'status': 'error', 'message': 'No image uploaded'})

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_msg = request.form.get('message', '')
        # Placeholder AI response
        reply = f"I'm your AI Stylist! You said: {user_msg}"
        return jsonify({'reply': reply})
    return render_template('chat.html')

@app.route('/library_editor')
def library_editor():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, image, short_name, short_desc, long_desc FROM items')
    items = c.fetchall()
    conn.close()
    return render_template('library_editor.html', items=items)

@app.route('/suggestion', methods=['GET', 'POST'])
def suggestion():
    if request.method == 'POST':
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')
        weather_info = get_weather(lat, lon)
        # For demo: pick a random item from the DB as suggestion
        import random
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT image, short_name, short_desc FROM items ORDER BY RANDOM() LIMIT 1')
        row = c.fetchone()
        conn.close()
        if row:
            image_url = f"/static/uploads/{row[0]}"
            if weather_info:
                text = f"{row[1]}: {row[2]}\nWeather: {weather_info['weather']}, {weather_info['temp']}°C"
            else:
                text = f"{row[1]}: {row[2]}"
            return jsonify({'image': image_url, 'text': text})
        else:
            return jsonify({'image': '', 'text': 'No suggestion available.'})
    return render_template('suggestion.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
