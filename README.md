# AIstylist - AI-Powered Fashion Coordination

AIstylist is an intelligent fashion assistant that automatically generates personalized outfit recommendations using AI. It leverages OpenAI's GPT-4o and DALL-E to analyze your clothing and create stylish outfit combinations based on weather, occasion, and personal style.

## ✨ Key Features

- 🧠 **AI-Powered Analysis**: Analyze clothing images in detail using GPT-4o
- 🌤️ **Weather-Aware Styling**: Generate outfits based on real-time weather conditions
- 🎨 **Smart Color Coordination**: Intelligent layering and color harmony
- 📱 **Mobile-Optimized**: iPhone-friendly interface with camera integration
- 💬 **Chat Interface**: Conversational AI stylist for instant advice
- 🛍️ **Virtual Wardrobe**: Upload and manage your clothing collection
- 💳 **Payment Integration**: Stripe-powered subscription system
- 🎯 **Personalized Recommendations**: Tailored suggestions based on your style

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API Key
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/1231-arisa/AIstylist.git
cd AIstylist
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_api_key_here
```

5. **Run the application**
```bash
python app.py
```

6. **Access the app**
- Local: `http://127.0.0.1:8080`
- Mobile: `http://[YOUR_IP]:8080`

## 📱 Mobile Usage (iPhone)

1. **Connect to the same Wi-Fi network** as your computer
2. **Open Safari** and navigate to `http://[YOUR_IP]:8080`
3. **Disable HTTPS upgrade** in Safari settings:
   - Settings → Safari → Advanced → Experimental Features
   - Turn off "HTTPS Upgrade"

## 🎯 Main Features

### Virtual Wardrobe
- Upload clothing items via camera or photo library
- Automatic categorization (Tops, Bottoms, Dresses, Shoes, Accessories)
- Smart item naming and analysis
- Category-based filtering and search

### AI Outfit Generation
- Weather-based recommendations
- Layering suggestions (base + outer layers)
- Color coordination and harmony
- Occasion-appropriate styling

### Chat Interface
- Upload photos for instant styling advice
- Ask questions about outfit combinations
- Get personalized recommendations
- Natural language interaction

### Weather Integration
- Real-time weather data
- Automatic outfit adjustments
- Weather-appropriate suggestions
- 5-minute cache updates

## 🏗️ Project Structure

```
AIstylist/
├── app.py                    # Main Flask application
├── database.py               # Database operations
├── chat_service.py           # AI chat functionality
├── weather_service.py        # Weather data integration
├── payment_service.py        # Stripe payment processing
├── src/
│   ├── style_agent.py        # Outfit selection logic
│   ├── generate_item.py      # Clothing analysis
│   └── generate_visualisation.py  # Image generation
├── templates/
│   ├── home.html            # Main application interface
│   ├── landing.html         # Landing page
│   └── payment_*.html       # Payment pages
├── data/
│   ├── clothes/input/        # Uploaded clothing images
│   └── avatar.txt           # Avatar description
├── cache/                   # Weather and API cache
├── output/                  # Generated outfit images
└── requirements.txt         # Python dependencies
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - Main application interface
- `POST /upload` - Upload and analyze clothing
- `POST /generate-outfit` - Generate outfit recommendations
- `GET /closet` - Get wardrobe contents
- `POST /chat` - AI chat interface

### Utility Endpoints
- `GET /weather` - Get weather information
- `POST /payment` - Process payments
- `GET /health` - Health check

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **AI/ML**: OpenAI GPT-4o, DALL-E
- **Database**: SQLite
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Payments**: Stripe
- **Image Processing**: Pillow, pillow-heif
- **Weather**: OpenWeatherMap API

## 📦 Dependencies

- Flask==3.0.0 - Web framework
- openai==1.92.2 - OpenAI API integration
- Pillow==11.2.1 - Image processing
- pillow-heif==0.16.0 - HEIC/HEIF support
- apscheduler==3.10.4 - Task scheduling
- requests==2.31.0 - HTTP requests
- python-dotenv==1.0.0 - Environment variables

## 🔧 Configuration

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
WEATHER_API_KEY=your_weather_api_key
```

### Database
The application uses SQLite for data storage. The database file (`aistylist.db`) is created automatically on first run.

## 🚨 Troubleshooting

### Common Issues

1. **App won't start**
   - Ensure virtual environment is activated
   - Check all dependencies are installed
   - Verify Python version (3.11+)

2. **API Key errors**
   - Verify `.env` file exists and contains valid API key
   - Check API key has sufficient credits
   - Ensure no extra spaces in API key

3. **Mobile access issues**
   - Confirm both devices are on same Wi-Fi
   - Check firewall settings
   - Disable HTTPS upgrade in Safari

4. **Image upload problems**
   - Verify image format is supported (JPG, PNG, HEIC)
   - Check file size (max 16MB)
   - Ensure stable internet connection

5. **Weather data not updating**
   - Check internet connection
   - Verify weather API key
   - Clear cache if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o and DALL-E APIs
- Stripe for payment processing
- OpenWeatherMap for weather data
- The open-source community for various libraries

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Made with ❤️ for fashion enthusiasts**