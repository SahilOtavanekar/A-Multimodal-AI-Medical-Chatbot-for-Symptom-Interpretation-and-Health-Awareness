import os
from supabase import create_client

url = "https://mhuhgozelxwgmtvugxsq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1odWhnb3plbHh3Z210dnVneHNxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0NDgxMjEsImV4cCI6MjA4ODAyNDEyMX0.Zt3rOoTaYQmGwhAql1660jLh7SnVcTgxQGIHh71xlRA"

# First get a token
client1 = create_client(url, key)
res = client1.auth.sign_in_with_password({
    "email": "sahilotavanekar29@gmail.com",
    "password": "s29122003@"
})
token = res.session.access_token

# Now simulate an API request with a COMPLETELY NEW client
client2 = create_client(url, key)
print("Testing get_user(token) with brand new client...")
try:
    user = client2.auth.get_user(token)
    print(f"SUCCESS: {user.user.email}")
except Exception as e:
    print(f"FAILED: {str(e)}")
