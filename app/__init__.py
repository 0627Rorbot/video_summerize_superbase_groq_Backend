from flask import Flask
from .routes import register_routes
from dotenv import load_dotenv
import os

def create_app():
  app = Flask(__name__)
  
  # Load environment variables
  load_dotenv()
  
  # Load configuration from config.py
  app.config.from_object('config.Config')

  # Register routes (blueprints)
  register_routes(app)

  return app
