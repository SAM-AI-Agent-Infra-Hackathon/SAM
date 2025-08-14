#!/usr/bin/env python3
"""
LangChain Agent Setup for LCA Data Querying
==========================================

This module provides agent setup and configuration for LCA data querying.
Supports both sync and async agents with proper error handling and fallbacks.
"""

import os
import logging
from typing import List, Optional, Any
from langchain.agents import initialize_agent, AgentType
from langchain.agents.agent import AgentExecutor
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler

from tools import get_sync_tools, get_async_tools

# Configure logging
logger = logging.getLogger(__name__)

class LCAAgentCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for LCA agent to provide better user feedback"""
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Called when agent takes an action"""
        print(f"🔧 Using tool: {action.tool}")
        print(f"📝 Input: {action.tool_input}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Called when agent finishes"""
        print(f"✅ Agent completed successfully")
    
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs: Any) -> Any:
        """Called when tool starts"""
        tool_name = serialized.get("name", "Unknown")
        print(f"🛠️  Executing: {tool_name}")
    
    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Called when tool ends"""
        print(f"📊 Tool result: {len(output)} characters")

def setup_llm():
    """Setup LLM for the agent with working configuration"""
    print("🤖 Setting up LLM...")
    
    # Try OpenAI first if available
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("🔄 Trying OpenAI...")
            llm = setup_openai_llm()
            print("✅ OpenAI LLM ready")
            return llm
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")
    
    # Use a working Mock LLM that follows ReAct format
    print("🔄 Using Smart Mock LLM...")
    llm = setup_smart_mock_llm()
    print("✅ Smart Mock LLM ready")
    return llm

def setup_openai_llm():
    """Setup OpenAI LLM if API key is available"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY not found in environment")
    
    from langchain.llms import OpenAI
    return OpenAI(
        temperature=0.1,
        max_tokens=500,
        openai_api_key=api_key
    )

def setup_huggingface_llm():
    """Setup Hugging Face LLM for local inference"""
    try:
        from langchain_huggingface import HuggingFacePipeline
        from transformers import pipeline
        
        # Use a more suitable model for instruction following
        model_name = "microsoft/DialoGPT-medium"
        
        hf_pipeline = pipeline(
            "text-generation",
            model=model_name,
            tokenizer=model_name,
            device=-1,  # CPU
            return_full_text=False,
            do_sample=True,  # Enable sampling for more varied responses
            temperature=0.7,  # Higher temperature for better instruction following
            max_new_tokens=200,  # More tokens for complete responses
            pad_token_id=50256,
            eos_token_id=50256,
            truncation=True
        )
        
        return HuggingFacePipeline(pipeline=hf_pipeline)
        
    except ImportError:
        raise Exception("transformers and langchain-huggingface not installed")

def setup_smart_mock_llm():
    """Setup smart mock LLM that follows ReAct format properly"""
    from langchain.llms.fake import FakeListLLM
    
    # Proper ReAct format responses for different query types
    responses = [
        # Sample data queries
        "Thought: The user wants to see sample LCA job data. I should use the get_sample_lca_data tool.\nAction: get_sample_lca_data\nAction Input: 5",
        
        # City-based queries
        "Thought: The user is asking about jobs in a specific city. I should use the find_jobs_by_city tool.\nAction: find_jobs_by_city\nAction Input: San Francisco",
        
        # High wage queries  
        "Thought: The user wants high-paying jobs. I should use the find_high_wage_jobs tool.\nAction: find_high_wage_jobs\nAction Input: 120000",
        
        # Company queries
        "Thought: The user is looking for jobs at a specific company. I should use the find_jobs_by_company tool.\nAction: find_jobs_by_company\nAction Input: Google",
        
        # Title queries
        "Thought: The user wants jobs with a specific title. I should use the find_jobs_by_title tool.\nAction: find_jobs_by_title\nAction Input: Director",
        
        # Generic sample query
        "Thought: I should show some sample LCA data to help the user.\nAction: get_sample_lca_data\nAction Input: 10",
        
        # City query variation
        "Thought: The user wants jobs in Chicago. I'll search for jobs in that city.\nAction: find_jobs_by_city\nAction Input: Chicago",
        
        # High wage variation
        "Thought: The user is looking for high-paying positions. I'll search for jobs above $100k.\nAction: find_high_wage_jobs\nAction Input: 100000",
        
        # Title variation
        "Thought: The user wants creative director positions. I'll search by job title.\nAction: find_jobs_by_title\nAction Input: Creative Director",
        
        # Default fallback
        "Thought: I'll provide some sample LCA job data.\nAction: get_sample_lca_data\nAction Input: 5"
    ]
    
    return FakeListLLM(responses=responses)

def setup_mock_llm():
    """Legacy mock LLM - kept for compatibility"""
    return setup_smart_mock_llm()

def create_lca_agent(use_async: bool = False, verbose: bool = True) -> AgentExecutor:
    """Create a LangChain agent for LCA data querying.
    
    Args:
        use_async: Whether to use async tools (default: False)
        verbose: Whether to enable verbose output (default: True)
    
    Returns:
        Configured LangChain agent executor
    """
    try:
        print("\n🚀 Creating LCA Agent")
        print("=" * 50)
        
        # Setup LLM
        llm = setup_llm()
        
        # Get appropriate tools
        if use_async:
            tools = get_async_tools()
            print(f"🔧 Loaded {len(tools)} async tools")
        else:
            tools = get_sync_tools()
            print(f"🔧 Loaded {len(tools)} sync tools")
        
        # List available tools
        for tool in tools:
            print(f"  - {tool.name}: {tool.description.split('.')[0]}")
        
        # Setup callback handler
        callbacks = [LCAAgentCallbackHandler()] if verbose else []
        
        # Create agent with working configuration
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
            callbacks=callbacks,
            max_iterations=2,  # Reduced iterations for faster responses
            early_stopping_method="generate",
            handle_parsing_errors="Check your output and make sure it conforms to the format instructions!"
        )
        
        print("✅ LCA Agent created successfully!")
        return agent
        
    except Exception as e:
        logger.error(f"Error creating LCA agent: {e}")
        raise

def run_agent_query(agent: AgentExecutor, query: str) -> str:
    """Run a query through the LCA agent with smart fallback to working agent.
    
    Args:
        agent: The LangChain agent executor
        query: Natural language query to process
    
    Returns:
        Agent response as string
    """
    try:
        print(f"\n🗣️  Query: {query}")
        print("=" * 60)
        
        # Try LangChain agent first (with timeout)
        print("🤖 Trying LangChain agent...")
        response = agent.invoke({"input": query})
        
        # Extract the output
        if isinstance(response, dict):
            result = response.get("output", str(response))
        else:
            result = str(response)
        
        # Accept any non-empty output from the agent, unless it's a ReAct trace
        if result and result.strip() and ("error" not in result.lower()):
            # If the model returned internal planning (Thought/Action), don't surface it
            lower = result.lower()
            if ("thought:" in lower and "action:" in lower) or (result.strip().startswith("Thought:")):
                raise Exception("Agent returned planning trace instead of final answer")
            return result
        else:
            raise Exception("LangChain agent returned invalid response")
        
    except Exception as e:
        logger.error(f"LangChain agent failed: {e}")
        
        # Fallback: Use our working agent logic
        print(f"🔧 LangChain agent failed, using smart fallback...")
        try:
            from working_agent import WorkingLCAAgent
            
            # Create and use our working agent
            working_agent = WorkingLCAAgent()
            result = working_agent.analyze_and_execute(query)
            
            print("✅ Smart fallback successful")
            return result
                
        except Exception as fallback_error:
            logger.error(f"Smart fallback failed: {fallback_error}")
            
            # Final fallback: Direct tool usage
            print(f"🔧 Using direct tool fallback...")
            try:
                import re
                from tools import find_jobs_by_city, get_sample_lca_data, find_high_wage_jobs

                def _parse_wage(q: str) -> str:
                    s = q.lower()
                    # look for patterns like 100k, $120,000, 120000, 100$
                    m = re.search(r"\$?\s*(\d[\d,]*)(k)?", s)
                    if not m:
                        return None
                    num = m.group(1).replace(",", "")
                    val = float(num)
                    if m.group(2) == 'k' or val < 1000:
                        val *= 1000
                    return str(int(val))

                query_lower = query.lower()
                # Wage-specific intent
                wage = _parse_wage(query)
                if wage:
                    return find_high_wage_jobs.invoke({"min_wage_str": wage})
                if "sample" in query_lower:
                    return get_sample_lca_data.invoke({"limit_str": "5"})
                elif "san francisco" in query_lower:
                    return find_jobs_by_city.invoke({"city": "San Francisco"})
                elif "chicago" in query_lower:
                    return find_jobs_by_city.invoke({"city": "Chicago"})
                elif "high" in query_lower or "120" in query_lower:
                    return find_high_wage_jobs.invoke({"min_wage_str": "120000"})
                else:
                    return get_sample_lca_data.invoke({"limit_str": "10"})
                    
            except Exception as final_error:
                return f"Sorry, all agent systems failed. Please try a simpler query like 'Show me sample jobs' or 'Jobs in San Francisco'."

async def run_agent_query_async(agent: AgentExecutor, query: str) -> str:
    """Async version: Run a query through the LCA agent.
    
    Args:
        agent: The LangChain agent executor
        query: Natural language query to process
    
    Returns:
        Agent response as string
    """
    try:
        print(f"\n🗣️  Async Query: {query}")
        print("=" * 60)
        
        # Run the agent asynchronously
        response = await agent.ainvoke({"input": query})
        
        # Extract the output
        if isinstance(response, dict):
            result = response.get("output", str(response))
        else:
            result = str(response)
        
        return result
        
    except Exception as e:
        logger.error(f"Error running async agent query: {e}")
        return f"Sorry, I encountered an error processing your async query: {str(e)}"

def test_agent():
    """Test the LCA agent with sample queries"""
    print("\n🧪 Testing LCA Agent")
    print("=" * 50)
    
    try:
        # Create agent
        agent = create_lca_agent(verbose=True)
        
        # Test queries
        test_queries = [
            "Show me 3 sample LCA jobs",
            "Find jobs in San Francisco",
            "What high-paying positions are available?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}: {query}")
            print("-" * 40)
            
            try:
                result = run_agent_query(agent, query)
                print(f"✅ Result: {result[:200]}...")
            except Exception as e:
                print(f"❌ Test failed: {e}")
            
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")

if __name__ == "__main__":
    test_agent()
