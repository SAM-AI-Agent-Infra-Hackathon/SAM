#!/usr/bin/env python3
"""
Quick PERM Test - Verify fixes are working
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_perm_fixes():
    """Test that PERM wage column fix is working"""
    print("🧪 Testing PERM fixes...")
    
    # Load environment
    load_dotenv()
    
    try:
        from services.data_service import DataService
        
        # Test basic PERM data
        data_service = DataService()
        print("✅ DataService initialized")
        
        # Test sample data
        sample_data = data_service.get_sample_perm_data(2)
        print(f"✅ Sample PERM data: {len(sample_data)} records")
        if sample_data:
            print(f"   Sample: {sample_data[0]['company']} - ${sample_data[0]['wage']:,.2f}")
        
        # Test high wage jobs (this was failing before)
        print("\n🧪 Testing PERM high wage jobs...")
        high_wage = data_service.get_perm_high_wage_jobs(80000, 3)
        print(f"✅ PERM high wage jobs: {len(high_wage)} records")
        if high_wage:
            print(f"   Highest: ${high_wage[0]['wage']:,.2f} at {high_wage[0]['company']}")
        
        # Test combined high wage jobs
        print("\n🧪 Testing combined high wage jobs...")
        combined = data_service.get_all_high_wage_jobs(100000, 5)
        print(f"✅ Combined high wage jobs: {len(combined)} records")
        
        # Count by type
        lca_count = len([job for job in combined if job['visa_class'] != 'PERM'])
        perm_count = len([job for job in combined if job['visa_class'] == 'PERM'])
        print(f"   LCA: {lca_count}, PERM: {perm_count}")
        
        print("\n🎉 All PERM fixes working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_agent_creation():
    """Test that agent creation is working"""
    print("\n🧪 Testing agent creation...")
    
    try:
        from agent import create_lca_agent
        
        agent = create_lca_agent(verbose=False)
        print("✅ Agent created successfully")
        
        # Test a simple PERM query
        from agent import run_agent_query
        result = run_agent_query(agent, "Show me 2 sample PERM jobs")
        print(f"✅ Agent query result: {len(result)} characters")
        print(f"   Preview: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick PERM Fix Test")
    print("=" * 40)
    
    success1 = test_perm_fixes()
    success2 = test_agent_creation()
    
    if success1 and success2:
        print("\n🎉 ALL FIXES WORKING! Your PERM integration is ready!")
    else:
        print("\n⚠️  Some issues remain. Check the errors above.")
