import os
import sys

from dotenv import load_dotenv
load_dotenv(".env")
from dependencies import supabase

if __name__ == "__main__":
    try:
        url_data = supabase.storage.from_("medical_images").get_public_url("test.jpg")
        print(f"URL from SDK: {url_data}")
        print(f"Type: {type(url_data)}")
    except Exception as e:
        print(f"Error: {e}")
