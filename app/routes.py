from flask import Blueprint, render_template, send_from_directory, current_app
import os

main = Blueprint('main', __name__)

@main.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(current_app.static_folder, filename)

# Data
outfits = [
    {
        "id": 1,
        "name": "Casual Chic",
        "weather": "Sunny, 72°F",
        "occasion": "Casual Day Out",
        "image": "/static/images/female-avatar.png"
    },
    {
        "id": 2,
        "name": "Office Ready",
        "weather": "Sunny, 72°F",
        "occasion": "Work Day",
        "image": "/static/images/female-avatar.png"
    },
    {
        "id": 3,
        "name": "Evening Casual",
        "weather": "Clear, 68°F",
        "occasion": "Dinner with Friends",
        "image": "/static/images/female-avatar.png"
    },
    {
        "id": 4,
        "name": "Weekend Comfort",
        "weather": "Partly Cloudy, 70°F",
        "occasion": "Weekend Errands",
        "image": "/static/images/female-avatar.png"
    }
]

categories = ["All", "Tops", "Bottoms", "Dresses", "Outerwear", "Shoes", "Accessories"]

closet_items = [
    {"id": 1, "name": "White Blouse", "category": "Tops", "color": "bg-[#FAFAFA]"},
    {"id": 2, "name": "Beige Sweater", "category": "Tops", "color": "bg-[#F5F0E8]"},
    {"id": 3, "name": "Gray Pants", "category": "Bottoms", "color": "bg-[#E8E8E8]"},
    {"id": 4, "name": "Pink Dress", "category": "Dresses", "color": "bg-[#E8D0D0]"},
    {"id": 5, "name": "Cream Skirt", "category": "Bottoms", "color": "bg-[#F5F0E8]"},
    {"id": 6, "name": "Taupe Blazer", "category": "Outerwear", "color": "bg-[#E8E0D5]"},
    {"id": 7, "name": "Nude Heels", "category": "Shoes", "color": "bg-[#F0E5D8]"},
    {"id": 8, "name": "Pearl Necklace", "category": "Accessories", "color": "bg-[#FAFAFA]"},
    {"id": 9, "name": "Beige Cardigan", "category": "Outerwear", "color": "bg-[#F5F0E8]"},
    {"id": 10, "name": "Gray Tee", "category": "Tops", "color": "bg-[#E8E8E8]"},
    {"id": 11, "name": "Blush Blouse", "category": "Tops", "color": "bg-[#E8D0D0]"},
    {"id": 12, "name": "Ivory Sweater", "category": "Tops", "color": "bg-[#FAFAFA]"}
]

@main.route('/')
def index():
    return render_template('home.html', 
                         outfits=outfits,
                         categories=categories,
                         closet_items=closet_items)
