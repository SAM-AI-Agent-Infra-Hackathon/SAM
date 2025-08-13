"""
LangChain Tools for LCA Data Querying

This module wraps the DataService filtering methods as LangChain Tools,
making them available for AI agents to use in natural language workflows.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain.tools import tool

from services.data_service import DataService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the global data service instance
data_service = DataService()


@tool
def get_filings_by_city(city: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch LCA filings filtered by worksite city.
    
    Args:
        city: City name to filter by (case-insensitive partial match)
        limit: Maximum number of records to return (default: 50)
        
    Returns:
        List of dictionaries with keys: case_number, company, job_title, city, state, wage, visa_class
        
    Example:
        get_filings_by_city("San Francisco", 25)
    """
    try:
        logger.info(f"LangChain tool: Fetching filings for city: {city}")
        results = data_service.get_filings_by_city(city, limit)
        logger.info(f"LangChain tool: Found {len(results)} filings for city: {city}")
        return results
    except Exception as e:
        logger.error(f"LangChain tool error in get_filings_by_city: {e}")
        return []


@tool
def get_high_wage_jobs(min_wage: float, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch LCA filings with prevailing wage above the specified minimum.
    Results are sorted by wage in descending order.
    
    Args:
        min_wage: Minimum prevailing wage threshold (in USD)
        limit: Maximum number of records to return (default: 50)
        
    Returns:
        List of dictionaries with keys: case_number, company, job_title, city, state, wage, visa_class
        
    Example:
        get_high_wage_jobs(120000.0, 20)
    """
    try:
        logger.info(f"LangChain tool: Fetching high wage jobs above ${min_wage:,.2f}")
        results = data_service.get_high_wage_jobs(min_wage, limit)
        logger.info(f"LangChain tool: Found {len(results)} high wage jobs above ${min_wage:,.2f}")
        return results
    except Exception as e:
        logger.error(f"LangChain tool error in get_high_wage_jobs: {e}")
        return []


@tool
def get_jobs_by_company(company: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch LCA filings filtered by employer/company name.
    
    Args:
        company: Company name to filter by (case-insensitive partial match)
        limit: Maximum number of records to return (default: 50)
        
    Returns:
        List of dictionaries with keys: case_number, company, job_title, city, state, wage, visa_class
        
    Example:
        get_jobs_by_company("Google", 30)
    """
    try:
        logger.info(f"LangChain tool: Fetching jobs for company: {company}")
        results = data_service.get_jobs_by_company(company, limit)
        logger.info(f"LangChain tool: Found {len(results)} jobs for company: {company}")
        return results
    except Exception as e:
        logger.error(f"LangChain tool error in get_jobs_by_company: {e}")
        return []


@tool
def get_jobs_by_title(title: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch LCA filings filtered by job title.
    
    Args:
        title: Job title to filter by (case-insensitive partial match)
        limit: Maximum number of records to return (default: 50)
        
    Returns:
        List of dictionaries with keys: case_number, company, job_title, city, state, wage, visa_class
        
    Example:
        get_jobs_by_title("Software Engineer", 40)
    """
    try:
        logger.info(f"LangChain tool: Fetching jobs with title: {title}")
        results = data_service.get_jobs_by_title(title, limit)
        logger.info(f"LangChain tool: Found {len(results)} jobs with title: {title}")
        return results
    except Exception as e:
        logger.error(f"LangChain tool error in get_jobs_by_title: {e}")
        return []


@tool
def get_sample_joined_data(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch a sample of joined LCA filings and worksite data.
    
    Args:
        limit: Maximum number of records to return (default: 10)
        
    Returns:
        List of dictionaries with keys: case_number, company, job_title, city, state, wage, visa_class
        
    Example:
        get_sample_joined_data(15)
    """
    try:
        logger.info(f"LangChain tool: Fetching sample joined data with limit: {limit}")
        results = data_service.get_sample_joined_data(limit)
        logger.info(f"LangChain tool: Found {len(results)} sample records")
        return results
    except Exception as e:
        logger.error(f"LangChain tool error in get_sample_joined_data: {e}")
        return []


# Tool collection for easy import
LCA_TOOLS = [
    get_filings_by_city,
    get_high_wage_jobs,
    get_jobs_by_company,
    get_jobs_by_title,
    get_sample_joined_data
]


def get_all_lca_tools() -> List:
    """
    Get all available LCA data tools for LangChain agents.
    
    Returns:
        List of LangChain tools for LCA data querying
    """
    return LCA_TOOLS


# Example usage for LangChain agents
"""
Example usage in a LangChain agent:

from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain_tools import get_all_lca_tools

# Initialize LLM
llm = OpenAI(temperature=0)

# Get LCA tools
tools = get_all_lca_tools()

# Create agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use the agent
response = agent.run("Find high-paying tech jobs in San Francisco above $150,000")
"""
