import asyncio
import sys

from crawl import async_crawl_page
from cvs_out import write_csv_report


async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        exit(1)

    if len(sys.argv) > 4:
        print("too many arguments provided")
        exit(1)

    base_url = sys.argv[1]
    max_jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 30

    print(f"starting crawl of: {base_url}")

    res = await async_crawl_page(base_url, max_jobs, max_pages)

    for page in res.values():
        print(f"Found {len(page['outgoing_link_urls'])} outgoing links on {page['page_url']}")

    write_csv_report(res.values())

    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
