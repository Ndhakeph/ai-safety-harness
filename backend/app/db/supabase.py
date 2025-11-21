from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")

supabase: Client = create_client(url, key)

def get_supabase() -> Client:
    return supabase

def get_db() -> Client:
    return supabase

class SupabaseClient:
    def __init__(self):
        self.client = supabase
    
    def get_client(self) -> Client:
        return self.client
