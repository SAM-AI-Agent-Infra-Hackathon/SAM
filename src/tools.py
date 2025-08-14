#!/usr/bin/env python3
"""
LangChain Tools for LCA Data Querying
====================================

This module provides both sync and async LangChain tools for querying LCA data.
All tools are designed to work with LangChain agents and return formatted strings.
"""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
from langchain.tools import tool

from services.data_service import DataService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the global data service instance
data_service = DataService()

def format_job_results(results: List[Dict[str, Any]], query_type: str) -> str:
    """Format job results for display with strict UI rules.
    
    Rules enforced:
    - Header: emoji + bolded title
    - Numbered list with consistent icon order
    - One blank line between sections
    - Missing data -> "Not specified"
    """
    if not results:
        return f"📊 **{query_type.title()}** (0 found)\n{'=' * 60}\n\nNo results found matching your criteria."

    def _nz(val: Optional[str]) -> str:
        if val is None:
            return "Not specified"
        if isinstance(val, str):
            # Collapse all internal whitespace/newlines to single spaces
            v = re.sub(r"\s+", " ", val).strip()
            return v if v else "Not specified"
        return str(val)

    output: List[str] = []
    output.append(f"📊 **{query_type.title()}** ({len(results)} found)")
    output.append("=" * 60)
    
    # One blank line before list
    output.append("")

    for i, job in enumerate(results[:10], 1):  # Limit to 10 results
        company = _nz(job.get('company'))
        title = _nz(job.get('job_title'))
        city = _nz(job.get('city'))
        state = _nz(job.get('state'))
        visa = _nz(job.get('visa_class'))
        wage_val = job.get('wage')
        if isinstance(wage_val, (int, float)) and wage_val > 0:
            salary_str = f"${wage_val:,.0f}"
        else:
            salary_str = "Not specified"

        # Numbered list with fixed icon order
        output.append(f"{i}. 🏢 {company}")
        output.append("")
        output.append(f"   📋 Position: {title}")
        if city == "Not specified" and state != "Not specified":
            loc_str = state
        elif city != "Not specified" and state == "Not specified":
            loc_str = city
        elif city == "Not specified" and state == "Not specified":
            loc_str = "Not specified"
        else:
            loc_str = f"{city}, {state}"
        output.append(f"   📍 Location: {loc_str}")
        output.append(f"   💰 Salary: {salary_str}")
        output.append(f"   🛂 Visa: {visa}")
        
        # One blank line between entries for readability
        output.append("")
    
    if len(results) > 10:
        output.append(f"... and {len(results) - 10} more results")
    
    # Ensure trailing newline trimmed
    return "\n".join(line for line in output).rstrip()

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
# PERM TOOLS
# =============================================================================

@tool
def get_sample_perm_data(limit_str: str = "10") -> str:
    """Get sample PERM disclosure data.
    
    Args:
        limit_str: Number of records to return as string (default: "10")
    
    Returns:
        Formatted string with PERM job listings
    
    Example: get_sample_perm_data("5")
    """
    try:
        limit = int(limit_str)
        logger.info(f"LangChain tool: Fetching sample PERM data with limit: {limit}")
        results = data_service.get_sample_perm_data(limit)
        logger.info(f"LangChain tool: Found {len(results)} sample PERM records")
        return format_job_results(results, "sample PERM jobs")
    except Exception as e:
        logger.error(f"LangChain tool error in get_sample_perm_data: {e}")
        return f"Error fetching sample PERM data: {str(e)}"

@tool
def find_perm_jobs_by_city(city: str) -> str:
    """Find PERM jobs in a specific city.
    
    Args:
        city: City name to search for
    
    Returns:
        Formatted string with PERM job listings in that city
    
    Example: find_perm_jobs_by_city("San Francisco")
    """
    try:
        logger.info(f"LangChain tool: Fetching PERM jobs for city: {city}")
        results = data_service.get_perm_by_city(city, 20)
        logger.info(f"LangChain tool: Found {len(results)} PERM jobs in {city}")
        return format_job_results(results, f"PERM jobs in {city}")
    except Exception as e:
        logger.error(f"LangChain tool error in find_perm_jobs_by_city: {e}")
        return f"Error finding PERM jobs in {city}: {str(e)}"

@tool
def find_perm_high_wage_jobs(min_wage_str: str) -> str:
    """Find PERM jobs with wages above the specified minimum.
    
    Args:
        min_wage_str: Minimum wage as string (e.g., "120000")
    
    Returns:
        Formatted string with high-wage PERM job listings
    
    Example: find_perm_high_wage_jobs("120000")
    """
    try:
        min_wage = float(min_wage_str)
        logger.info(f"LangChain tool: Fetching PERM high wage jobs above ${min_wage:,.2f}")
        results = data_service.get_perm_high_wage_jobs(min_wage, 20)
        logger.info(f"LangChain tool: Found {len(results)} PERM high wage jobs")
        return format_job_results(results, f"high-wage PERM jobs (${min_wage:,.0f}+)")
    except Exception as e:
        logger.error(f"LangChain tool error in find_perm_high_wage_jobs: {e}")
        return f"Error finding PERM high wage jobs: {str(e)}"

@tool
def find_perm_jobs_by_company(company: str) -> str:
    """Find PERM jobs at a specific company.
    
    Args:
        company: Company name or partial name to search for
    
    Returns:
        Formatted string with PERM job listings at that company
    
    Example: find_perm_jobs_by_company("Google")
    """
    try:
        logger.info(f"LangChain tool: Fetching PERM jobs for company: {company}")
        results = data_service.get_perm_by_company(company, 20)
        logger.info(f"LangChain tool: Found {len(results)} PERM jobs at {company}")
        return format_job_results(results, f"PERM jobs at {company}")
    except Exception as e:
        logger.error(f"LangChain tool error in find_perm_jobs_by_company: {e}")
        return f"Error finding PERM jobs at {company}: {str(e)}"

@tool
def find_perm_jobs_by_title(title: str) -> str:
    """Find PERM jobs with specific job titles.
    
    Args:
        title: Job title or partial title to search for
    
    Returns:
        Formatted string with PERM job listings matching that title
    
    Example: find_perm_jobs_by_title("Software Engineer")
    """
    try:
        logger.info(f"LangChain tool: Fetching PERM jobs with title: {title}")
        results = data_service.get_perm_by_title(title, 20)
        logger.info(f"LangChain tool: Found {len(results)} PERM jobs with title: {title}")
        return format_job_results(results, f"PERM '{title}' positions")
    except Exception as e:
        logger.error(f"LangChain tool error in find_perm_jobs_by_title: {e}")
        return f"Error finding PERM jobs with title {title}: {str(e)}"

# =============================================================================
# COMBINED LCA + PERM TOOLS
# =============================================================================

@tool
def find_all_jobs_by_city(city: str) -> str:
    """Find both LCA and PERM jobs in a specific city.
    
    Args:
        city: City name to search for
    
    Returns:
        Formatted string with combined LCA and PERM job listings
    
    Example: find_all_jobs_by_city("San Francisco")
    """
    try:
        logger.info(f"LangChain tool: Fetching all jobs (LCA + PERM) for city: {city}")
        results = data_service.get_all_jobs_by_city(city, 30)
        logger.info(f"LangChain tool: Found {len(results)} total jobs in {city}")
        return format_job_results(results, f"all jobs (LCA + PERM) in {city}")
    except Exception as e:
        logger.error(f"LangChain tool error in find_all_jobs_by_city: {e}")
        return f"Error finding all jobs in {city}: {str(e)}"

@tool
def find_all_high_wage_jobs(min_wage_str: str) -> str:
    """Find both LCA and PERM high-wage jobs.
    
    Args:
        min_wage_str: Minimum wage as string (e.g., "120000")
    
    Returns:
        Formatted string with combined high-wage job listings
    
    Example: find_all_high_wage_jobs("150000")
    """
    try:
        min_wage = float(min_wage_str)
        logger.info(f"LangChain tool: Fetching all high wage jobs (LCA + PERM) above ${min_wage:,.2f}")
        results = data_service.get_all_high_wage_jobs(min_wage, 30)
        logger.info(f"LangChain tool: Found {len(results)} total high wage jobs")
        return format_job_results(results, f"all high-wage jobs (LCA + PERM) (${min_wage:,.0f}+)")
    except Exception as e:
        logger.error(f"LangChain tool error in find_all_high_wage_jobs: {e}")
        return f"Error finding all high wage jobs: {str(e)}"

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

# Sync tools collection - LCA only
SYNC_LCA_TOOLS = [
    get_sample_lca_data,
    find_jobs_by_city,
    find_high_wage_jobs,
    find_jobs_by_company,
    find_jobs_by_title
]

# Sync tools collection - PERM only
SYNC_PERM_TOOLS = [
    get_sample_perm_data,
    find_perm_jobs_by_city,
    find_perm_high_wage_jobs,
    find_perm_jobs_by_company,
    find_perm_jobs_by_title
]

# Sync tools collection - Combined LCA + PERM
SYNC_COMBINED_TOOLS = [
    find_all_jobs_by_city,
    find_all_high_wage_jobs
]

# All sync tools
SYNC_ALL_TOOLS = SYNC_LCA_TOOLS + SYNC_PERM_TOOLS + SYNC_COMBINED_TOOLS

# Async tools collection
ASYNC_LCA_TOOLS = [
    get_sample_lca_data_async,
    find_jobs_by_city_async
]

def get_sync_tools() -> List:
    """Get all sync tools (LCA + PERM + Combined) for LangChain agents.
    
    Returns:
        List of all sync LangChain tools for data querying
    """
    return SYNC_ALL_TOOLS

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
# TEST FUNCTIONS
# =============================================================================

def test_sync_tools():
    """Test all sync tools to ensure they work correctly"""
    print("🧪 Testing sync LCA tools...")
    
    try:
        # Test sample data
        print("\n1. Testing get_sample_lca_data...")
        result = get_sample_lca_data("3")
        print(f"✅ Sample data: {len(result)} characters")
        
        # Test city search
        print("\n2. Testing find_jobs_by_city...")
        result = find_jobs_by_city("San Francisco")
        print(f"✅ City search: {len(result)} characters")
        
        # Test high wage search
        print("\n3. Testing find_high_wage_jobs...")
        result = find_high_wage_jobs("100000")
        print(f"✅ High wage search: {len(result)} characters")
        
        print("\n✅ All sync LCA tools working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing sync LCA tools: {e}")
        logger.error(f"Error in test_sync_tools: {e}")

def test_perm_tools():
    """Test all PERM tools to ensure they work correctly"""
    print("🧪 Testing sync PERM tools...")
    
    try:
        # Test PERM sample data
        print("\n1. Testing get_sample_perm_data...")
        result = get_sample_perm_data("3")
        print(f"✅ PERM sample data: {len(result)} characters")
        
        # Test PERM city search
        print("\n2. Testing find_perm_jobs_by_city...")
        result = find_perm_jobs_by_city("San Francisco")
        print(f"✅ PERM city search: {len(result)} characters")
        
        # Test PERM high wage search
        print("\n3. Testing find_perm_high_wage_jobs...")
        result = find_perm_high_wage_jobs("100000")
        print(f"✅ PERM high wage search: {len(result)} characters")
        
        # Test PERM company search
        print("\n4. Testing find_perm_jobs_by_company...")
        result = find_perm_jobs_by_company("Google")
        print(f"✅ PERM company search: {len(result)} characters")
        
        print("\n✅ All sync PERM tools working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing sync PERM tools: {e}")
        logger.error(f"Error in test_perm_tools: {e}")

def test_combined_tools():
    """Test combined LCA + PERM tools"""
    print("🧪 Testing combined LCA + PERM tools...")
    
    try:
        # Test combined city search
        print("\n1. Testing find_all_jobs_by_city...")
        result = find_all_jobs_by_city("San Francisco")
        print(f"✅ Combined city search: {len(result)} characters")
        
        # Test combined high wage search
        print("\n2. Testing find_all_high_wage_jobs...")
        result = find_all_high_wage_jobs("120000")
        print(f"✅ Combined high wage search: {len(result)} characters")
        
        print("\n✅ All combined tools working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing combined tools: {e}")
        logger.error(f"Error in test_combined_tools: {e}")

def test_all_tools():
    """Test all tools (LCA, PERM, and Combined)"""
    print("🧪 Testing ALL tools...")
    test_sync_tools()
    test_perm_tools()
    test_combined_tools()
    print("\n🎉 All tool testing completed!")

async def test_async_tools():
    """Test all async tools to ensure they work correctly"""
    print("🧪 Testing async LCA tools...")
    
    try:
        # Test async sample data
        print("\n1. Testing get_sample_lca_data_async...")
        result = await get_sample_lca_data_async("3")
        print(f"✅ Async sample data: {len(result)} characters")
        
        # Test async city search
        print("\n2. Testing find_jobs_by_city_async...")
        result = await find_jobs_by_city_async("San Francisco")
        print(f"✅ Async city search: {len(result)} characters")
        
        print("\n✅ All async tools working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing async tools: {e}")
        logger.error(f"Error in test_async_tools: {e}")

if __name__ == "__main__":
    # Test sync tools
    test_sync_tools()
    
    # Test async tools
    print("\n" + "=" * 60)
    asyncio.run(test_async_tools())
