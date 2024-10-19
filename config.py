import os

class Config:
  SUPABASE_URL = os.getenv("SUPABASE_URL")
  SUPABASE_KEY = os.getenv("SUPABASE_KEY")
  GROQ_API_KEY = os.getenv("GROQ_API_KEY")
