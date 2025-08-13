#!/usr/bin/env python3
"""
LangChain Tools for LCA Data Querying
====================================

This module provides both sync and async LangChain tools for querying LCA data.
All tools are designed to work with LangChain agents and return formatted strings.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from langchain.tools import tool

from services.data_service import DataService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the global data service instance
data_service = DataService()

def format_job_results(results: List[Dict[str, Any]], query_type: str) -> str:
    """Format job results as a readable string for LangChain agents"""
    if not results:
        return f"No {query_type} found matching your criteria."
    
    output = [f"\n{query_type.title()} ({len(results)} found)"]
    output.append("=" * 60)
    
    for i, job in enumerate(results[:10], 1):  # Limit to 10 results
        company = job.get('company', 'N/A')
        title = job.get('job_title', 'N/A')
        city = job.get('city', 'N/A')
        state = job.get('state', 'N/A')
        wage = job.get('wage', 0)
        visa = job.get('visa_class', 'H-1B')
        
        output.append(f"\n{i}. 🏢 {company}")
        output.append(f"   📋 Position: {title}")
        output.append(f"   📍 Location: {city}, {state}")
        
        if wage and wage > 0:
            output.append(f"   💰 Salary: ${wage:,.0f}")
        else:
            output.append(f"   💰 Salary: Not specified")
        
        output.append(f"   🛂 Visa: {visa}")
    
    if len(results) > 10:
        output.append(f"\n... and {len(results) - 10} more results")
    
    return "\n".join(output)

# =============================================================================
# SYNC TOOLS
# =============================================================================

@tool
def get_sample_lca_data(limit_str: str = "10") -> str:
    """Get sample LCA filing data with worksite information.
    
    Args:
        limit_str: Number of records to return as string (default: "10")
    
    Returns:
        Formatted string with job listings
    
    Example: get_sample_lca_data("5")
    """
    try:
        limit = int(limit_str)
        logger.info(f"LangChain tool: Fetching sample data with limit: {limit}")
        results = data_service.get_sample_joined_data(limit)
        logger.info(f"LangChain tool: Found {len(results)} sample records")
        return format_job_results(results, "sample LCA jobs")
    except Exception as e:
        logger.error(f"LangChain tool error in get_sample_lca_data: {e}")
        return f"Error fetching sample data: {str(e)}"

@tool
def find_jobs_by_city(city: str) -> str:
    """Find LCA jobs in a specific city.
    
    Args:
        city: City name to search for
    
    Returns:
        Formatted string with job listings in that city
    
    Example: find_jobs_by_city("San Francisco")
    """
    try:
        logger.info(f"LangChain tool: Fetching jobs for city: {city}")
        results = data_service.get_filings_by_city(city, 20)
        logger.info(f"LangChain tool: Found {len(results)} jobs in {city}")
        return format_job_results(results, f"jobs in {city}")
    except Exception as e:
        logger.error(f"LangChain tool error in find_jobs_by_city: {e}")
        return f"Error finding jobs in {city}: {str(e)}"

@tool
def find_high_wage_jobs(min_wage_str: str) -> str:
    """Find LCA jobs with wages above the specified minimum.
    
    Args:
        min_wage_str: Minimum wage as string (e.g., "120000")
    
    Returns:
        Formatted string with high-wage job listings
    
    Example: find_high_wage_jobs("120000")
    """
    try:
        min_wage = float(min_wage_str)
        logger.info(f"LangChain tool: Fetching high wage jobs above ${min_wage:,.2f}")
        results = data_service.get_high_wage_jobs(min_wage, 20)
        logger.info(f"LangChain tool: Found {len(results)} high wage jobs")
        return format_job_results(results, f"high-wage jobs (${min_wage:,.0f}+)")
    except Exception as e:
        logger.error(f"LangChain tool error in find_high_wage_jobs: {e}")
        return f"Error finding high wage jobs: {str(e)}"

@tool
def find_jobs_by_company(company: str) -> str:
    """Find LCA jobs at a specific company or companies matching a name.
    
    Args:
        company: Company name or partial name to search for
    
    Returns:
        Formatted string with job listings at that company
    
    Example: find_jobs_by_company("Google")
    """
    try:
        logger.info(f"LangChain tool: Fetching jobs for company: {company}")
        results = data_service.get_jobs_by_company(company, 20)
        logger.info(f"LangChain tool: Found {len(results)} jobs at {company}")
        return format_job_results(results, f"jobs at {company}")
    except Exception as e:
        logger.error(f"LangChain tool error in find_jobs_by_company: {e}")
        return f"Error finding jobs at {company}: {str(e)}"

@tool
def find_jobs_by_title(title: str) -> str:
    """Find LCA jobs with specific job titles.
    
    Args:
        title: Job title or partial title to search for
    
    Returns:
        Formatted string with job listings matching that title
    
    Example: find_jobs_by_title("Creative Director")
    """
    try:
        logger.info(f"LangChain tool: Fetching jobs with title: {title}")
        results = data_service.get_jobs_by_title(title, 20)
        logger.info(f"LangChain tool: Found {len(results)} jobs with title: {title}")
        return format_job_results(results, f"'{title}' positions")
    except Exception as e:
        logger.error(f"LangChain tool error in find_jobs_by_title: {e}")
        return f"Error finding jobs with title {title}: {str(e)}"

# =============================================================================
# ASYNC TOOLS
# =============================================================================

@tool
async def get_sample_lca_data_async(limit_str: str = "10") -> str:
    """Async version: Get sample LCA filing data with worksite information.
    
    Args:
        limit_str: Number of records to return as string (default: "10")
    
    Returns:
        Formatted string with job listings
    
    Example: await get_sample_lca_data_async("5")
    """
    try:
        limit = int(limit_str)
        logger.info(f"LangChain async tool: Fetching sample data with limit: {limit}")
        results = await data_service.get_sample_joined_data_async(limit)
        logger.info(f"LangChain async tool: Found {len(results)} sample records")
        return format_job_results(results, "sample LCA jobs")
    except Exception as e:
        logger.error(f"LangChain async tool error in get_sample_lca_data_async: {e}")
        return f"Error fetching sample data: {str(e)}"

@tool
async def find_jobs_by_city_async(city: str) -> str:
    """Async version: Find LCA jobs in a specific city.
    
    Args:
        city: City name to search for
    
    Returns:
        Formatted string with job listings in that city
    
    Example: await find_jobs_by_city_async("San Francisco")
    """
    try:
        logger.info(f"LangChain async tool: Fetching jobs for city: {city}")
        results = await data_service.get_filings_by_city_async(city, 20)
        logger.info(f"LangChain async tool: Found {len(results)} jobs in {city}")
        return format_job_results(results, f"jobs in {city}")
    except Exception as e:
        logger.error(f"LangChain async tool error in find_jobs_by_city_async: {e}")
        return f"Error finding jobs in {city}: {str(e)}"

# =============================================================================
# TOOL COLLECTIONS
# =============================================================================

# Sync tools collection
SYNC_LCA_TOOLS = [
    get_sample_lca_data,
    find_jobs_by_city,
    find_high_wage_jobs,
    find_jobs_by_company,
    find_jobs_by_title
]

# Async tools collection
ASYNC_LCA_TOOLS = [
    get_sample_lca_data_async,
    find_jobs_by_city_async
]

def get_sync_tools() -> List:
    """Get all sync LCA data tools for LangChain agents.
    
    Returns:
        List of sync LangChain tools for LCA data querying
    """
    return SYNC_LCA_TOOLS

def get_async_tools() -> List:
    """Get all async LCA data tools for LangChain agents.
    
    Returns:
        List of async LangChain tools for LCA data querying
    """
    return ASYNC_LCA_TOOLS

def get_all_tools() -> List:
    """Get all LCA data tools (sync and async) for LangChain agents.
    
    Returns:
        List of all LangChain tools for LCA data querying
    """
    return SYNC_LCA_TOOLS + ASYNC_LCA_TOOLS

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def test_sync_tools():
    """Test all sync tools with sample queries"""
    print("\n🧪 Testing Sync LCA Tools")
    print("=" * 50)
    
    test_cases = [
        (get_sample_lca_data, "5"),
        (find_jobs_by_city, "San Francisco"),
        (find_high_wage_jobs, "120000"),
        (find_jobs_by_company, "Media"),
        (find_jobs_by_title, "Director")
    ]
    
    for tool_func, test_input in test_cases:
        print(f"\n🔧 Testing {tool_func.name} with input: '{test_input}'")
        try:
            result = tool_func.invoke({"input": test_input})
            print(f"✅ Result: {result[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_async_tools():
    """Test all async tools with sample queries"""
    print("\n🧪 Testing Async LCA Tools")
    print("=" * 50)
    
    test_cases = [
        (get_sample_lca_data_async, "3"),
        (find_jobs_by_city_async, "Chicago")
    ]
    
    for tool_func, test_input in test_cases:
        print(f"\n🔧 Testing {tool_func.name} with input: '{test_input}'")
        try:
            result = await tool_func.ainvoke({"input": test_input})
            print(f"✅ Result: {result[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test sync tools
    test_sync_tools()
    
    # Test async tools
    print("\n" + "=" * 60)
    asyncio.run(test_async_tools())
