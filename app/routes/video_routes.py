from flask import Blueprint, request, jsonify
from app.controllers.video_controller import handle_video_upload, handle_video_processing
from flask_cors import CORS

video_bp = Blueprint('video_bp', __name__)

# Enable CORS for this Blueprint
CORS(video_bp)

# Route to upload video
@video_bp.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
      return jsonify({'error': 'No video file found'}), 400
    video_file = request.files['video']
    return handle_video_upload(video_file)

# Route to process the video and extract clips
@video_bp.route('/process', methods=['POST'])
def process_video():
    data = request.json
    video_name = data.get('video_name')
    if not video_name:
      return jsonify({'error': 'No video name provided'}), 400
    return handle_video_processing(video_name)
