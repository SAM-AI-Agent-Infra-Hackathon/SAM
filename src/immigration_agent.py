#!/usr/bin/env python3
"""
Immigration-Focused AI Agent for International Students
======================================================

This agent understands the F-1 → OPT → H-1B → Green Card pathway and provides
contextual advice for international students navigating US immigration law.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from services.data_service import DataService
from tools import get_sync_tools

logger = logging.getLogger(__name__)

class ImmigrationAgent:
    """AI Agent specialized for international student immigration guidance"""
    
    def __init__(self, data_service: Optional[DataService] = None):
        self.data_service = data_service or DataService()
        self.tools = get_sync_tools()
        
    def analyze_immigration_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to understand immigration context and intent"""
        query_lower = query.lower()
        
        context = {
            'visa_stage': self._detect_visa_stage(query_lower),
            'location_focus': self._extract_location(query_lower),
            'industry_focus': self._extract_industry(query_lower),
            'salary_concern': self._detect_salary_concern(query_lower),
            'timeline_concern': self._detect_timeline_concern(query_lower),
            'company_specific': self._extract_company(query_lower)
        }
        
        return context
    
    def _detect_visa_stage(self, query: str) -> str:
        """Detect which visa stage the student is asking about"""
        if any(term in query for term in ['opt', 'f-1', 'student', 'graduate']):
            return 'opt_stage'
        elif any(term in query for term in ['h-1b', 'h1b', 'lottery', 'sponsor']):
            return 'h1b_stage'
        elif any(term in query for term in ['green card', 'perm', 'permanent', 'eb-2', 'eb-3']):
            return 'green_card_stage'
        elif any(term in query for term in ['pathway', 'journey', 'timeline', 'process']):
            return 'full_pathway'
        return 'general'
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location preferences from query"""
        cities = ['san francisco', 'new york', 'seattle', 'chicago', 'boston', 'austin', 'los angeles']
        for city in cities:
            if city in query:
                return city.title()
        return None
    
    def _extract_industry(self, query: str) -> Optional[str]:
        """Extract industry focus from query"""
        industries = {
            'tech': ['software', 'engineer', 'developer', 'tech', 'google', 'microsoft', 'amazon'],
            'finance': ['finance', 'banking', 'analyst', 'goldman', 'jpmorgan'],
            'consulting': ['consulting', 'consultant', 'mckinsey', 'bain', 'bcg'],
            'healthcare': ['healthcare', 'medical', 'pharma', 'biotech']
        }
        
        for industry, keywords in industries.items():
            if any(keyword in query for keyword in keywords):
                return industry
        return None
    
    def _detect_salary_concern(self, query: str) -> bool:
        """Detect if query is about salary/wage requirements"""
        return any(term in query for term in ['salary', 'wage', 'pay', 'money', 'prevailing'])
    
    def _detect_timeline_concern(self, query: str) -> bool:
        """Detect if query is about timing/deadlines"""
        return any(term in query for term in ['when', 'timeline', 'deadline', 'how long', 'time'])
    
    def _extract_company(self, query: str) -> Optional[str]:
        """Extract specific company mentions"""
        companies = ['google', 'microsoft', 'amazon', 'apple', 'meta', 'netflix', 'tesla']
        for company in companies:
            if company in query:
                return company.title()
        return None
    
    def provide_immigration_guidance(self, query: str) -> str:
        """Provide contextual immigration guidance based on query analysis"""
        context = self.analyze_immigration_query(query)
        
        # Build response based on context
        response_parts = []
        
        # Add immigration context header
        response_parts.append(self._get_context_header(context))
        
        # Get relevant data
        data_response = self._get_relevant_data(context, query)
        response_parts.append(data_response)
        
        # Add immigration advice
        advice = self._get_immigration_advice(context)
        if advice:
            response_parts.append(advice)
        
        return "\n\n".join(response_parts)
    
    def _get_context_header(self, context: Dict[str, Any]) -> str:
        """Generate contextual header based on visa stage"""
        stage = context['visa_stage']
        
        headers = {
            'opt_stage': "🎓 **OPT Stage Guidance** - Planning your post-graduation work authorization",
            'h1b_stage': "🏢 **H-1B Stage Guidance** - Finding sponsoring employers",
            'green_card_stage': "🟢 **Green Card Stage Guidance** - Permanent residency pathway",
            'full_pathway': "🛤️ **Complete Immigration Pathway** - F-1 to Green Card journey",
            'general': "📋 **Immigration Data Analysis**"
        }
        
        return headers.get(stage, headers['general'])
    
    def _get_relevant_data(self, context: Dict[str, Any], query: str) -> str:
        """Get relevant data based on context"""
        try:
            # Fetch LCA and PERM separately and format into two distinct sections
            def _nz(val):
                if val is None:
                    return "Not specified"
                if isinstance(val, str):
                    v = re.sub(r"\s+", " ", val).strip()
                    return v if v else "Not specified"
                return str(val)

            def _format_section(title: str, results: List[Dict[str, Any]], visa_label: str, max_items: int = 10) -> str:
                lines: List[str] = []
                lines.append(f"📊 {title} – {len(results)} found")
                lines.append("=" * 60)
                lines.append("")
                shown = results[:max_items]
                for idx, job in enumerate(shown, 1):
                    company = _nz(job.get('company'))
                    role = _nz(job.get('job_title'))
                    city = _nz(job.get('city'))
                    state = _nz(job.get('state'))
                    wage_val = job.get('wage')
                    salary = f"${wage_val:,.0f}" if isinstance(wage_val, (int, float)) and wage_val > 0 else "Not specified"
                    # Location normalization
                    if city == "Not specified" and state != "Not specified":
                        loc = state
                    elif city != "Not specified" and state == "Not specified":
                        loc = city
                    elif city == "Not specified" and state == "Not specified":
                        loc = "Not specified"
                    else:
                        loc = f"{city}, {state}"
                    # One entry block
                    lines.append(f"{idx}. 🏢 {company}")
                    lines.append("")
                    lines.append(f"   📋 Position: {role}")
                    lines.append(f"   📍 Location: {loc}")
                    lines.append(f"   💰 Salary: {salary}")
                    lines.append(f"   🛂 Visa: {visa_label}")
                    lines.append("")
                if len(results) > max_items:
                    lines.append(f"... and {len(results) - max_items} more results")
                return "\n".join(lines).rstrip()

            city = context['location_focus']
            company = context['company_specific']

            # Branches
            if city:
                lca = self.data_service.get_filings_by_city(city, limit=30)
                perm = self.data_service.get_perm_by_city(city, limit=30)
                lca_sec = _format_section("Recent H-1B Filings (LCA Data)", lca, "H-1B")
                perm_sec = _format_section("Recent Green Card Filings (PERM Data)", perm, "PERM")
                return f"{lca_sec}\n\n{perm_sec}"

            if company:
                lca = self.data_service.get_jobs_by_company(company, limit=30)
                perm = self.data_service.get_perm_by_company(company, limit=30)
                lca_sec = _format_section("Recent H-1B Filings (LCA Data)", lca, "H-1B")
                perm_sec = _format_section("Recent Green Card Filings (PERM Data)", perm, "PERM")
                return f"{lca_sec}\n\n{perm_sec}"

            if context['salary_concern']:
                lca = self.data_service.get_high_wage_jobs(100000, limit=30)
                perm = self.data_service.get_perm_high_wage_jobs(100000, limit=30)
                lca_sec = _format_section("High-wage H-1B Filings (LCA Data)", lca, "H-1B")
                perm_sec = _format_section("High-wage Green Card Filings (PERM Data)", perm, "PERM")
                return f"{lca_sec}\n\n{perm_sec}"

            # Default samples
            lca = self.data_service.get_sample_joined_data(10)
            perm = self.data_service.get_sample_perm_data(10)
            lca_sec = _format_section("Recent H-1B Filings (LCA Data)", lca, "H-1B")
            perm_sec = _format_section("Recent Green Card Filings (PERM Data)", perm, "PERM")
            return f"{lca_sec}\n\n{perm_sec}"
                
        except Exception as e:
            logger.error(f"Error getting relevant data: {e}")
            return "Sorry, I encountered an error retrieving the data. Please try a more specific query."
    
    def _get_immigration_advice(self, context: Dict[str, Any]) -> str:
        """Provide stage-specific immigration advice"""
        stage = context['visa_stage']
        
        advice_map = {
            'opt_stage': """
**💡 OPT Stage Tips:**
• Focus on companies with high H-1B approval rates
• STEM students get 24-month extension - use it wisely
• Start H-1B prep early (applications due in March)
• Consider companies that also file PERM applications
            """,
            
            'h1b_stage': """
**💡 H-1B Stage Tips:**
• H-1B lottery odds vary by company size and filing history
• Look for companies that file multiple applications
• Consider consulting firms for higher lottery chances
• Backup plan: Look into L-1, O-1, or other visa options
            """,
            
            'green_card_stage': """
**💡 Green Card Stage Tips:**
• PERM process takes 1-3 years depending on country of birth
• EB-2 vs EB-3 categories have different wait times
• Some companies prefer internal transfers for PERM
• Consider EB-1 if you qualify (extraordinary ability)
            """,
            
            'full_pathway': """
**💡 Complete Pathway Strategy:**
1. **OPT (1-3 years)**: Build skills, network, find H-1B sponsors
2. **H-1B (up to 6 years)**: Prove value, get PERM sponsorship
3. **PERM Process (1-3 years)**: Maintain status, prepare for delays
4. **Green Card**: Adjust status or consular processing

**Key Success Factors:**
• Choose employers with proven immigration support
• Maintain legal status throughout
• Build strong case for permanent residency
• Have backup plans at each stage
            """
        }
        
        return advice_map.get(stage, "")
    
    def get_company_immigration_profile(self, company_name: str) -> str:
        """Get comprehensive immigration profile for a company"""
        try:
            # Get both H-1B and PERM data
            lca_jobs = self.data_service.get_jobs_by_company(company_name, 50)
            perm_jobs = self.data_service.get_perm_by_company(company_name, 50)
            
            # Analyze the data
            total_h1b = len(lca_jobs)
            total_perm = len(perm_jobs)
            
            # Calculate average wages
            def _avg_wage(jobs):
                wages = [j.get('wage') for j in jobs if isinstance(j.get('wage'), (int, float)) and j.get('wage') > 0]
                return (sum(wages) / len(wages)) if wages else None

            avg_h1b_wage = _avg_wage(lca_jobs)
            avg_perm_wage = _avg_wage(perm_jobs)

            def _fmt_money(v):
                return f"${v:,.0f}" if isinstance(v, (int, float)) and v > 0 else "Not specified"

            def _rating(label_count: int, good_thresh: int, great_thresh: int, kind: str) -> str:
                if label_count >= great_thresh:
                    return "🟢 Excellent"
                if label_count >= good_thresh:
                    return "🟡 Good"
                if label_count > 0:
                    return "🟠 Limited"
                return "🔴 None"

            conv_rate = f"{(total_perm/total_h1b*100):.1f}%" if total_h1b > 0 else "Not specified"

            # Build profile
            profile = f"""
**🏢 Immigration Profile: {company_name.title()}**

**📊 H-1B Sponsorship:**
• Total H-1B filings: {total_h1b if total_h1b > 0 else 'Not specified'}
• Average H-1B wage: {_fmt_money(avg_h1b_wage)}
• H-1B sponsor rating: {_rating(total_h1b, good_thresh=6, great_thresh=21, kind='H-1B')}

**📊 Green Card (PERM) Sponsorship:**
• Total PERM filings: {total_perm if total_perm > 0 else 'Not specified'}
• Average PERM wage: {_fmt_money(avg_perm_wage)}
• PERM sponsor rating: {_rating(total_perm, good_thresh=3, great_thresh=11, kind='PERM')}

**📊 Immigration Friendliness Score:**
• H-1B → PERM conversion rate: {conv_rate}
• Overall rating: {('🟢 Excellent' if total_perm > 10 and total_h1b > 20 else '🟡 Good' if total_perm > 2 or total_h1b > 10 else '🔴 Limited')}

**💡 Recommendation:**
{self._get_company_recommendation(total_h1b, total_perm)}
            """
            
            return profile.strip()
            
        except Exception as e:
            return f"Sorry, I couldn't analyze the immigration profile for {company_name}. Error: {str(e)}"
    
    def _get_company_recommendation(self, h1b_count: int, perm_count: int) -> str:
        """Generate recommendation with required symbol + short reason"""
        if h1b_count >= 21 and perm_count >= 11:
            return "✅ Strong sponsor – Consistent H-1B + PERM history"
        if h1b_count >= 11 and perm_count >= 6:
            return "✅ Good option – Solid H-1B and active green card pathway"
        if h1b_count >= 6 and perm_count >= 1:
            return "⚠️ Mixed – H-1B present, limited green card activity"
        if h1b_count >= 1:
            return "⚠️ Weak – H-1B activity but little/no green card history"
        return "❌ Not recommended – No visible immigration sponsorship"

# Test function
def test_immigration_agent():
    """Test the immigration-focused agent"""
    agent = ImmigrationAgent()
    
    test_queries = [
        "I'm on OPT and looking for H-1B sponsors in San Francisco",
        "What companies sponsor green cards for software engineers?",
        "Tell me about Google's immigration sponsorship",
        "I need help understanding the F-1 to green card pathway"
    ]
    
    for query in test_queries:
        print(f"\n🗣️ Query: {query}")
        print("=" * 60)
        response = agent.provide_immigration_guidance(query)
        print(response)
        print("=" * 60)

if __name__ == "__main__":
    test_immigration_agent()
