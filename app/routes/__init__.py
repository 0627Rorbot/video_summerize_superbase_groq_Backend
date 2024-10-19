from .video_routes import video_bp

def register_routes(app):
  app.register_blueprint(video_bp)
