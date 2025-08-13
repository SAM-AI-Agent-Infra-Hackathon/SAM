"""
Supabase client configuration module.

This module handles the initialization and configuration of the Supabase client
using environment variables for secure credential management.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseConfig:
    """Configuration class for Supabase client."""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.service_role_key:
            raise ValueError(
                "Missing required environment variables: SUPABASE_URL and/or SUPABASE_SERVICE_ROLE_KEY. "
                "Please check your .env file."
            )


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    
    Returns:
        Client: Configured Supabase client
        
    Raises:
        ValueError: If required environment variables are missing
        Exception: If client creation fails
    """
    try:
        config = SupabaseConfig()
        client = create_client(config.url, config.service_role_key)
        logger.info("Supabase client initialized successfully")
        return client
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise


# Global client instance (lazy initialization)
_client: Optional[Client] = None


def get_client() -> Client:
    """
    Get the global Supabase client instance (singleton pattern).
    
    Returns:
        Client: Supabase client instance
    """
    global _client
    if _client is None:
        _client = get_supabase_client()
    return _client
