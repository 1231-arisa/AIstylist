
---
title: AI Stylist
emoji: 👔
colorFrom: indigo
colorTo: purple
sdk: docker
sdk_version: 28.1.1
app_port: 7860
app_file: run.py
pinned: false
---

# AI Stylist

An AI-powered personal stylist application built with Flask. This application helps users manage their virtual wardrobe and get personalized outfit recommendations.

https://https://aistylist_aistylist.hf.space/

## Features

- Virtual wardrobe management
- AI-powered outfit recommendations
- Interactive chat interface
- Responsive design with Tailwind CSS
- Dark/light mode support

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python run.py
```

## Docker Deployment

The application can be built and run using Docker:

```bash
docker build -t ai-stylist .
docker run -p 7860:7860 ai-stylist
```

Visit [http://localhost:7860](http://localhost:7860) to view the application.

## Deployment to Hugging Face Spaces

```shell
git remote add hf https://huggingface.co/spaces/AIstylist/AIstylist
git push -u hf flask:main
=======

#### Publish to HF Spaces

```shell
% git remote add hf https://huggingface.co/spaces/...  
% git push -u hf flask:main
```
