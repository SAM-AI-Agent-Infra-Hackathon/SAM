"""
Data service module for querying Supabase tables.

This module provides both synchronous and asynchronous functions for fetching
joined data from lca_filings and lca_worksites tables. Designed to be easily
integrated with LangChain/LangGraph for AI-powered data querying.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from supabase import Client

from ..config.supabase_client import get_client

# Configure logging
logger = logging.getLogger(__name__)


class DataService:
    """Service class for handling data operations with Supabase."""
    
    def __init__(self, client: Optional[Client] = None):
        """
        Initialize the data service.
        
        Args:
            client: Optional Supabase client. If None, uses the global client.
        """
        self.client = client or get_client()
    
    def get_sample_joined_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch joined data from lca_filings and lca_worksites tables.
        
        This function executes a JOIN query to combine filing information
        with worksite details based on case_number.
        
        Args:
            limit: Maximum number of records to return (default: 10)
            
        Returns:
            List of dictionaries containing joined data
            
        Raises:
            Exception: If the query fails
        """
        try:
            logger.info(f"Fetching joined data with limit: {limit}")
            
            # Execute the JOIN query
            response = self.client.rpc(
                'get_joined_lca_data',
                {'record_limit': limit}
            )
            
            # If RPC function doesn't exist, fall back to raw SQL
            if not response.data:
                logger.info("RPC function not found, using raw query")
                response = self.client.from_('lca_filings') \
                    .select('''
                        case_number,
                        employer_name,
                        job_title,
                        lca_worksites!inner(
                            worksite_city,
                            prevailing_wage
                        )
                    ''') \
                    .limit(limit) \
                    .execute()
                
                # Flatten the nested structure
                flattened_data = []
                for record in response.data:
                    for worksite in record.get('lca_worksites', []):
                        flattened_data.append({
                            'case_number': record['case_number'],
                            'employer_name': record['employer_name'],
                            'job_title': record['job_title'],
                            'worksite_city': worksite['worksite_city'],
                            'prevailing_wage': worksite['prevailing_wage']
                        })
                
                logger.info(f"Successfully fetched {len(flattened_data)} joined records")
                return flattened_data
            
            logger.info(f"Successfully fetched {len(response.data)} joined records")
            return response.data
            
        except Exception as e:
            logger.error(f"Error fetching joined data: {e}")
            raise
    
    async def get_sample_joined_data_async(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Asynchronously fetch joined data from lca_filings and lca_worksites tables.
        
        This is the async version of get_sample_joined_data, suitable for use
        in async contexts like LangChain/LangGraph agent loops.
        
        Args:
            limit: Maximum number of records to return (default: 10)
            
        Returns:
            List of dictionaries containing joined data
            
        Raises:
            Exception: If the query fails
        """
        try:
            logger.info(f"Async fetching joined data with limit: {limit}")
            
            # Run the synchronous query in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.get_sample_joined_data, 
                limit
            )
            
            logger.info(f"Successfully fetched {len(result)} joined records (async)")
            return result
            
        except Exception as e:
            logger.error(f"Error in async fetch: {e}")
            raise
    
    def execute_custom_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a custom SQL query against the database.
        
        This method is designed for future integration with AI agents that
        might generate custom queries based on natural language input.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Query results as list of dictionaries
            
        Raises:
            Exception: If the query fails
        """
        try:
            logger.info(f"Executing custom query: {query[:100]}...")
            
            if params:
                response = self.client.rpc('execute_query', {'sql_query': query, 'query_params': params})
            else:
                response = self.client.rpc('execute_query', {'sql_query': query})
            
            logger.info(f"Custom query executed successfully, returned {len(response.data)} records")
            return response.data
            
        except Exception as e:
            logger.error(f"Error executing custom query: {e}")
            raise
    
    async def execute_custom_query_async(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Asynchronously execute a custom SQL query against the database.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Query results as list of dictionaries
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.execute_custom_query, 
                query, 
                params
            )
            return result
        except Exception as e:
            logger.error(f"Error in async custom query: {e}")
            raise


# Convenience functions for direct usage
def get_sample_joined_data(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to fetch joined data using the default client.
    
    Args:
        limit: Maximum number of records to return (default: 10)
        
    Returns:
        List of dictionaries containing joined data
    """
    service = DataService()
    return service.get_sample_joined_data(limit)


async def get_sample_joined_data_async(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience async function to fetch joined data using the default client.
    
    Args:
        limit: Maximum number of records to return (default: 10)
        
    Returns:
        List of dictionaries containing joined data
    """
    service = DataService()
    return await service.get_sample_joined_data_async(limit)
