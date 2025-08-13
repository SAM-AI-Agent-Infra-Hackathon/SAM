"""
Main script for the Supabase LCA data fetcher.

This script demonstrates how to use the data service to fetch joined data
from lca_filings and lca_worksites tables. It includes both sync and async
examples for different use cases.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any

from services.data_service import get_sample_joined_data, get_sample_joined_data_async, DataService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_results(data: List[Dict[str, Any]], title: str = "Results") -> None:
    """
    Pretty print the query results.
    
    Args:
        data: List of dictionaries to print
        title: Title for the output section
    """
    print(f"\n{'=' * 50}")
    print(f"{title}")
    print(f"{'=' * 50}")
    
    if not data:
        print("No data found.")
        return
    
    print(f"Found {len(data)} records:")
    print()
    
    for i, record in enumerate(data, 1):
        print(f"Record {i}:")
        for key, value in record.items():
            print(f"  {key}: {value}")
        print()


async def run_async_example(limit: int = 5) -> None:
    """
    Demonstrate async data fetching.
    
    Args:
        limit: Number of records to fetch
    """
    try:
        logger.info("Running async example...")
        data = await get_sample_joined_data_async(limit)
        print_results(data, f"Async Results (limit: {limit})")
    except Exception as e:
        logger.error(f"Async example failed: {e}")
        print(f"Error in async example: {e}")


def run_sync_example(limit: int = 10) -> None:
    """
    Demonstrate synchronous data fetching.
    
    Args:
        limit: Number of records to fetch
    """
    try:
        logger.info("Running sync example...")
        data = get_sample_joined_data(limit)
        print_results(data, f"Sync Results (limit: {limit})")
    except Exception as e:
        logger.error(f"Sync example failed: {e}")
        print(f"Error in sync example: {e}")


def run_service_example(limit: int = 3) -> None:
    """
    Demonstrate using the DataService class directly.
    
    Args:
        limit: Number of records to fetch
    """
    try:
        logger.info("Running DataService example...")
        service = DataService()
        data = service.get_sample_joined_data(limit)
        print_results(data, f"DataService Results (limit: {limit})")
    except Exception as e:
        logger.error(f"DataService example failed: {e}")
        print(f"Error in DataService example: {e}")


def main() -> None:
    """
    Main function that demonstrates different ways to fetch data.
    """
    print("🚀 Supabase LCA Data Fetcher")
    print("This script demonstrates fetching joined data from lca_filings and lca_worksites tables.")
    
    try:
        # Run synchronous example
        run_sync_example(limit=10)
        
        # Run DataService example
        run_service_example(limit=3)
        
        # Run async example
        print("\n" + "=" * 50)
        print("Running async example...")
        print("=" * 50)
        asyncio.run(run_async_example(limit=5))
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("1. Your .env file has the correct Supabase credentials")
        print("2. Your Supabase tables (lca_filings, lca_worksites) exist")
        print("3. Your network connection is working")
    else:
        print("\n✅ All examples completed successfully!")
        print("\nNext steps:")
        print("- Integrate with LangChain/LangGraph for AI-powered querying")
        print("- Add more complex queries using DataService.execute_custom_query()")
        print("- Build a web API or CLI interface on top of this foundation")


if __name__ == "__main__":
    main()
