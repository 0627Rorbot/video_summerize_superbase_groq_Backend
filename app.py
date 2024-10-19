from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from moviepy.editor import VideoFileClip
import os
import re
import json
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("Supabase URL or API Key is missing.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class VideoProcessor:
    def extract_audio(self, video_file, audio_file='input_audio.mp3'):
        try:
            video = VideoFileClip(video_file)
            audio = video.audio
            audio.write_audiofile(audio_file)
            return audio_file
        except Exception as e:
            return None

    def transcribe_audio(self, audio_file):
        # Dummy transcription method for demonstration
        # In a real scenario, integrate Groq or another transcription service here
        transcription = {
            'segments': [
                {'text': 'This is the first segment.', 'start': 0, 'end': 5},
                {'text': 'This is the second segment.', 'start': 6, 'end': 10}
            ]
        }
        return self._parse_transcription(transcription)

    def _parse_transcription(self, transcription_dict):
        sentences_with_timestamps = []
        current_sentence = ""
        start_time = None

        for segment in transcription_dict['segments']:
            segment_text = segment['text'].strip()
            segment_start = segment['start']
            segment_end = segment['end']

            if not current_sentence:
                start_time = segment_start

            current_sentence += " " + segment_text

            if re.search(r'[.!?]$', segment_text):
                sentences_with_timestamps.append({
                    "start_time": start_time,
                    "end_time": segment_end,
                    "sentence": current_sentence.strip()
                })
                current_sentence = ""
                start_time = None

        return sentences_with_timestamps

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    file_path = f'uploads/{file.filename}'
    file.save(file_path)

    processor = VideoProcessor()
    audio_file = processor.extract_audio(file_path)

    if audio_file:
        transcript = processor.transcribe_audio(audio_file)
        return jsonify({'transcript': transcript})
    return jsonify({'error': 'Failed to extract audio'}), 500

@app.route('/download/<string:video_name>', methods=['GET'])
def download_video(video_name):
    bucket_name = 'video_bucket'
    try:
        data = supabase.storage.from_(bucket_name).download(video_name)
        video_path = f'temp/{video_name}'
        with open(video_path, 'wb') as f:
            f.write(data)
        return send_file(video_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
