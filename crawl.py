import asyncio
from urllib.parse import urlparse

import aiohttp
from urllib3.util import url
from bs4 import BeautifulSoup

class AsyncCrawler:
    def __init__(self, base_url, max_concurrency = 10, max_pages = 30):
        self.base_url = base_url
        self.domain = self.get_domain(base_url)
        self.page_data = {}
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None
        self.links = []
        self.page_data = {}
        self.added = 0

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            await self.session.close()

            self.session = None

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.added >= self.max_pages:
                return False

            self.added += 1

            if normalized_url in self.page_data:
                return False

            return True

    def normalize_url(self, uri: url):
        """Normalize a URL given via parameter by removing the scheme."""
        parsed = urlparse(uri)

        if not parsed.hostname:
            return None

        path = parsed.path if parsed.path else ""

        return parsed.hostname + path

    def get_h1_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find('h1').text if soup.find('h1') else ""

    def get_first_paragraph_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        if not soup.find('main'):
            return soup.find('p').text if soup.find('p') else ""

        return soup.find('main').find('p').text if soup.find('main').find('p') else ""

    def get_urls_from_html(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        urls = []

        parsed = urlparse(url)

        if not parsed.hostname or not parsed.scheme:
            return urls

        base_url = parsed.scheme + "://" + parsed.hostname

        for link in soup.find_all('a'):
            href = link.get('href')

            if not href:
                continue

            if href.startswith('/') and not href.startswith('//'):
                href = base_url + href

            if href not in urls:
                urls.append(href)

        return urls

    def get_images_from_html(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        images = []

        parsed = urlparse(url)

        if not parsed.hostname or not parsed.scheme:
            return images

        base_url = parsed.scheme + "://" + parsed.hostname

        for img in soup.find_all('img'):
            src = img.get('src')

            if not src:
                continue

            if src.startswith('/'):
                images.append(base_url + src)

        return images

    def extract_page_data(self, html, page_url):
        return {
            'page_url'          : page_url,
            'h1'                : self.get_h1_from_html(html),
            'first_paragraph'   : self.get_first_paragraph_from_html(html),
            'outgoing_link_urls': self.get_urls_from_html(html, page_url),
            'image_urls'        : self.get_images_from_html(html, page_url)
        }

    async def get_html(self, url, content_type = "text/html"):
        if self.session is None:
            raise RuntimeError("Crawler not initialized. Use: async with AsyncCrawler(...) as c:")

        try:
            async with self.session.get(url, headers = {"User-Agent": "Scrappy/1.0"}) as response:
                if response.status < 200 or response.status >= 300:
                    return ConnectionError(f"Unable to fetch page. Response code: {response.status}")

                if not response.headers.get('Content-Type', "").startswith(content_type):
                    return ValueError("Page is not HTML.")

                return await response.text()
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

            return None

    def get_domain(self, url):
        """Extract domain from URL."""
        parsed = urlparse(url)

        return parsed.hostname

    async def get_robots_rules(self):
        """Get robots.txt rules for a given URL."""
        url = self.base_url

        if not url.endswith('/'):
            url += '/'

        try:
            response = await self.get_html(f"{url}robots.txt", "text/plain")

            lines = response.splitlines()

            rules = []

            adding_rules = False

            for line in lines:
                if line.startswith('User-agent:'):
                    if line.split(' ')[1] == '*':
                        adding_rules = True
                    else:
                        adding_rules = False

                if adding_rules and line.startswith('Disallow:'):
                    rules.append(line.split(' ')[1])

            return rules
        except Exception as e:
            print(f"Failed to fetch robots.txt: {e}")

            return []

    async def start_crawl(self):
        rules = await self.get_robots_rules()

        await self.crawl(rules)

        return self.page_data

    async def crawl(self, rules, current_url = None, links = None):
        if links is None:
            links = []
        if not current_url:
            current_url = self.base_url

        normalized_url = self.normalize_url(current_url)

        if not await self.add_page_visit(current_url):
            return

        if self.get_domain(current_url) != self.get_domain(self.base_url):
            return

        if len(rules) and current_url.startswith(rules):
            print(f"Skipping blocked URL {current_url}")

            return

        async with self.semaphore:
            print(f"Crawling {current_url}")

            try:
                html = await self.get_html(current_url)

                if not type(html) is str:
                    return

                page_info = self.extract_page_data(html, current_url)

                async with self.lock:
                    self.page_data[normalized_url] = page_info

                tasks = []

                for link in page_info['outgoing_links']:
                    if link.startswith(tuple(rules)):
                        continue

                    if link not in links:
                        links.append(link)

                        tasks.append(asyncio.create_task(
                            self.crawl(rules, link, links)
                        ))

                if tasks:
                    await asyncio.gather(*tasks)
            except Exception as e:
                print(f"Failed to crawl {current_url}: {e}")

async def async_crawl_page(url: str, max_jobs: int, max_pages: int):
    async with AsyncCrawler(url, max_jobs, max_pages) as crawler:
        return await crawler.start_crawl()
