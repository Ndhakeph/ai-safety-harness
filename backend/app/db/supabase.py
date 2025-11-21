"""Supabase client configuration and initialization."""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    """Singleton Supabase client manager."""

    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance.

        Returns:
            Supabase client instance

        Raises:
            ValueError: If required environment variables are missing
        """
        if cls._instance is None:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
                )

            cls._instance = create_client(supabase_url, supabase_key)

        return cls._instance


def get_db() -> Client:
    """Dependency function to get Supabase client.

    Returns:
        Supabase client instance
    """
    return SupabaseClient.get_client()
