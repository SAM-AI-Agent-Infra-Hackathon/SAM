"""
Test script for LangChain Tools

This script demonstrates how to use the LangChain-wrapped DataService methods
for AI agent integration.
"""

import logging
from langchain_tools import (
    get_filings_by_city,
    get_high_wage_jobs,
    get_jobs_by_company,
    get_jobs_by_title,
    get_sample_joined_data,
    get_all_lca_tools
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_clean_results(data, title, max_display=3):
    """Print LangChain tool results in a clean format."""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")
    
    if not data:
        print("No results found.")
        return
    
    print(f"Found {len(data)} total records")
    print(f"Showing first {min(len(data), max_display)} records:\n")
    
    for i, record in enumerate(data[:max_display], 1):
        print(f"Record {i}:")
        print(f"  Case Number: {record['case_number']}")
        print(f"  Company: {record['company']}")
        print(f"  Job Title: {record['job_title']}")
        print(f"  Location: {record['city']}, {record.get('state', 'N/A')}")
        wage = record['wage']
        wage_str = f"${wage:,.2f}" if wage > 0 else "Not specified"
        print(f"  Wage: {wage_str}")
        print(f"  Visa Class: {record['visa_class']}")
        print()


def test_langchain_tools():
    """Test all LangChain tools with the new clean data structure."""
    
    print("🔧 Testing LangChain Tools for LCA Data")
    print("=" * 60)
    
    try:
        # Test 1: Sample data
        print("📊 Testing sample data tool...")
        sample_results = get_sample_joined_data.invoke({"limit": 5})
        print_clean_results(sample_results, "Sample LCA Data")
        
        # Test 2: City filter
        print("\n🏙️ Testing city filter tool...")
        city_results = get_filings_by_city.invoke({"city": "New York", "limit": 5})
        print_clean_results(city_results, "Jobs in New York")
        
        # Test 3: High wage filter
        print("\n💰 Testing high wage filter tool...")
        wage_results = get_high_wage_jobs.invoke({"min_wage": 100000.0, "limit": 5})
        print_clean_results(wage_results, "High Wage Jobs (>$100K)")
        
        # Test 4: Company filter
        print("\n🏢 Testing company filter tool...")
        company_results = get_jobs_by_company.invoke({"company": "Media", "limit": 5})
        print_clean_results(company_results, "Jobs at Media Companies")
        
        # Test 5: Title filter
        print("\n👔 Testing job title filter tool...")
        title_results = get_jobs_by_title.invoke({"title": "Director", "limit": 5})
        print_clean_results(title_results, "Director Positions")
        
        # Test 6: Tool collection
        print(f"\n🛠️ Available LangChain Tools:")
        tools = get_all_lca_tools()
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.name}: {tool.description.split('.')[0]}")
        
        # Summary
        print(f"\n{'=' * 60}")
        print("LANGCHAIN TOOLS TEST SUMMARY")
        print(f"{'=' * 60}")
        print(f"✅ Sample data: {len(sample_results)} results")
        print(f"✅ City filter (New York): {len(city_results)} results")
        print(f"✅ High wage filter (>$100K): {len(wage_results)} results")
        print(f"✅ Company filter (Media): {len(company_results)} results")
        print(f"✅ Title filter (Director): {len(title_results)} results")
        print(f"✅ Total tools available: {len(tools)}")
        print("\n🎉 All LangChain tools working successfully!")
        print("\n🤖 Ready for AI Agent Integration!")
        
    except Exception as e:
        logger.error(f"Error testing LangChain tools: {e}")
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("1. Your .env file has correct Supabase credentials")
        print("2. Your database tables exist and have data")
        print("3. LangChain is installed (pip install langchain)")


def demonstrate_agent_usage():
    """Show example of how these tools would be used in a LangChain agent."""
    
    print(f"\n{'=' * 60}")
    print("EXAMPLE: LangChain Agent Integration")
    print(f"{'=' * 60}")
    
    example_code = '''
# Example LangChain Agent Setup
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain_tools import get_all_lca_tools

# Initialize LLM
llm = OpenAI(temperature=0, openai_api_key="your-key")

# Get LCA tools
tools = get_all_lca_tools()

# Create agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Example queries the agent can handle:
responses = [
    agent.run("Find high-paying tech jobs in San Francisco above $150,000"),
    agent.run("Show me all Google positions available"),
    agent.run("What director-level jobs are available in New York?"),
    agent.run("Find the highest paying software engineering roles")
]
'''
    
    print("📝 Code Example:")
    print(example_code)
    
    print("🗣️ Natural Language Queries the Agent Can Handle:")
    queries = [
        "Find high-paying tech jobs in San Francisco above $150,000",
        "Show me all Google positions available", 
        "What director-level jobs are available in New York?",
        "Find the highest paying software engineering roles",
        "Which companies offer the best salaries for product managers?",
        "Show me entry-level positions in Seattle"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"  {i}. \"{query}\"")


if __name__ == "__main__":
    test_langchain_tools()
    demonstrate_agent_usage()
