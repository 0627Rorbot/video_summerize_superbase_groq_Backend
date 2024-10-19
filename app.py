from app import create_app
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os

# Create log directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')
    
app = create_app()

# Enable CORS for all routes
CORS(app)

    
# Set up the log handler with rotation
file_handler = RotatingFileHandler('logs/flask_app.log', maxBytes=10240, backupCount=10)
file_handler.setLevel(logging.INFO)

# Define a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to app.logger
app.logger.addHandler(file_handler)


app.config['DEBUG'] = True

@app.route('/hello')
def index():
    app.logger.info('Home route accessed')
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
