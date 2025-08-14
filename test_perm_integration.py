#!/usr/bin/env python3
"""
PERM Integration Test Suite
==========================

This script tests all PERM-related functionality including:
1. PERM DataService methods
2. PERM LangChain tools
3. Combined LCA + PERM tools
4. Agent integration with PERM queries

Run this to verify your PERM integration is working correctly.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.data_service import DataService
from tools import (
    get_sample_perm_data, find_perm_jobs_by_city, find_perm_high_wage_jobs,
    find_perm_jobs_by_company, find_perm_jobs_by_title,
    find_all_jobs_by_city, find_all_high_wage_jobs,
    test_perm_tools, test_combined_tools, test_all_tools
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Load environment variables and verify setup"""
    print("🔧 Setting up environment...")
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please ensure your .env file contains SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    print("✅ Environment setup complete")
    return True

def test_perm_data_service():
    """Test PERM DataService methods directly"""
    print("\n" + "="*60)
    print("🧪 TESTING PERM DATA SERVICE METHODS")
    print("="*60)
    
    try:
        # Initialize data service
        data_service = DataService()
        print("✅ DataService initialized successfully")
        
        # Test 1: Sample PERM data
        print("\n1️⃣ Testing get_sample_perm_data...")
        sample_data = data_service.get_sample_perm_data(3)
        print(f"✅ Retrieved {len(sample_data)} sample PERM records")
        if sample_data:
            print(f"   Sample record: {sample_data[0]['company']} - {sample_data[0]['job_title']}")
        
        # Test 2: PERM jobs by city
        print("\n2️⃣ Testing get_perm_by_city...")
        city_jobs = data_service.get_perm_by_city("San Francisco", 5)
        print(f"✅ Found {len(city_jobs)} PERM jobs in San Francisco")
        
        # Test 3: PERM high wage jobs
        print("\n3️⃣ Testing get_perm_high_wage_jobs...")
        high_wage_jobs = data_service.get_perm_high_wage_jobs(100000, 5)
        print(f"✅ Found {len(high_wage_jobs)} PERM jobs above $100k")
        if high_wage_jobs:
            print(f"   Highest wage: ${high_wage_jobs[0]['wage']:,.2f}")
        
        # Test 4: PERM jobs by company
        print("\n4️⃣ Testing get_perm_by_company...")
        company_jobs = data_service.get_perm_by_company("Google", 3)
        print(f"✅ Found {len(company_jobs)} PERM jobs at companies matching 'Google'")
        
        # Test 5: PERM jobs by title
        print("\n5️⃣ Testing get_perm_by_title...")
        title_jobs = data_service.get_perm_by_title("Software Engineer", 3)
        print(f"✅ Found {len(title_jobs)} PERM 'Software Engineer' positions")
        
        print("\n✅ All PERM DataService methods working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing PERM DataService: {e}")
        logger.error(f"PERM DataService test failed: {e}")
        return False

def test_combined_data_service():
    """Test combined LCA + PERM DataService methods"""
    print("\n" + "="*60)
    print("🧪 TESTING COMBINED LCA + PERM DATA SERVICE METHODS")
    print("="*60)
    
    try:
        # Initialize data service
        data_service = DataService()
        
        # Test 1: All jobs by city
        print("\n1️⃣ Testing get_all_jobs_by_city...")
        all_city_jobs = data_service.get_all_jobs_by_city("San Francisco", 10)
        print(f"✅ Found {len(all_city_jobs)} total jobs (LCA + PERM) in San Francisco")
        
        # Count by visa type
        lca_count = len([job for job in all_city_jobs if job['visa_class'] != 'PERM'])
        perm_count = len([job for job in all_city_jobs if job['visa_class'] == 'PERM'])
        print(f"   LCA jobs: {lca_count}, PERM jobs: {perm_count}")
        
        # Test 2: All high wage jobs
        print("\n2️⃣ Testing get_all_high_wage_jobs...")
        all_high_wage = data_service.get_all_high_wage_jobs(120000, 10)
        print(f"✅ Found {len(all_high_wage)} total high-wage jobs (LCA + PERM) above $120k")
        
        if all_high_wage:
            print(f"   Highest wage: ${all_high_wage[0]['wage']:,.2f} ({all_high_wage[0]['visa_class']})")
        
        print("\n✅ All combined DataService methods working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing combined DataService: {e}")
        logger.error(f"Combined DataService test failed: {e}")
        return False

def test_perm_langchain_tools():
    """Test PERM LangChain tools"""
    print("\n" + "="*60)
    print("🧪 TESTING PERM LANGCHAIN TOOLS")
    print("="*60)
    
    try:
        # Test 1: Sample PERM data tool
        print("\n1️⃣ Testing get_sample_perm_data tool...")
        result = get_sample_perm_data("3")
        print(f"✅ Tool result: {len(result)} characters")
        print(f"   Preview: {result[:100]}...")
        
        # Test 2: PERM city search tool
        print("\n2️⃣ Testing find_perm_jobs_by_city tool...")
        result = find_perm_jobs_by_city("San Francisco")
        print(f"✅ Tool result: {len(result)} characters")
        
        # Test 3: PERM high wage tool
        print("\n3️⃣ Testing find_perm_high_wage_jobs tool...")
        result = find_perm_high_wage_jobs("100000")
        print(f"✅ Tool result: {len(result)} characters")
        
        # Test 4: PERM company search tool
        print("\n4️⃣ Testing find_perm_jobs_by_company tool...")
        result = find_perm_jobs_by_company("Microsoft")
        print(f"✅ Tool result: {len(result)} characters")
        
        # Test 5: PERM title search tool
        print("\n5️⃣ Testing find_perm_jobs_by_title tool...")
        result = find_perm_jobs_by_title("Data Scientist")
        print(f"✅ Tool result: {len(result)} characters")
        
        print("\n✅ All PERM LangChain tools working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing PERM LangChain tools: {e}")
        logger.error(f"PERM LangChain tools test failed: {e}")
        return False

def test_combined_langchain_tools():
    """Test combined LCA + PERM LangChain tools"""
    print("\n" + "="*60)
    print("🧪 TESTING COMBINED LANGCHAIN TOOLS")
    print("="*60)
    
    try:
        # Test 1: Combined city search
        print("\n1️⃣ Testing find_all_jobs_by_city tool...")
        result = find_all_jobs_by_city("Seattle")
        print(f"✅ Tool result: {len(result)} characters")
        print(f"   Preview: {result[:150]}...")
        
        # Test 2: Combined high wage search
        print("\n2️⃣ Testing find_all_high_wage_jobs tool...")
        result = find_all_high_wage_jobs("150000")
        print(f"✅ Tool result: {len(result)} characters")
        
        print("\n✅ All combined LangChain tools working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing combined LangChain tools: {e}")
        logger.error(f"Combined LangChain tools test failed: {e}")
        return False

def test_agent_integration():
    """Test agent integration with PERM queries"""
    print("\n" + "="*60)
    print("🧪 TESTING AGENT INTEGRATION")
    print("="*60)
    
    try:
        from agent import create_lca_agent
        from services.data_service import DataService
        
        # Initialize components
        data_service = DataService()
        agent = create_lca_agent(verbose=False)
        
        if not agent:
            print("❌ Failed to create agent")
            return False
        
        print("✅ Agent created successfully")
        
        # Test queries
        test_queries = [
            "Show me 3 sample PERM jobs",
            "Find PERM jobs in New York",
            "What are the highest paying PERM jobs?",
            "Show me all jobs (LCA and PERM) in San Francisco"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}️⃣ Testing query: '{query}'")
            try:
                response = agent.run(query)
                print(f"✅ Agent response: {len(response)} characters")
                print(f"   Preview: {response[:100]}...")
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        print("\n✅ Agent integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent integration: {e}")
        logger.error(f"Agent integration test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all PERM integration tests"""
    print("🚀 STARTING COMPREHENSIVE PERM INTEGRATION TEST")
    print("="*80)
    
    # Setup
    if not setup_environment():
        return False
    
    # Track test results
    test_results = []
    
    # Run all tests
    tests = [
        ("PERM DataService Methods", test_perm_data_service),
        ("Combined DataService Methods", test_combined_data_service),
        ("PERM LangChain Tools", test_perm_langchain_tools),
        ("Combined LangChain Tools", test_combined_langchain_tools),
        ("Agent Integration", test_agent_integration)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED! Your PERM integration is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return passed == len(tests)

def quick_test():
    """Run a quick test of key PERM functionality"""
    print("⚡ QUICK PERM TEST")
    print("="*40)
    
    if not setup_environment():
        return False
    
    try:
        # Test basic PERM data access
        data_service = DataService()
        sample_data = data_service.get_sample_perm_data(2)
        
        if sample_data:
            print(f"✅ PERM data accessible: {len(sample_data)} records")
            print(f"   Sample: {sample_data[0]['company']} - {sample_data[0]['job_title']}")
            
            # Test a tool
            tool_result = get_sample_perm_data("2")
            print(f"✅ PERM tools working: {len(tool_result)} characters")
            
            print("\n🎉 Quick test PASSED! PERM integration is working!")
            return True
        else:
            print("❌ No PERM data found. Check your database.")
            return False
            
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

if __name__ == "__main__":
    print("PERM Integration Test Suite")
    print("Choose an option:")
    print("1. Quick Test (recommended)")
    print("2. Comprehensive Test")
    print("3. Built-in Tool Tests")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        quick_test()
    elif choice == "2":
        run_comprehensive_test()
    elif choice == "3":
        print("\n🧪 Running built-in tool tests...")
        test_all_tools()
    else:
        print("Invalid choice. Running quick test...")
        quick_test()
    
    print("\n✨ Test completed!")
