import json
import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from app.config.settings import settings

# Configuration constants
PH_API_TOKEN = settings.PH_API_TOKEN  
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Scraping limits for optimal performance (tuned by 30+ years experience)
# 20-25 is optimal: Balances coverage, execution time (~60-90 sec), and data quality
# <15 = insufficient data for synthesis | >25 = diminishing returns
YC_SCRAPE_LIMIT = 50  # Y Combinator: 20 startups = ~60-80 sec execution
THUB_SCRAPE_LIMIT = 50  # T-Hub: 20 startups = ~60-80 sec execution

class BaseConnector(ABC):
    @abstractmethod
    def fetch_signals(self, query: str, limit: int = 5) -> List:
        pass

class YCombinatorConnector(BaseConnector):
    """
    Implements the 'Scroll and Wait' pattern to harvest YC Company data.
    Optimized: Limits scraping to first 30 links for performance efficiency.
    Thread-safe: Runs in isolated thread to prevent AsyncIO event loop blocking.
    """
    def fetch_signals(self, query: str, limit: int = YC_SCRAPE_LIMIT) -> List:
        # Apply global limit cap
        limit = min(limit, YC_SCRAPE_LIMIT)
        results = []
        error = None

        def run_scrape():
            nonlocal results, error
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, slow_mo=500)
                    page = browser.new_page(user_agent=USER_AGENT)
                    
                    url = f"https://www.ycombinator.com/companies?q={query}"
                    print(f"[YC] Scraping: {url} | Max limit: {limit}")
                    page.goto(url, timeout=30000)
                    
                    # Optimized scroll logic with early termination
                    previous_height = 0
                    scroll_attempts = 0
                    max_scroll_attempts = 5  # Prevent infinite scrolling
                    
                    while len(results) < limit and scroll_attempts < max_scroll_attempts:
                        company_cards = page.locator('a._company_86jzd_338').all()
                        
                        if not company_cards:
                            company_cards = page.locator('a[href^="/companies/"]').all()

                        for card in company_cards:
                            if len(results) >= limit: 
                                break
                            
                            try:
                                name = card.locator('.coName').first.text_content()
                                desc = card.locator('.coDescription').first.text_content()
                                
                                if card.locator('.coBatch').count() > 0:
                                    batch = card.locator('.coBatch').first.text_content()
                                else:
                                    batch = "Unknown"
                                
                                # Deduplication
                                if not any(r['name'] == name for r in results):
                                    results.append({
                                        "source": "Y Combinator",
                                        "type": "supply_signal",
                                        "name": name,
                                        "description": desc,
                                        "batch": batch,
                                        "url": f"https://www.ycombinator.com{card.get_attribute('href')}"
                                    })
                            except Exception:
                                continue

                        if len(results) >= limit:
                            break

                        # Smart scroll with timeout
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(1000)
                        
                        new_height = page.evaluate("document.body.scrollHeight")
                        if new_height == previous_height:
                            break 
                        previous_height = new_height
                        scroll_attempts += 1
                    
                    browser.close()
                    print(f"[YC] Completed: Scraped {len(results)} startups")
                    
            except Exception as e:
                error = e
                print(f"[YC] Error: {str(e)}")

        # Run in isolated thread to avoid AsyncIO blocking
        t = threading.Thread(target=run_scrape)
        t.daemon = False
        t.start()
        t.join(timeout=120)  # 2-minute timeout per scraper thread
        
        if error:
            print(f"[YC] Scraping failed: {error}")
            return []

        return results[:limit]

class ProductHuntConnector(BaseConnector):
    """
    Implements GraphQL v2 API to fetch high-velocity launches.
    """
    def fetch_signals(self, query: str, limit: int = 5) -> List:
        # Check if token is missing or default
        if not PH_API_TOKEN or PH_API_TOKEN == "YOUR_PRODUCT_HUNT_DEVELOPER_TOKEN":
            print("Warning: Product Hunt API Token missing.")
            return []

        url = "https://api.producthunt.com/v2/api/graphql"
        headers = {"Authorization": f"Bearer {PH_API_TOKEN}"}
        
        graphql_query = """
        {
          posts(first: %d, order: VOTES_COUNT) {
            edges {
              node {
                name
                tagline
                description
                votesCount
                commentsCount
                website
                topics {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """ % limit

        try:
            response = requests.post(url, json={'query': graphql_query}, headers=headers)
            if response.status_code != 200:
                print(f"Product Hunt API Error: {response.status_code}")
                return []

            data = response.json().get('data', {}).get('posts', {}).get('edges', [])
            normalized = []
            
            for edge in data:
                node = edge['node']
                topics = [t['node']['name'] for t in node['topics']['edges']]
                normalized.append({
                    "source": "Product Hunt",
                    "type": "market_velocity",
                    "name": node['name'],
                    "pitch": node['tagline'],
                    "metrics": f"{node['votesCount']} votes, {node['commentsCount']} comments",
                    "tags": topics,
                    "url": node['website']
                })
            return normalized
        except Exception as e:
            print(f"Product Hunt connection failed: {e}")
            return []

class DevpostConnector(BaseConnector):
    """
    Scrapes 'Built With' tags to identify Technical Momentum.
    """
    def fetch_signals(self, query: str, limit: int = 5) -> List:
        search_url = f"https://devpost.com/software/search?query={query}"
        try:
            resp = requests.get(search_url, headers={'User-Agent': USER_AGENT})
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            projects = []
            # Selector might need maintenance as Devpost updates UI
            project_links = [a['href'] for a in soup.select('.link-to-software')][:limit]
            
            for link in project_links:
                try:
                    p_resp = requests.get(link, headers={'User-Agent': USER_AGENT})
                    p_soup = BeautifulSoup(p_resp.text, 'html.parser')
                    
                    title = p_soup.select_one('#app-title').text.strip() if p_soup.select_one('#app-title') else "Unknown"
                    tagline = p_soup.select_one('.large.mb-4').text.strip() if p_soup.select_one('.large.mb-4') else ""
                    
                    built_with = [li.text.strip() for li in p_soup.select('#built-with li')]
                    
                    projects.append({
                        "source": "Devpost",
                        "type": "technical_signal",
                        "name": title,
                        "tagline": tagline,
                        "tech_stack": built_with,
                        "url": link
                    })
                except Exception:
                    continue
            return projects
        except Exception as e:
            print(f"Devpost scraping failed: {e}")
            return []

class RedditDorkGenerator(BaseConnector):
    """
    Generates 'Google Dork' URLs for high-intent social listening.
    """
    def fetch_signals(self, query: str, limit: int = 5) -> List:
        dorks = [
            {"source": "Reddit", "type": "social_signal", "dork": f'site:reddit.com "{query}" "I hate doing"'},
            {"source": "Reddit", "type": "social_signal", "dork": f'site:reddit.com "{query}" "alternative to"'},
            {"source": "Reddit", "type": "social_signal", "dork": f'site:reddit.com "{query}" "willing to pay"'},
            {"source": "Reddit", "type": "social_signal", "dork": f'site:reddit.com "{query}" "why isn\'t there a"'},
        ]
        return dorks

class THubConnector(BaseConnector):
    """
    Scrapes T-Hub (India's premier startup incubator) for emerging startups.
    Optimized: Thread-safe implementation with pagination limits.
    Focus: Early-stage Indian startups and deep-tech innovations.
    """
    def fetch_signals(self, query: str, limit: int = THUB_SCRAPE_LIMIT) -> List:
        limit = min(limit, THUB_SCRAPE_LIMIT)
        results = []
        error = None

        def run_scrape():
            nonlocal results, error
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, slow_mo=500)
                    page = browser.new_page(user_agent=USER_AGENT)
                    
                    # T-Hub startup directory search
                    url = f"https://www.t-hub.co/startups?search={query}"
                    print(f"[T-Hub] Scraping: {url} | Max limit: {limit}")
                    page.goto(url, timeout=30000)
                    page.wait_for_timeout(2000)
                    
                    # Pagination handling for T-Hub
                    pages_scanned = 0
                    max_pages = 2  # Limit to 2 pages (~30 startups)
                    
                    while len(results) < limit and pages_scanned < max_pages:
                        try:
                            # T-Hub startup cards selector
                            startup_cards = page.locator('div[class*="startup-card"]').all()
                            
                            if not startup_cards:
                                startup_cards = page.locator('a[href*="/startups/"]').all()
                            
                            for card in startup_cards:
                                if len(results) >= limit:
                                    break
                                
                                try:
                                    # Extract startup info from T-Hub card
                                    name_elem = card.locator('h3, h4, [class*="name"]').first
                                    name = name_elem.text_content().strip() if name_elem.is_visible() else "Unknown"
                                    
                                    desc_elem = card.locator('p, [class*="description"]').first
                                    description = desc_elem.text_content().strip() if desc_elem and desc_elem.is_visible() else "N/A"
                                    
                                    url_attr = card.get_attribute('href') or ""
                                    
                                    # Deduplication
                                    if name != "Unknown" and not any(r['name'] == name for r in results):
                                        results.append({
                                            "source": "T-Hub",
                                            "type": "supply_signal",
                                            "name": name,
                                            "description": description[:150],
                                            "category": "Indian Startup",
                                            "url": url_attr if url_attr.startswith('http') else f"https://www.t-hub.co{url_attr}"
                                        })
                                except Exception as e:
                                    continue
                            
                            if len(results) >= limit:
                                break
                            
                            # Navigate to next page if available
                            next_btn = page.locator('a[aria-label*="next"], button:has-text("Next")').first
                            if next_btn and next_btn.is_visible():
                                next_btn.click()
                                page.wait_for_timeout(1500)
                                pages_scanned += 1
                            else:
                                break
                                
                        except Exception as e:
                            print(f"[T-Hub] Pagination error: {str(e)}")
                            break
                    
                    browser.close()
                    print(f"[T-Hub] Completed: Scraped {len(results)} startups")
                    
            except Exception as e:
                error = e
                print(f"[T-Hub] Connection error: {str(e)}")

        # Execute in isolated thread
        t = threading.Thread(target=run_scrape)
        t.daemon = False
        t.start()
        t.join(timeout=120)  # 2-minute timeout
        
        if error:
            print(f"[T-Hub] Scraping failed: {error}")
            return []

        return results[:limit]

def market_intel_search(query: str, sources: List[str] = ["yc", "ph", "devpost", "reddit", "thub"]):
    """
    The Orchestrator function to be called by the Agent.
    Multi-threaded execution for parallel source scraping.
    """
    aggregator = []
    
    # Map sources to connector instances
    connector_map = {
        "yc": YCombinatorConnector(),
        "ph": ProductHuntConnector(),
        "devpost": DevpostConnector(),
        "reddit": RedditDorkGenerator(),
        "thub": THubConnector()
    }
    
    # Filter to only requested sources
    active_sources = [s for s in sources if s in connector_map]
    
    if not active_sources:
        print("[Market Intel] No valid sources specified")
        return json.dumps([], indent=2)
    
    print(f"[Market Intel] Executing parallel scrape for: {', '.join(active_sources)}")
    
    # Execute all sources in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(active_sources), thread_name_prefix="MarketIntel") as executor:
        futures = {
            executor.submit(connector_map[source].fetch_signals, query): source 
            for source in active_sources
        }
        
        for future in as_completed(futures):
            source = futures[future]
            try:
                results = future.result(timeout=130)  # 2+ min timeout per thread
                aggregator.extend(results)
                print(f"[Market Intel] {source.upper()}: Retrieved {len(results)} results")
            except Exception as e:
                print(f"[Market Intel] {source.upper()} failed: {str(e)}")
    
    print(f"[Market Intel] Total aggregated results: {len(aggregator)}")
    return json.dumps(aggregator, indent=2)

def search_all(query: str, limit: int = 5, types: Optional[List[str]] = None) -> List[Dict]:
    """
    Unified search function with multi-threaded parallel execution.
    Optimized for CPU utilization across all source connectors.
    """
    aggregator = []
    
    # Define all connectors
    connectors = [
        ("YC", YCombinatorConnector(), min(limit, YC_SCRAPE_LIMIT)),
        ("Product Hunt", ProductHuntConnector(), limit),
        ("Devpost", DevpostConnector(), limit),
        ("Reddit", RedditDorkGenerator(), limit),
        ("T-Hub", THubConnector(), min(limit, THUB_SCRAPE_LIMIT))
    ]
    
    print(f"[Search All] Initiating parallel search across {len(connectors)} sources")
    start_time = time.time()
    
    # Execute all connectors in parallel thread pool
    with ThreadPoolExecutor(max_workers=len(connectors), thread_name_prefix="SearchAll") as executor:
        futures = {
            executor.submit(connector.fetch_signals, query, conn_limit): name 
            for name, connector, conn_limit in connectors
        }
        
        for future in as_completed(futures):
            source_name = futures[future]
            try:
                results = future.result(timeout=130)
                aggregator.extend(results)
                print(f"[Search All] {source_name}: {len(results)} results")
            except Exception as e:
                print(f"[Search All] {source_name} error: {str(e)}")
    
    elapsed = time.time() - start_time
    print(f"[Search All] Completed in {elapsed:.2f}s | Total: {len(aggregator)} results")
    
    # Filter by types if provided
    if types:
        aggregator = [item for item in aggregator if item.get("type") in types]
        print(f"[Search All] After type filter: {len(aggregator)} results")
    
    return aggregator

# --- Tool Definition ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "market_intel_search",
            "description": "Search for market intelligence signals across multiple sources (YC, Product Hunt, Devpost, Reddit).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The market/product/technology query to search for."
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific data silos to mine."
                    }
                },
                "required": ["query"]
            }
        }
    }
]