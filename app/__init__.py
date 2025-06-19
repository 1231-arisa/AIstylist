from flask import Flask
import os

def create_app():
    # Get the absolute path to the project root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(__name__,
                static_folder=os.path.join(root_dir, 'static'),
                template_folder=os.path.join(root_dir, 'templates'))
    
    # Ensure directories exist
    os.makedirs(app.static_folder, exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'css'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'js'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'images'), exist_ok=True)

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching during development
    
    # Import routes
    from app.routes import main
    app.register_blueprint(main)
    
    return app
