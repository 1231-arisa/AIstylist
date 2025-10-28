---
title: AIstylist - AI Fashion Assistant
emoji: 👗
colorFrom: pink
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# AIstylist - AI-Powered Fashion Assistant

AIstylist is an intelligent fashion assistant that automatically generates personalized outfit recommendations using AI. It leverages OpenAI's GPT-4o to analyze your clothing and create stylish outfit combinations based on weather, occasion, and personal style.

## ✨ Key Features

- 🧠 **AI-Powered Analysis**: Analyze clothing images in detail using GPT-4o
- 🌤️ **Weather-Aware Styling**: Generate outfits based on real-time weather conditions
- 🎨 **Smart Color Coordination**: Intelligent layering and color harmony
- 📱 **Mobile-Optimized**: iPhone-friendly interface with camera integration
- 💬 **Chat Interface**: Conversational AI stylist for instant advice
- 🛍️ **Virtual Wardrobe**: Upload and manage your clothing collection
- 🎯 **Personalized Recommendations**: Tailored suggestions based on your style

## 🚀 How to Use

1. **Upload Your Clothes**: Take photos or upload images of your clothing items
2. **Get AI Analysis**: Each item is analyzed for color, style, category, and material
3. **Receive Recommendations**: Get personalized outfit suggestions based on weather and occasion
4. **Chat with AI**: Ask for styling advice and get instant responses
5. **Build Your Wardrobe**: Create a virtual closet of all your fashion items

## 🔧 Setup

### Environment Variables

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

### Required API Keys

- **OpenAI API Key**: For GPT-4o image analysis and chat functionality
- **Weather API Key**: For weather-based outfit recommendations (optional)

## 📱 Mobile Features

- Camera integration for easy clothing uploads
- Touch-optimized interface
- Responsive design for all screen sizes
- HEIC/HEIF image format support

## 🎨 Outfit Generation

The app generates outfits based on:
- **Weather conditions** (temperature, rain, sun)
- **Occasion types** (Casual, Business, Formal, etc.)
- **Your existing wardrobe**
- **Color coordination principles**
- **Style preferences**

## 💬 AI Chat Features

- Upload clothing images for instant analysis
- Get styling advice and recommendations
- Ask questions about fashion and styling
- Receive personalized outfit suggestions

## 🛠️ Technical Details

- **Backend**: Flask (Python)
- **AI Model**: OpenAI GPT-4o
- **Image Processing**: Pillow, pillow-heif
- **Database**: SQLite
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS
- **Deployment**: Hugging Face Spaces

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Note**: This is a demo version for Hugging Face Spaces. Some features may be limited compared to the full version.
