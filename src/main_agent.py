#!/usr/bin/env python3
"""
Main CLI Runner for LCA Agent
============================

This is the main entry point for the LCA AI Agent system.
It loads environment variables, initializes the DataService,
creates a LangChain agent, and provides an interactive CLI.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.supabase_client import get_supabase_client
from services.data_service import DataService
from agent import create_lca_agent, run_agent_query
from tools import get_sync_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file"""
    print("🔧 Loading environment variables...")
    
    # Load .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print("✅ Environment variables loaded from .env")
    else:
        print("⚠️  No .env file found, using system environment variables")
    
    # Check required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please check your .env file and ensure all required variables are set.")
        return False
    
    print("✅ All required environment variables found")
    return True

def initialize_services():
    """Initialize DataService and verify database connection"""
    print("\n🔗 Initializing services...")
    
    try:
        # Test Supabase connection
        client = get_supabase_client()
        print("✅ Supabase client initialized")
        
        # Initialize DataService
        data_service = DataService()
        print("✅ DataService initialized")
        
        # Test database connection with a simple query
        print("🧪 Testing database connection...")
        sample_data = data_service.get_sample_joined_data(1)
        if sample_data:
            print(f"✅ Database connection successful - found {len(sample_data)} sample record(s)")
        else:
            print("⚠️  Database connection successful but no data found")
        
        return data_service
        
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return None

def initialize_agent():
    """Initialize the LangChain agent with LCA tools"""
    print("\n🤖 Initializing LangChain Agent...")
    
    try:
        # Create the agent
        agent = create_lca_agent(use_async=False, verbose=True)
        
        # Test the agent with a simple query
        print("🧪 Testing agent...")
        test_result = run_agent_query(agent, "Show me 1 sample LCA job")
        
        if test_result and "error" not in test_result.lower():
            print("✅ Agent test successful")
        else:
            print("⚠️  Agent test completed with warnings")
        
        return agent
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return None

def interactive_cli(agent):
    """Run interactive CLI for the LCA agent"""
    print("\n" + "="*70)
    print("🤖 LCA AI Agent - Interactive CLI")
    print("="*70)
    print("Ask me about LCA jobs! Examples:")
    print("• 'Find creative director jobs in San Francisco paying above $120k'")
    print("• 'List employers in Chicago with H-1B jobs'")
    print("• 'Show me high-paying software engineering roles'")
    print("• 'What director positions are available?'")
    print("• 'Give me 5 sample jobs'")
    print("\nCommands:")
    print("• Type 'help' for more examples")
    print("• Type 'tools' to see available tools")
    print("• Type 'quit' or 'exit' to leave")
    print("="*70)
    
    while True:
        try:
            user_input = input("\n💬 Your question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                show_help()
                continue
            
            if user_input.lower() == 'tools':
                show_tools()
                continue
            
            # Process the query
            print("\n" + "="*60)
            print(f"🤔 Processing: '{user_input}'")
            print("="*60)
            
            try:
                response = run_agent_query(agent, user_input)
                print(f"\n🤖 Response:\n{response}")
            except Exception as e:
                print(f"❌ Error processing query: {e}")
            
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def show_help():
    """Show help information with query examples"""
    print("\n📚 LCA Agent Help")
    print("="*50)
    print("🎯 Query Examples:")
    print("• City-based: 'Jobs in San Francisco', 'Employers in Chicago'")
    print("• Wage-based: 'High-paying jobs', 'Jobs above $150k', 'Positions under $80k'")
    print("• Company-based: 'Jobs at Google', 'Positions at Media companies'")
    print("• Title-based: 'Director positions', 'Software engineer roles'")
    print("• Sample data: 'Show me 10 jobs', 'Give me examples'")
    print("• Combined: 'Creative director jobs in NYC paying above $120k'")
    print("\n💡 Tips:")
    print("• Be specific with city names (e.g., 'San Francisco' not 'SF')")
    print("• Use dollar amounts for wage queries (e.g., '$120k' or '$120000')")
    print("• Combine criteria for more targeted results")

def show_tools():
    """Show available LangChain tools"""
    print("\n🛠️  Available Tools")
    print("="*50)
    tools = get_sync_tools()
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}")
        print(f"   Description: {tool.description.split('.')[0]}")
        print()

def run_single_query(query: str):
    """Run a single query and exit (useful for scripting)"""
    print(f"🚀 Running single query: '{query}'")
    
    # Initialize everything
    if not load_environment():
        return 1
    
    data_service = initialize_services()
    if not data_service:
        return 1
    
    agent = initialize_agent()
    if not agent:
        return 1
    
    # Run the query
    try:
        response = run_agent_query(agent, query)
        print(f"\n🤖 Response:\n{response}")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def main():
    """Main function"""
    print("🚀 Starting LCA AI Agent System")
    print("="*50)
    
    # Check for single query mode
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        return run_single_query(query)
    
    # Load environment
    if not load_environment():
        return 1
    
    # Initialize services
    data_service = initialize_services()
    if not data_service:
        return 1
    
    # Initialize agent
    agent = initialize_agent()
    if not agent:
        return 1
    
    # Start interactive CLI
    try:
        interactive_cli(agent)
    except Exception as e:
        print(f"❌ CLI error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
