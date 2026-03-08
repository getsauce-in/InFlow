import os
import httpx

SUPABASE_URL = "https://xprhqtavwhaloxpumkuz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhwcmhxdGF2d2hhbG94cHVta3V6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5ODc4MDYsImV4cCI6MjA4ODU2MzgwNn0.l3j4xVEPb8SfsT1Qbp6dAztktX3vv8Cgbh6wEaKl3cY"

def get_supabase_headers() -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates" # For upserts
    }

