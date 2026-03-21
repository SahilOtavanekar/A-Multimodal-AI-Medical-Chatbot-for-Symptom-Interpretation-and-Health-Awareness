import os
from supabase import create_client

url = "https://mhuhgozelxwgmtvugxsq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1odWhnb3plbHh3Z210dnVneHNxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0NDgxMjEsImV4cCI6MjA4ODAyNDEyMX0.Zt3rOoTaYQmGwhAql1660jLh7SnVcTgxQGIHh71xlRA"

supabase = create_client(url, key)

try:
    print("Signing in with credentials...")
    res = supabase.auth.sign_in_with_password({
        "email": "sahilotavanekar29@gmail.com",
        "password": "s29122003@"
    })
    token = res.session.access_token
    print(f"Logged in successfully. Token starts with: {token[:10]}...")
    
    print("Testing get_user(token) ...")
    user = supabase.auth.get_user(token)
    print(f"get_user SUCCESS: {user.user.id} - {user.user.email}")
except Exception as e:
    print(f"FAILED: {str(e)}")
