import os
from supabase import create_client, Client


class SupabaseClient:
    def __init__(self, url, key):
        try:
            self.supabase: Client = create_client(url, key)
        except Exception as e:
            print(f"ERROR. Error connecting to Supabase: {e}. You provided {url=}, {key=}")
            self.supabase = None
            
    def get_user_from_db(self, email):
        """Fetches user details from the 'users' table based on email."""
        try:
            response = self.supabase.table('authorized_users').select('*').eq('email', email).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching user from database: {e}")
            return None
            