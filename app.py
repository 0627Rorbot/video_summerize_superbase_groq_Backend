from app import create_app
from flask_cors import CORS

app = create_app()

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "https://video-summerize-superbase-groq-backend.onrender.com/"}})


app.config['DEBUG'] = True

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
