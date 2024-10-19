from supabase import create_client, Client
import os
import logging

class SupabaseStorageManager:
  def __init__(self, supabase_url, supabase_key):
    self.supabase_url = supabase_url
    self.supabase_key = supabase_key
    self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

  def upload_video_to_bucket(self, bucket_name, video_path):
    video_name = os.path.basename(video_path)
    with open(video_path, 'rb') as video_file:
      return self.supabase.storage.from_(bucket_name).upload(file=video_file, path=video_name)

  def download_video_from_bucket(self, bucket_name, video_name, download_path):
    video_data = self.supabase.storage.from_(bucket_name).download(video_name)
    with open(download_path, 'wb') as download_file:
      download_file.write(video_data)

  def delete_video_on_bucket(self, bucket_name, video_name):
    return self.supabase.storage.from_(bucket_name).remove([video_name])
