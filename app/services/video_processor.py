from moviepy.editor import VideoFileClip
from groq import Groq
import re
import os

class VideoProcessor:
  def __init__(self, api_key):
    self.client = Groq(api_key=api_key)

  def extract_audio(self, video_file, audio_file='/data/input_audio.mp3'):
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

        Output format: "
        1. Timestamp: [start_time]-[end_time] seconds
          Insight: [description]
        2. Timestamp: [start_time]-[end_time] seconds
          Insight: [description]
        3. Timestamp: [start_time]-[end_time] seconds
          Insight: [description]
        "

        Prompt: "
          I have a video transcription and I need to identify the three moments with lasting duration's minimum is 70 seconds and maximum is 180 seconds and most insightful.
          The each result video's lasting duration's minimum is 70 seconds and maximum is 180 seconds .(This is the most important)

          If each result video's lasting duration is short of 70 seconds, please continue getting the correct result while you get all good result which video's lasting duration is large of 100 seconds. If each result video's lasting duration is not short of 100 seconds, output the correct formatted result.
          You can try 10 times. Please give me the best result one.
        "
      """
        
    completion = self.client.chat.completions.create(
      model="llama-3.2-90b-text-preview", messages=[{"role": "user", "content": prompt}], max_tokens=2048
    )

    insights_text = completion.choices[0].message.content
      
    return insights_text

  def parse_insights(self, insights_text):
    pattern = r"Timestamp: (\d+\.\d+)-(\d+\.\d+) seconds\s+Insight: (.+)"
    matches = re.findall(pattern, insights_text)
    
    return [{"start_time": float(m[0]), "end_time": float(m[1]), "description": m[2]} for m in matches]

  def _is_validate_videos(self, video_infoes, min_limit, max_limit):
    if len(video_infoes) != 3:
      return False
    
    # print("start")
    # for video_info in video_infoes:
    #   duration = video_info["end_time"] - video_info["start_time"]
    #   print(f'{video_info["end_time"]} --- {video_info["start_time"]} --- {duration}')
      
    #   # if duration < min_limit | duration > max_limit:
    #     # return False
    # print("end")
      
    return True
  
  
  def extract_clips(self, video_file, insights):
    video = VideoFileClip(video_file)
    for idx, insight in enumerate(insights):
      clip = video.subclip(insight['start_time'], insight['end_time'])
      clip_path = f"/data/clip_{idx + 1}.mp4"
      # Check if the file exists
      if os.path.exists(clip_path):
        os.remove(clip_path)
          
      clip.write_videofile(clip_path)
      