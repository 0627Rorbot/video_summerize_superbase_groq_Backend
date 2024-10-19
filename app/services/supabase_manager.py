from supabase import create_client, Client
import os
import logging

class SupabaseStorageManager:
  def __init__(self, supabase_url, supabase_key):
    self.supabase_url = supabase_url
    self.supabase_key = supabase_key
    self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

  def _get_uploaded_videos(self, bucket_name: str):
    """Helper method to retrieve the list of videos from the bucket."""
    try:
      logging.info(f"Retrieving file list from bucket: {bucket_name}")
      return self.supabase.storage.from_(bucket_name).list()
    except Exception as e:
      logging.error(f"Failed to retrieve videos from bucket {bucket_name}: {e}")
      raise

  def upload_video_to_bucket(self, bucket_name, video_path):
    video_name = os.path.basename(video_path)
    try:
      uploaded_videos = self._get_uploaded_videos(bucket_name)
      video_exists = any(video['name'] == video_name for video in uploaded_videos)

      with open(video_path, 'rb') as video_file:
        if video_exists:
          # Update the video if it exists
          logging.info(f"Video '{video_name}' already exists in '{bucket_name}', updating.")
          return self.supabase.storage.from_(bucket_name).update(file=video_file, path=video_name, file_options={"content-type": "video/mp4"})
        
        else:
          # Upload the video if it doesn't exist
          logging.info(f"Uploading video '{video_name}' to bucket '{bucket_name}'.")
          return self.supabase.storage.from_(bucket_name).upload(file=video_file, path=video_name, file_options={"content-type": "video/mp4"})
      
    except FileNotFoundError:
      logging.error(f"Video file not found at path: {video_path}")
      raise
    
    except Exception as e:
      logging.error(f"An error occurred while uploading video '{video_name}': {e}")
      raise

  def download_video_from_bucket(self, bucket_name, video_name, download_path):
    video_data = self.supabase.storage.from_(bucket_name).download(video_name)
    with open(download_path, 'wb') as download_file:
      download_file.write(video_data)

  def delete_video_on_bucket(self, bucket_name, video_name):
    return self.supabase.storage.from_(bucket_name).remove([video_name])
