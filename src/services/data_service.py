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

from config.supabase_client import get_client

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
            
            # Use the select query with inner join syntax
            response = self.client.from_('lca_filings') \
                .select('''
                    case_number,
                    employer_name,
                    job_title,
                    visa_class,
                    lca_worksites!inner(
                        worksite_city,
                        worksite_state,
                        prevailing_wage
                    )
                ''') \
                .limit(limit) \
                .execute()
            
            # Flatten the nested structure from the join
            flattened_data = []
            for record in response.data:
                worksites = record.get('lca_worksites', [])
                if worksites:
                    for worksite in worksites:
                        flattened_data.append({
                            'case_number': record['case_number'],
                            'company': record['employer_name'],
                            'job_title': record['job_title'],
                            'city': worksite['worksite_city'],
                            'state': worksite.get('worksite_state'),
                            'wage': worksite['prevailing_wage'] if worksite['prevailing_wage'] is not None else 0.0,
                            'visa_class': record.get('visa_class', 'H-1B')
                        })
                else:
                    # Handle case where there are no worksites (shouldn't happen with inner join)
                    flattened_data.append({
                        'case_number': record['case_number'],
                        'company': record['employer_name'],
                        'job_title': record['job_title'],
                        'city': None,
                        'state': None,
                        'wage': 0.0,
                        'visa_class': record.get('visa_class', 'H-1B')
                    })
            
            logger.info(f"Successfully fetched {len(flattened_data)} joined records")
            return flattened_data
            
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

    # Filtering Query Methods
    
    def get_filings_by_city(self, city: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch LCA filings filtered by worksite city.
        
        Args:
            city: City name to filter by (case-insensitive)
            limit: Maximum number of records to return (default: 50)
            
        Returns:
            List of dictionaries containing joined data for the specified city
            
        Raises:
            Exception: If the query fails
        """
        try:
            logger.info(f"Fetching filings for city: {city} with limit: {limit}")
            
            response = self.client.from_('lca_filings') \
                .select('''
                    case_number,
                    employer_name,
                    job_title,
                    visa_class,
                    lca_worksites!inner(
                        worksite_city,
                        worksite_state,
                        prevailing_wage
                    )
                ''') \
                .filter('lca_worksites.worksite_city', 'ilike', f'%{city}%') \
                .limit(limit) \
                .execute()
            
            # Flatten the nested structure
            flattened_data = []
            for record in response.data:
                worksites = record.get('lca_worksites', [])
                for worksite in worksites:
                    # Only include worksites that match the city filter
                    if city.lower() in worksite['worksite_city'].lower():
                        flattened_data.append({
                            'case_number': record['case_number'],
                            'company': record['employer_name'],
                            'job_title': record['job_title'],
                            'city': worksite['worksite_city'],
                            'state': worksite.get('worksite_state'),
                            'wage': worksite['prevailing_wage'] if worksite['prevailing_wage'] is not None else 0.0,
                            'visa_class': record.get('visa_class', 'H-1B')
                        })
            
            logger.info(f"Successfully fetched {len(flattened_data)} filings for city: {city}")
            return flattened_data
            
        except Exception as e:
            logger.error(f"Error fetching filings by city {city}: {e}")
            raise

    def get_high_wage_jobs(self, min_wage: float, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch LCA filings with prevailing wage above the specified minimum.
        
        Args:
            min_wage: Minimum prevailing wage threshold
            limit: Maximum number of records to return (default: 50)
            
        Returns:
            List of dictionaries containing high-wage job filings
            
        Raises:
            Exception: If the query fails
        """
        try:
            logger.info(f"Fetching high wage jobs above ${min_wage:,.2f} with limit: {limit}")
            
            # Remove the problematic order() call and fetch more records to sort later
            response = self.client.from_('lca_filings') \
                .select('''
                    case_number,
                    employer_name,
                    job_title,
                    visa_class,
                    lca_worksites!inner(
                        worksite_city,
                        worksite_state,
                        prevailing_wage
                    )
                ''') \
                .filter('lca_worksites.prevailing_wage', 'gte', min_wage) \
                .limit(limit * 2) \
                .execute()
            
            # Flatten the nested structure
            flattened_data = []
            for record in response.data:
                worksites = record.get('lca_worksites', [])
                for worksite in worksites:
                    # Only include worksites with wage >= min_wage (double-check filtering)
                    wage_value = worksite['prevailing_wage'] if worksite['prevailing_wage'] is not None else 0.0
                    logger.debug(f"Checking wage: {wage_value} >= {min_wage} = {wage_value >= min_wage}")
                    if wage_value >= min_wage:
                        flattened_data.append({
                            'case_number': record['case_number'],
                            'company': record['employer_name'],
                            'job_title': record['job_title'],
                            'city': worksite['worksite_city'],
                            'state': worksite.get('worksite_state'),
                            'wage': wage_value,
                            'visa_class': record.get('visa_class', 'H-1B')
                        })
            
            # Sort by wage descending and limit results
            flattened_data.sort(key=lambda x: x['wage'], reverse=True)
            flattened_data = flattened_data[:limit]
            
            logger.info(f"Successfully fetched {len(flattened_data)} high wage jobs above ${min_wage:,.2f}")
            return flattened_data
            
        except Exception as e:
            logger.error(f"Error fetching high wage jobs above ${min_wage}: {e}")
            raise

    def get_jobs_by_company(self, company: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch LCA filings filtered by employer/company name.
        
        Args:
            company: Company name to filter by (case-insensitive partial match)
            limit: Maximum number of records to return (default: 50)
            
        Returns:
            List of dictionaries containing filings for the specified company
            
        Raises:
            Exception: If the query fails
        """
        try:
            logger.info(f"Fetching jobs for company: {company} with limit: {limit}")
            
            response = self.client.from_('lca_filings') \
                .select('''
                    case_number,
                    employer_name,
                    job_title,
                    visa_class,
                    lca_worksites!inner(
                        worksite_city,
                        worksite_state,
                        prevailing_wage
                    )
                ''') \
                .filter('employer_name', 'ilike', f'%{company}%') \
                .limit(limit) \
                .execute()
            
            # Flatten the nested structure
            flattened_data = []
            for record in response.data:
                worksites = record.get('lca_worksites', [])
                for worksite in worksites:
                    flattened_data.append({
                        'case_number': record['case_number'],
                        'employer_name': record['employer_name'],
                        'job_title': record['job_title'],
                        'worksite_city': worksite['worksite_city'],
                        'prevailing_wage': worksite['prevailing_wage']
                    })
            
            logger.info(f"Successfully fetched {len(flattened_data)} jobs for company: {company}")
            return flattened_data
            
        except Exception as e:
            logger.error(f"Error fetching jobs by company {company}: {e}")
            raise

    def get_jobs_by_title(self, title: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch LCA filings filtered by job title.
        
        Args:
            title: Job title to filter by (case-insensitive partial match)
            limit: Maximum number of records to return (default: 50)
            
        Returns:
            List of dictionaries containing filings with matching job titles
            
        Raises:
            Exception: If the query fails
        """
        try:
            logger.info(f"Fetching jobs with title: {title} with limit: {limit}")
            
            response = self.client.from_('lca_filings') \
                .select('''
                    case_number,
                    employer_name,
                    job_title,
                    visa_class,
                    lca_worksites!inner(
                        worksite_city,
                        worksite_state,
                        prevailing_wage
                    )
                ''') \
                .filter('job_title', 'ilike', f'%{title}%') \
                .limit(limit) \
                .execute()
            
            # Flatten the nested structure
            flattened_data = []
            for record in response.data:
                worksites = record.get('lca_worksites', [])
                for worksite in worksites:
                    flattened_data.append({
                        'case_number': record['case_number'],
                        'employer_name': record['employer_name'],
                        'job_title': record['job_title'],
                        'worksite_city': worksite['worksite_city'],
                        'prevailing_wage': worksite['prevailing_wage']
                    })
            
            logger.info(f"Successfully fetched {len(flattened_data)} jobs with title: {title}")
            return flattened_data
            
        except Exception as e:
            logger.error(f"Error fetching jobs by title {title}: {e}")
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
