import re
import httpx
from typing import List, Optional, Dict
from bs4 import BeautifulSoup

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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }) as client:
            r = client.get(url)
            if r.status_code == 200:
                return r.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
    return None


def get_top_h1b_companies_2025() -> List[Source]:
    """Scrape MyVisaJobs for top H-1B petitioners for the latest year.
    Returns a list of Source objects with structured data in the snippet.
    """
    print("ATTEMPTING LIVE SCRAPE: Fetching top H-1B companies...")
    sources: List[Source] = []
    url = "https://www.myvisajobs.com/reports/h1b/"
    html = _fetch(url)

    if not html:
        print("SCRAPE FAILED: Could not fetch HTML from", url)
        sources.append(Source("MyVisaJobs Reports", url, snippet="Could not fetch report page."))
        return sources


def get_school_h1b_counts(university: str, fiscal_year: int) -> List[Source]:
    """Scrape MyVisaJobs employer page for a university to get FY-specific H-1B metrics.

    Extracts for the given fiscal year (e.g., 2024):
    - FY{year}_Petitions, FY{year}_Approved, FY{year}_Denied
    - AvgSalary if a phrase like 'average salary was $79,734' appears
    - LCA_Total if available

    Returns a single Source with key=value snippet lines for easy parsing downstream.
    """
    uni = university.strip()
    # Build two candidate URLs: SEO slug and legacy encoded
    def _slugify(name: str) -> str:
        s = name.lower().strip()
        # Remove common stop-words
        s = re.sub(r"\b(of|the|and|&|'s)\b", "", s)
        # Remove non-alphanum except spaces
        s = re.sub(r"[^a-z0-9\s]", "", s)
        # Collapse spaces
        s = re.sub(r"\s+", " ", s).strip()
        # Replace spaces with dashes
        s = s.replace(" ", "-")
        # Collapse multiple dashes
        s = re.sub(r"-+", "-", s)
        return s

    slug = _slugify(uni)
    url_slug = f"https://www.myvisajobs.com/employer/{slug}/"
    uni_q = re.sub(r"\s+", "+", uni)
    url_legacy = f"https://www.myvisajobs.com/Employer/{uni_q}/"

    # Try slug URL first, then legacy
    print(f"ATTEMPTING LIVE SCRAPE: University employer page (slug) for {uni} -> {url_slug}")
    html = _fetch(url_slug)
    final_url = url_slug
    if not html:
        print(f"Slug fetch failed, trying legacy URL -> {url_legacy}")
        html = _fetch(url_legacy)
        final_url = url_legacy
    sources: List[Source] = []
    if not html:
        print("SCRAPE FAILED: university page HTML fetch failed")
        sources.append(Source(f"MyVisaJobs University: {uni}", url_slug, snippet="error=fetch_failed"))
        return sources

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(" ", strip=True)

    # LCA total
    lca_total = None
    m_lca = re.search(r"LCA for H-1B:\s*([\d,]+)", text, re.IGNORECASE)
    if m_lca:
        try:
            lca_total = int(m_lca.group(1).replace(',', ''))
        except Exception:
            pass

    # FY-specific petitions and outcomes
    fy = int(fiscal_year)
    fy_petitions = fy_approved = fy_denied = None
    fy_pattern = (
        rf"fiscal year\s*{fy}[^\d]{{0,60}}filed\s*([\d,]{{1,7}})\s*Form\s*I-129\s*petitions.*?([\d,]{{1,7}})\s*were\s*approved.*?([\d,]{{1,7}})\s*were\s*denied"
    )
    m_fy = re.search(fy_pattern, text, re.IGNORECASE | re.DOTALL)
    if m_fy:
        try:
            fy_petitions = int(m_fy.group(1).replace(',', ''))
            fy_approved = int(m_fy.group(2).replace(',', ''))
            fy_denied = int(m_fy.group(3).replace(',', ''))
        except Exception:
            pass

    # Average salary (robust variations)
    avg_salary = None
    m_avg = re.search(r"average salary (?:was|of)?\s*\$?([\d,]+)", text, re.IGNORECASE)
    if m_avg:
        try:
            avg_salary = int(m_avg.group(1).replace(',', ''))
        except Exception:
            pass

    # Possible industry hint
    industry = None
    m_ind = re.search(r"(education(?:al)?\s+services)", text, re.IGNORECASE)
    if m_ind:
        industry = m_ind.group(1)

    # Build snippet
    lines = [f"University={uni}", f"FY={fy}"]
    if lca_total is not None:
        lines.append(f"LCA_Total={lca_total}")
    if fy_petitions is not None:
        lines.append(f"FY{fy}_Petitions={fy_petitions}")
    if fy_approved is not None:
        lines.append(f"FY{fy}_Approved={fy_approved}")
    if fy_denied is not None:
        lines.append(f"FY{fy}_Denied={fy_denied}")
    if avg_salary is not None:
        lines.append(f"AvgSalary={avg_salary}")
    if industry:
        lines.append(f"Industry={industry}")

    snippet = "\n".join(lines)
    if len(lines) <= 2:
        snippet += "\ninfo=No structured FY data found; check page manually."

    sources.append(Source(f"MyVisaJobs University: {uni}", final_url, snippet=snippet))
    return sources
    print("SCRAPE STATUS: HTML fetched successfully.")

    soup = BeautifulSoup(html, 'html.parser')
    # The data table has a class 'tbl'. We will search for it directly.
    table = soup.find('table', class_='tbl')
    if not table:
        print("SCRAPE FAILED: Could not find the data table with class='tbl'.")
        sources.append(Source("MyVisaJobs Reports", url, snippet="Could not find the data table on the page."))
        return sources
    print("SCRAPE STATUS: Found data table.")

    results = []
    rows = table.find_all('tr')
    print(f"SCRAPE STATUS: Found {len(rows)} rows in the table.")

    # Skip header row (tr[0]) and process the next 5 data rows
    for row in rows[1:6]:
        cols = row.find_all('td')
        if len(cols) >= 4:
            try:
                company = cols[1].text.strip()
                petitions = cols[2].text.strip().replace(',', '')
                salary = cols[3].text.strip()
                results.append(f"{company}|{petitions}|{salary}")
            except (IndexError, AttributeError) as e:
                print(f"SCRAPE WARNING: Skipping malformed row. Error: {e}")
                continue

    if results:
        print(f"SCRAPE SUCCESS: Extracted {len(results)} records.")
        snippet = "\n".join(results)
        sources.append(Source("MyVisaJobs Top H-1B Sponsors", url, snippet=snippet))
    else:
        print("SCRAPE FAILED: Could not parse any sponsor data from the table.")
        sources.append(Source("MyVisaJobs Reports", url, snippet="Failed to parse sponsor data from table."))

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


def get_company_h1b_counts(company: str) -> List[Source]:
    """Scrape MyVisaJobs employer page for H-1B counts for a given company.

    Parses:
    - LCA for H-1B total (typically last 3 fiscal years shown in header)
    - FY 2025 I-129 petitions (approved/denied) if present in Overview

    Returns a single Source with snippet as key=value lines, e.g.:
        Company=Apple
        LCA_Total=12680
        FY2025_Petitions=2301
        FY2025_Approved=2282
        FY2025_Denied=19
    """
    comp = company.strip()
    comp_q = re.sub(r"\s+", "+", comp)
    url = f"https://www.myvisajobs.com/Employer/{comp_q}/"
    print(f"ATTEMPTING LIVE SCRAPE: Employer page for {comp} -> {url}")
    html = _fetch(url)
    sources: List[Source] = []
    if not html:
        print("SCRAPE FAILED: employer page HTML fetch failed")
        sources.append(Source(f"MyVisaJobs Employer: {comp}", url, snippet="error=fetch_failed"))
        return sources

    text = BeautifulSoup(html, 'html.parser').get_text(" ", strip=True)

    # Patterns
    lca_total = None
    m_lca = re.search(r"LCA for H-1B:\s*([\d,]+)", text, re.IGNORECASE)
    if m_lca:
        try:
            lca_total = int(m_lca.group(1).replace(',', ''))
        except Exception:
            pass

    fy_petitions = fy_approved = fy_denied = None
    # Example: "in fiscal year 2025, Apple filed 2301 Form I-129 petitions... 2282 were approved and 19 were denied"
    m_fy = re.search(
        r"fiscal year\s*2025[^\d]{0,40}filed\s*([\d,]{1,6})\s*Form\s*I-129\s*petitions.*?([\d,]{1,6})\s*were\s*approved.*?([\d,]{1,6})\s*were\s*denied",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if m_fy:
        try:
            fy_petitions = int(m_fy.group(1).replace(',', ''))
            fy_approved = int(m_fy.group(2).replace(',', ''))
            fy_denied = int(m_fy.group(3).replace(',', ''))
        except Exception:
            pass

    # Build snippet lines
    lines = [f"Company={comp}"]
    if lca_total is not None:
        lines.append(f"LCA_Total={lca_total}")
    if fy_petitions is not None:
        lines.append(f"FY2025_Petitions={fy_petitions}")
    if fy_approved is not None:
        lines.append(f"FY2025_Approved={fy_approved}")
    if fy_denied is not None:
        lines.append(f"FY2025_Denied={fy_denied}")

    snippet = "\n".join(lines)
    if len(lines) == 1:
        # No data parsed, include a hint
        snippet += "\ninfo=No structured counts found; check page manually."

    sources.append(Source(f"MyVisaJobs Employer: {comp}", url, snippet=snippet))
    return sources
