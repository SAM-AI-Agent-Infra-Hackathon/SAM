#!/usr/bin/env python3
"""
Immigration-Aware Main Agent
===========================

Enhanced version of the main agent that understands immigration context
and provides guidance specifically for international students.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from services.data_service import DataService
from agent import create_lca_agent, run_agent_query
from immigration_agent import ImmigrationAgent
from tools import format_job_results
import re
from typing import Optional, Tuple, Dict
from web_sources import (
    get_top_h1b_companies_2025,
    get_h1b_majors_study,
    get_school_sponsors_links,
    get_company_h1b_links,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedImmigrationAgent:
    """Enhanced agent that combines LangChain capabilities with immigration context"""
    
    def __init__(self):
        self.data_service = DataService()
        self.langchain_agent = create_lca_agent(verbose=False)
        self.immigration_agent = ImmigrationAgent(self.data_service)
        
    def process_query(self, query: str) -> str:
        """Process query with immigration context awareness"""
        # 0) FAQ knowledge intents with live sources
        faq = self._extract_faq_intent(query)
        if faq:
            intent, args = faq
            try:
                return self._answer_faq_with_sources(intent, args)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"FAQ handler failed: {e}")
                # continue to other handlers
        # Highest priority: explicit visa intent (e.g., only H-1B jobs)
        visa = self._extract_visa(query)
        if visa:
            try:
                sample = self.data_service.get_sample_joined_data(200)
                filt = []
                for j in sample:
                    v = (j.get('visa_class') or '').strip()
                    if not v:
                        continue
                    if visa == 'H-1B' and 'h-1b' in v.lower():
                        filt.append(j)
                    elif visa == 'PERM' and ('perm' in v.lower() or 'green card' in v.lower()):
                        filt.append(j)
                    elif visa == 'E-3' and ('e-3' in v.lower() or 'e3' in v.lower()):
                        filt.append(j)
                return format_job_results(filt, f"{visa} jobs")
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Visa filter handler failed: {e}")
                # continue to other handlers

        # Fast-path: detect explicit wage queries and return direct results (avoid LC ReAct traces)
        wage_info = self._extract_wage(query)
        if wage_info is not None:
            wage, op = wage_info
            try:
                if op == 'gte':
                    results = self.data_service.get_high_wage_jobs(wage, 40)
                    title = f"jobs ($≥{wage:,.0f})"
                else:
                    # No direct API for <=, fetch a larger sample and filter client-side
                    sample = self.data_service.get_sample_joined_data(200)
                    results = [j for j in sample if 0 < (j.get('wage') or 0) <= wage]
                    title = f"jobs ($≤{wage:,.0f})"
                return format_job_results(results, title)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Direct wage handler failed: {e}")
                # continue to normal routing
        
        # Analyze if this is an immigration-focused query
        if self._is_immigration_query(query):
            print("🎓 Using Immigration-Focused Analysis...")
            return self.immigration_agent.provide_immigration_guidance(query)
        else:
            print("🤖 Using General LangChain Agent...")
            result = run_agent_query(self.langchain_agent, query)
            if not result or not str(result).strip():
                # Hard fallback if nothing returned
                try:
                    from working_agent import WorkingLCAAgent
                    return WorkingLCAAgent().analyze_and_execute(query)
                except Exception as _:
                    return "❌ Sorry, I couldn't produce a result. Try a simpler query like 'High-paying jobs $120k+'."
            return result

    def _extract_faq_intent(self, query: str) -> Optional[Tuple[str, Dict[str, str]]]:
        q = self._normalize_text(query)
        # Top petitioners 2025
        if ("which companies" in q or "top" in q or "filed the most" in q or "most petitions" in q) \
           and ("2025" in q or "fy 2025" in q) \
           and (re.search(r"\bh[-\u2010-\u2015]?\s?1b\b", q) is not None):
            return ("top_h1b_companies_2025", {})
        # Majors most likely to get approvals
        if ("which majors" in q or "majors" in q) \
           and (re.search(r"\bh[-\u2010-\u2015]?\s?1b\b", q) or "approve" in q or "approved" in q or "approval" in q or "certif" in q):
            return ("majors_approval", {})
        # School sponsors
        if ("sponsor" in q or "sponsored" in q) and ("school" in q or "university" in q):
            # try to pull university token after 'from' or 'at'
            m = re.search(r"(?:from|at)\s+([A-Za-z0-9&.,'()\-\s]{3,})", query, flags=re.I)
            uni = m.group(1).strip() if m else ""
            return ("school_sponsors", {"university": uni})
        # Company H-1B counts
        if ("how many" in q or "how much" in q or "number" in q) \
           and ("company" in q or "employer" in q or "from" in q) \
           and (re.search(r"\bh[-\u2010-\u2015]?\s?1b\b", q) or "petition" in q or "lca" in q):
            m = re.search(r"(?:company|employer|from)\s+([A-Za-z0-9&.,'()\-\s]{2,})", query, flags=re.I)
            comp = m.group(1).strip() if m else ""
            return ("company_counts", {"company": comp})
        return None

    def _normalize_text(self, s: str) -> str:
        """Lowercase, replace Unicode hyphens with '-', normalize quotes and collapse whitespace."""
        t = s.lower()
        # Replace various unicode dashes with ASCII '-'
        t = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015]", "-", t)
        # Normalize curly quotes to straight quotes
        t = t.replace("\u2018", "'").replace("\u2019", "'")
        t = t.replace("\u201c", '"').replace("\u201d", '"')
        # Collapse whitespace
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _answer_faq_with_sources(self, intent: str, args: Dict[str, str]) -> str:
        lines = []
        if intent == "top_h1b_companies_2025":
            lines.append("📊 Top H-1B Petitioners (FY 2025)")
            lines.append("=" * 60)
            lines.append("")
            srcs = get_top_h1b_companies_2025()
            lines.append("• This summary lists leading petitioners for FY 2025.")
            lines.append("")
            lines.append("Sources:")
            for s in srcs:
                snippet = f" — {s.snippet}" if s.snippet else ""
                lines.append(f"• {s.title}: {s.url}{snippet}")
            return "\n".join(lines).rstrip()

        if intent == "majors_approval":
            lines.append("🎓 Majors With Higher H-1B Certification Odds")
            lines.append("=" * 60)
            lines.append("")
            lines.append("• Studies suggest CS/STEM and PhD holders have higher certification rates.")
            lines.append("• Lower odds observed for associate degrees and some non-STEM fields.")
            lines.append("")
            lines.append("Sources:")
            for s in get_h1b_majors_study():
                lines.append(f"• {s.title}: {s.url}")
            return "\n".join(lines).rstrip()

        if intent == "school_sponsors":
            univ = (args.get("university") or "").strip()
            lines.append("🏫 School H-1B Sponsorships")
            lines.append("=" * 60)
            lines.append("")
            if not univ:
                lines.append("• Please share your university (e.g., 'University of Michigan').")
            else:
                lines.append(f"• School: {univ}")
            lines.append("• Use these sources to view recent LCA filings and sponsors.")
            lines.append("")
            lines.append("Sources:")
            for s in get_school_sponsors_links(univ or "your university"):
                lines.append(f"• {s.title}: {s.url}")
            return "\n".join(lines).rstrip()

        if intent == "company_counts":
            comp = (args.get("company") or "").strip()
            lines.append("🏢 Employer H-1B Petition Counts")
            lines.append("=" * 60)
            lines.append("")
            if not comp:
                lines.append("• Please provide the company legal name.")
            else:
                lines.append(f"• Company: {comp}")
            lines.append("• Use these to view recent annual counts (MyVisaJobs) and multi-year totals (H1BGrader).")
            lines.append("")
            lines.append("Sources:")
            for s in get_company_h1b_links(comp or "your company"):
                lines.append(f"• {s.title}: {s.url}")
            return "\n".join(lines).rstrip()

        return "No FAQ handler matched."

    def _extract_wage(self, s: str):
        """Extract (wage, op) where op in {'gte','lte'} from free text.
        Supports patterns: 'less than/under/below 100', 'more than/above/over 120k', '$120,000', '100$'.
        """
        # First detect explicit less-than intent
        less = re.search(r"(?<![a-z0-9])(?:less than|under|below)\s*\$?(\d[\d,]*)(k|\$)?(?![a-z])", s)
        if less:
            num = less.group(1).replace(',', '')
            try:
                val = float(num)
            except:
                val = None
            if val is not None:
                if (less.group(2) and 'k' in less.group(2)) or val < 1000:
                    val *= 1000
                return (val, 'lte')
        # Then detect explicit more-than intent
        more = re.search(r"(?<![a-z0-9])(?:more than|above|over|at least)\s*\$?(\d[\d,]*)(k|\$)?(?![a-z])", s)
        if more:
            num = more.group(1).replace(',', '')
            try:
                val = float(num)
            except:
                val = None
            if val is not None:
                if (more.group(2) and 'k' in more.group(2)) or val < 1000:
                    val *= 1000
                return (val, 'gte')

    def _extract_visa(self, q: str) -> str:
        """Detect visa-intent. Returns one of {'H-1B','PERM','E-3'} or None."""
        # q is normalized already
        if re.search(r"h\s*-?\s*1\s*-?\s*b", q):
            return 'H-1B'
        if 'perm' in q or 'green card' in q or 'greencard' in q:
            return 'PERM'
        if re.search(r"e\s*-?\s*3", q) or 'e3' in q:
            return 'E-3'
        return None
        # Generic amount without operator -> default to gte (common user intent)
        m = re.search(r"(?<![a-z0-9])\$?\s*(\d[\d,]*)(k|\$)?(?![a-z])", s)
        if not m:
            return None
        num = m.group(1).replace(',', '')
        try:
            val = float(num)
        except:
            return None
        if (m.group(2) and 'k' in m.group(2)) or val < 1000:
            val *= 1000
        return (val, 'gte')
    
    def _is_immigration_query(self, query: str) -> bool:
        """Detect if query needs immigration context"""
        immigration_keywords = [
            'opt', 'f-1', 'student', 'visa', 'sponsor', 'green card', 'perm',
            'h-1b', 'h1b', 'immigration', 'pathway', 'timeline', 'process',
            'international student', 'work authorization', 'permanent residency'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in immigration_keywords)
    
    def get_company_profile(self, company_name: str) -> str:
        """Get detailed company immigration profile"""
        return self.immigration_agent.get_company_immigration_profile(company_name)

def main():
    """Main interactive loop"""
    print("🌟 Immigration-Aware AI Agent for International Students")
    print("=" * 70)
    print("This agent understands your F-1 → OPT → H-1B → Green Card journey!")
    print("Ask about companies, locations, salaries, or immigration processes.")
    print("=" * 70)
    
    # Load environment
    if not load_dotenv():
        print("⚠️ Warning: .env file not found. Make sure your Supabase credentials are set.")
    
    # Initialize enhanced agent
    try:
        agent = EnhancedImmigrationAgent()
        print("✅ Enhanced Immigration Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Show available commands
    print("\n📋 Available Commands:")
    print("• Ask about companies: 'Tell me about Google's H-1B sponsorship'")
    print("• Location queries: 'Best H-1B sponsors in San Francisco'")
    print("• Salary research: 'High-paying PERM jobs for software engineers'")
    print("• Immigration guidance: 'Help me understand the OPT to H-1B process'")
    print("• Company profiles: '/profile [company_name]'")
    print("• Help: '/help'")
    print("• Quit: '/quit'")
    print()
    
    # Interactive loop
    while True:
        try:
            query = input("🗣️ Your question: ").strip()
            
            if not query:
                continue
                
            # Handle special commands
            if query.lower() in ['/quit', '/exit', 'quit', 'exit']:
                print("👋 Good luck with your immigration journey!")
                break
                
            elif query.lower() in ['/help', 'help']:
                show_help()
                continue
                
            elif query.lower().startswith('/profile '):
                company = query[9:].strip()
                if company:
                    print(f"\n📊 Analyzing {company}...")
                    result = agent.get_company_profile(company)
                    print(result)
                else:
                    print("Please specify a company name: /profile Google")
                continue
            
            # Process regular query
            print(f"\n🔍 Analyzing your query...")
            result = agent.process_query(query)
            print(f"\n📋 Response:")
            print(result)
            print("\n" + "─" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Good luck with your immigration journey!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try rephrasing your question.")

def show_help():
    """Show detailed help information"""
    help_text = """
🎓 **Immigration Agent Help Guide**

**For OPT Students:**
• "Companies that sponsor H-1B in [city]"
• "STEM-friendly employers for software engineers"
• "Timeline for H-1B application process"

**For H-1B Holders:**
• "Companies that sponsor green cards"
• "PERM processing times by company"
• "EB-2 vs EB-3 category differences"

**General Queries:**
• "High-paying tech jobs in San Francisco"
• "Compare salaries: Google vs Microsoft"
• "Immigration pathway from F-1 to green card"

**Company Analysis:**
• Use `/profile [company]` for detailed immigration analysis
• Example: `/profile Google`

**Data Sources:**
• H-1B data from DOL LCA filings
• Green card data from DOL PERM disclosures
• Real government data, updated regularly

**Tips:**
• Be specific about your visa stage (OPT, H-1B, etc.)
• Mention your field (software, finance, etc.)
• Ask about specific locations or companies
    """
    print(help_text)

def single_query_mode():
    """Handle single query from command line"""
    if len(sys.argv) < 2:
        print("Usage: python immigration_main_agent.py 'your question here'")
        return
    
    query = ' '.join(sys.argv[1:])
    
    # Load environment
    load_dotenv()
    
    try:
        agent = EnhancedImmigrationAgent()
        print(f"🗣️ Query: {query}")
        print("=" * 60)
        result = agent.process_query(query)
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check if running in single query mode
    if len(sys.argv) > 1:
        single_query_mode()
    else:
        main()
