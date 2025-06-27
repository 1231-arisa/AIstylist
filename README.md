# AIstylist - AI-Powered Fashion Coordination

AIstylist is a project that automatically generates fashion outfit recommendations using AI. It leverages OpenAI's GPT-4o and DALL-E to generate stylish illustrations of avatars wearing your clothes.

## Features

- **Clothing Analysis**: Analyze clothing images in detail using GPT-4o
- **Style Selection**: Automatically select outfit combinations based on weather and occasion
- **Image Generation**: Generate stylish fashion illustrations using DALL-E
- **Web Application**: Intuitive UI for easy operation

## Setup

### Prerequisites
- Python 3.11+
- OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd AIstylist
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
# source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
Create a `.env` file and set your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Web Application (Recommended)

1. **Start the application**
```bash
python app.py
```

2. **Access in your browser**
```
http://127.0.0.1:5000
```

3. **Main Features**
   - **Upload Clothing**: Upload clothing images with the "Upload Clothing" button
   - **Generate Outfit**: Select weather and occasion to generate an outfit
   - **Closet Management**: View your uploaded clothing items

### Command Line (Legacy)

1. **Prepare clothing images**
   - Place images in the `data/clothes/input/` directory

2. **Run the pipeline**
```bash
python run_full_pipeline.py
```

### Individual Features

- **Clothing Analysis**: `python src/generate_item.py <image_path>`
- **Style Selection**: `python src/style_agent.py`
- **Image Generation**: `python src/generate_visualisation.py <avatar.txt> <clothing1.txt> <clothing2.txt>`

## Project Structure

```
AIstylist/
├── app.py                    # Main web application
├── data/
│   ├── avatar.txt            # Avatar description
│   └── clothes/input/        # Clothing images
├── src/
│   ├── generate_item.py      # Clothing analysis
│   ├── style_agent.py        # Style selection
│   └── generate_visualisation.py  # Image generation
├── templates/                # HTML templates
├── static/                   # CSS, JS, images
├── output/                   # Generated images
├── requirements.txt          # Main dependencies
└── run_full_pipeline.py      # Command line pipeline
```

## API Endpoints

### POST /upload
Upload and analyze a clothing image
- **Content-Type**: multipart/form-data
- **Parameters**: file (image file)
- **Response**: JSON analysis result

### POST /generate-outfit
Generate an outfit based on weather and occasion
- **Content-Type**: application/json
- **Parameters**: weather, occasion
- **Response**: URL of the generated image

### GET /closet
Get the contents of your closet
- **Response**: List of uploaded clothing items

## Dependencies

- Flask==3.0.0 - Web framework
- openai==1.92.2 - OpenAI API
- Pillow==11.2.1 - Image processing
- numpy==1.26.4 - Numerical computation

## Notes

- An OpenAI API key is required
- Image generation consumes API credits
- Generated images must comply with OpenAI's content policy
- Maximum upload image size is 16MB

## Troubleshooting

1. **API Key Error**
   - Make sure your `.env` file contains a valid API key
   - Ensure your API key has sufficient credits

2. **Image Generation Error**
   - Check that clothing descriptions are properly generated
   - Ensure you are not violating OpenAI's content policy

3. **Application Won't Start**
   - Make sure your virtual environment is activated
   - Ensure all dependencies are installed

## License

This project is licensed under the MIT License.

## ✨ Features

- 👗 **Personalized Outfit Suggestions**  
  Get AI-powered recommendations tailored to your preferences, body type, and occasion.
- 🛍️ **Virtual Wardrobe**  
  Upload your wardrobe and let AIstylist create new looks from your own clothes.
- 🎨 **Style Inspiration**  
  Discover trending styles and get inspired by curated looks.
- 📸 **Image-Based Recommendations**  
  Upload a photo and receive suggestions to enhance or complement your style.
- 🗣️ **Conversational Interface**  
  Chat with your AI stylist for instant advice and tips.

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AIstylist.git
   cd AIstylist
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**
   ```bash
   python app.py
   ```

## 🤖 Technologies Used

- Artificial Intelligence / Machine Learning
- Python
- Flask
- OpenAI API
- Gradio (for Hugging Face Spaces)

## 📄 License

This project is licensed under the MIT License.
