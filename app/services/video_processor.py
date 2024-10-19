from moviepy.editor import VideoFileClip
from groq import Groq
import re
import os

class VideoProcessor:
  def __init__(self, api_key):
    self.client = Groq(api_key=api_key)

  def extract_audio(self, video_file, audio_file='input_audio.mp3'):
    video = VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file)
    return audio_file

  def transcribe_audio(self, audio_file):
    with open(audio_file, 'rb') as file:
      transcription = self.client.audio.transcriptions.create(
          file=(audio_file, file.read()), model="whisper-large-v3", response_format="verbose_json"
      )
    return self._parse_transcription(transcription.to_dict())

  def _parse_transcription(self, transcription_dict):
    if 'segments' not in transcription_dict:
        return None
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

  def get_insightful_moments(self, transcript):
    prompt = f"""
    Transcript:
    {transcript}
    Output format:
    1. Timestamp: [start_time]-[end_time] seconds
      Insight: [description]
    2. Timestamp: [start_time]-[end_time] seconds
      Insight: [description]
    """
    completion = self.client.chat.completions.create(
      model="llama-3.2-90b-text-preview", messages=[{"role": "user", "content": prompt}], max_tokens=2048
    )
    return completion.choices[0].message.content

  def parse_insights(self, insights_text):
    pattern = r"Timestamp: (\d+\.\d+)-(\d+\.\d+) seconds\s+Insight: (.+)"
    matches = re.findall(pattern, insights_text)
    return [{"start_time": float(m[0]), "end_time": float(m[1]), "description": m[2]} for m in matches]

  def extract_clips(self, video_file, insights):
    video = VideoFileClip(video_file)
    for idx, insight in enumerate(insights):
      clip = video.subclip(insight['start_time'], insight['end_time'])
      clip.write_videofile(f"clip_{idx + 1}.mp4")
