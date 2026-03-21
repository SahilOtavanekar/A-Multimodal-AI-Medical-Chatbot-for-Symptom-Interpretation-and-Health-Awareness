import os
import requests
from supabase import create_client

url = "https://mhuhgozelxwgmtvugxsq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1odWhnb3plbHh3Z210dnVneHNxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0NDgxMjEsImV4cCI6MjA4ODAyNDEyMX0.Zt3rOoTaYQmGwhAql1660jLh7SnVcTgxQGIHh71xlRA"

supabase = create_client(url, key)
res = supabase.auth.sign_in_with_password({
    "email": "sahilotavanekar29@gmail.com",
    "password": "s29122003@"
})
token = res.session.access_token

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "message": "hello",
    "session_id": None,
    "image_url": None
}

# POST to Render
print("Sending POST request to Render with brand new token...")
render_url = "https://a-multimodal-ai-medical-chatbot-for.onrender.com/api/chat/"
resp = requests.post(render_url, json=payload, headers=headers)
print("Render response:", resp.status_code)
print(resp.text)
