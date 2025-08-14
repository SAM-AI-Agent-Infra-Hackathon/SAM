from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

import requests
from bs4 import BeautifulSoup

BASE_PAGE_URL = "https://www.dol.gov/agencies/eta/foreign-labor/performance"
BASE_FILE_ROOT = "https://www.dol.gov"


@dataclass(order=True)
class FiscalQuarter:
    """Representation of a fiscal year and quarter."""

    year: int
    quarter: int

    @classmethod
    def parse_from_filename(cls, filename: str) -> Optional["FiscalQuarter"]:
        """Extract fiscal year and quarter from an LCA disclosure filename."""
        # Match strictly LCA disclosure naming
        match = re.search(r"^LCA_Disclosure_Data_FY(\d{4})_Q(\d)\.xlsx$", filename, re.IGNORECASE)
        if not match:
            return None
        year = int(match.group(1))
        quarter = int(match.group(2))
        return cls(year=year, quarter=quarter)

    def __str__(self) -> str:
        return f"FY{self.year} Q{self.quarter}"


def fetch_performance_page() -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0 Safari/537.36"
        )
    }
    resp = requests.get(BASE_PAGE_URL, headers=headers)
    resp.raise_for_status()
    return resp.text


def extract_lca_links(html: str) -> Iterable[Tuple[FiscalQuarter, str]]:
    """Yield only LCA Excel disclosure links."""
    soup = BeautifulSoup(html, "html.parser")
    for anchor in soup.find_all("a", href=True):
        href: str = anchor["href"]
        filename = os.path.basename(href)
        fq = FiscalQuarter.parse_from_filename(filename)
        if fq is None:
            continue
        if not href.startswith("http"):
            link = BASE_FILE_ROOT + href
        else:
            link = href
        yield fq, link


def choose_latest_quarter(links: Iterable[Tuple[FiscalQuarter, str]]) -> Optional[Tuple[FiscalQuarter, str]]:
    links_list = list(links)
    if not links_list:
        return None
    return max(links_list, key=lambda tup: tup[0])


def download_file(url: str, out_path: str) -> None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0 Safari/537.36"
        )
    }
    with requests.get(url, headers=headers, stream=True) as resp:
        resp.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    print(f"Downloaded: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the latest H-1B/LCA disclosure file from DOL")
    parser.add_argument("--year", type=int, help="Fiscal year to download (e.g., 2025)")
    parser.add_argument("--quarter", type=int, choices=[1, 2, 3, 4], help="Fiscal quarter (1-4)")
    parser.add_argument("--output", default=None, help="Destination filename (default: original filename)")
    args = parser.parse_args()

    html = fetch_performance_page()
    disclosures = list(extract_lca_links(html))
    if not disclosures:
        print("No LCA disclosure links found on the Performance Data page.", file=sys.stderr)
        sys.exit(1)

    selected_links = disclosures
    if args.year is not None:
        selected_links = [(fq, url) for fq, url in disclosures if fq.year == args.year]
        if args.quarter is not None:
            selected_links = [(fq, url) for fq, url in selected_links if fq.quarter == args.quarter]
        elif selected_links:
            selected_links = [max(selected_links, key=lambda tup: tup[0])]

    if not selected_links:
        print(f"No LCA files match year={args.year} and quarter={args.quarter}.", file=sys.stderr)
        sys.exit(1)

    fq, url = choose_latest_quarter(selected_links)
    filename = os.path.basename(url)
    out_path = args.output or filename
    print(f"Downloading {fq} disclosure data from {url}\nSaving to {out_path}…")
    download_file(url, out_path)


if __name__ == "__main__":
    main()
