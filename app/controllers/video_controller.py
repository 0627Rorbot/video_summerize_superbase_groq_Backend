from flask import jsonify
from app.services.supabase_manager import SupabaseStorageManager
from app.services.video_processor import VideoProcessor
import os

MOUNT_PATH = os.getenv("MOUNT_PATH")
if not os.path.exists(MOUNT_PATH):
  os.makedirs(MOUNT_PATH)
  print("Make Mount path")  # Logs an info level message
print("Mount path is Exists.")  # Logs an info level message
    
# Initialize managers with environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

storage_manager = SupabaseStorageManager(supabase_url, supabase_key)
video_processor = VideoProcessor(groq_api_key)

bucket_name = 'video_bucket'

def handle_video_upload(video_file):
  try:
    # Create directory if it does not exist
    os.makedirs('/data/uploads', exist_ok=True)
    
    # Save the uploaded video locally for processing
    video_path = os.path.join('/data/uploads', video_file.filename)
    video_file.save(video_path)

    # Upload to Supabase
    res = storage_manager.upload_video_to_bucket(bucket_name, video_path)
    
    return jsonify({'message': 'Video uploaded successfully', 'data': str(res)}), 200
  
  except Exception as e:
    return jsonify({'error': str(e)}), 500

def handle_video_processing(video_name):
  try:
    # Create directory if it does not exist
    os.makedirs('/data/downloads', exist_ok=True)
    
    # Download video from Supabase
    video_path = os.path.join('/data/downloads', video_name)
    storage_manager.download_video_from_bucket(bucket_name, video_name, video_path)

    if not os.path.exists(video_path):
      print(f"Video is downloaded, Path: {video_path}")  # Logs an info level message
    else:
      print(f"Video is not downloaded. Path: {video_path}")  # Logs an info level message
      
    audio_file='/data/input_audio.mp3'
    if os.path.exists(audio_file):
      os.remove(audio_file)
      print("Audio file is removed.")
    else:
      print("Audio file is not exists")
    # Extract audio and process insights
    audio_file = video_processor.extract_audio(video_path, audio_file)
    
    if not os.path.exists(audio_file):
      print(f"Audio is generated, Path: {audio_file}")  # Logs an info level message
    else:
      print(f"Audio is not generated. Path: {audio_file}")  # Logs an info level message
      
    if audio_file:
      transcript = video_processor.transcribe_audio(audio_file)
      print(f"Transcription: {transcript}")  # Logs an info level message
      
      
      if transcript:
        insights_text = video_processor.get_insightful_moments(transcript)
        print(f"Insights_text: {insights_text}")  # Logs an info level message
        
        if insights_text:
          insights = video_processor.parse_insights(insights_text)
          print(f"Insights: {insights}")  # Logs an info level message
          
          if insights:
            # Extract clips based on insights
            video_processor.extract_clips(video_path, insights)
            
            for idx, insight in enumerate(insights):
              clip = video.subclip(insight['start_time'], insight['end_time'])
              clip_path = f"/data/clip_{idx + 1}.mp4"
              # Check upload superbase
              res = storage_manager.upload_video_to_bucket(bucket_name, f"/data/{clip_path}")
              
            return jsonify({'message': 'Video processed successfully', 'insights': insights}), 200
          
    return jsonify({'error': 'Video processing failed'}), 500
  
  except Exception as e:
    
    return jsonify({'error': str(e)}), 500
