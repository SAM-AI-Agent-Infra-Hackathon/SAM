import re
import httpx
from typing import List, Optional, Dict

# Simple source record
class Source:
    def __init__(self, title: str, url: str, snippet: Optional[str] = None):
        self.title = title
        self.url = url
        self.snippet = snippet or ""

    def to_dict(self) -> Dict[str, str]:
        return {"title": self.title, "url": self.url, "snippet": self.snippet}


def _fetch(url: str, timeout: float = 8.0) -> Optional[str]:
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (compatible; SamImmigrationBot/1.0)"
        }) as client:
            r = client.get(url)
            if r.status_code == 200:
                return r.text
    except Exception:
        return None
    return None


def get_top_h1b_companies_2025() -> List[Source]:
    """Attempt to retrieve top H-1B petitioners FY2025 from public sources.
    Returns list of Source with optional snippets.
    """
    sources: List[Source] = []
    # MyVisaJobs report (URL pattern may change, keep generic reports page as fallback)
    report_urls = [
        "https://www.myvisajobs.com/Reports/",  # hub
        # Known direct pages sometimes exist per year; keep hub primary
    ]
    for url in report_urls:
        html = _fetch(url)
        if not html:
            continue
        # Best-effort: find lines that look like "Company – 12,345 petitions"
        matches = re.findall(r"([A-Za-z0-9&.,'()\-\s]{3,})\s[–-]\s([\d,]{3,})\s+petitions", html, flags=re.I)
        if matches:
            top5 = matches[:5]
            bullets = [f"{name.strip()} – {count.replace(',', '') if count else count} petitions" for name, count in top5]
            sources.append(Source("MyVisaJobs Reports", url, snippet="; ".join(bullets)))
            break
    # Add the hub link at minimum
    if not sources:
        sources.append(Source("MyVisaJobs Reports", "https://www.myvisajobs.com/Reports/", snippet="See latest H-1B Visa Report"))
    return sources


def get_h1b_majors_study() -> List[Source]:
    """Return sources discussing majors vs certification odds (best-effort)."""
    sources: List[Source] = []
    # Example arXiv query URL (no API):
    arxiv_urls = [
        "https://arxiv.org/",  # hub as fallback
    ]
    for url in arxiv_urls:
        html = _fetch(url)
        if html:
            sources.append(Source("arXiv", url, snippet="Academic studies on H-1B/LCA trends"))
            break
    if not sources:
        sources.append(Source("arXiv", "https://arxiv.org/", snippet="Search for H-1B approval rate by major"))
    return sources


def get_school_sponsors_links(university: str) -> List[Source]:
    """Return plausible sources for school sponsorships (links + hints)."""
    uni_q = re.sub(r"\s+", "+", university.strip())
    links = [
        Source("MyVisaJobs University Search", f"https://www.myvisajobs.com/University/{uni_q}/"),
        Source("Google: MyVisaJobs {university}", f"https://www.google.com/search?q=site:myvisajobs.com+{uni_q}+LCA"),
    ]
    return links


def get_company_h1b_links(company: str) -> List[Source]:
    comp_q = re.sub(r"\s+", "+", company.strip())
    links = [
        Source("MyVisaJobs Employer Search", f"https://www.myvisajobs.com/Employer/{comp_q}/"),
        Source("H1BGrader Employer Search", f"https://h1bgrader.com/employer/{comp_q}"),
        Source("Google: Employer H-1B LCAs", f"https://www.google.com/search?q=site:myvisajobs.com+{comp_q}+H-1B+petitions"),
    ]
    return links
