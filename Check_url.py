import asyncio
from playwright.async_api import async_playwright
from sys import argv
import validators

# Dictionary containing tools and their corresponding selectors
Tools = {
    "virus_total": ["https://www.virustotal.com/gui/home/url", "input[placeholder='Search or scan a URL']", "div.engines"],
    "norton": ["https://safeweb.norton.com/", "input[placeholder='Search for a site, example: www.google.com']", "p.rating-label"],
    "metadefender": ["https://metadefender.opswat.com/", "input[placeholder='File, URL, IP address, Domain, Hash, or CVE']", "div.score"],
}


async def scrape_tool(tool, url):
    async with async_playwright() as p:
        # Launching the browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # Route to abort unnecessary resources for faster loading
            await page.route("**/*.{png,jpg,jpeg,gif,svg,ico,ttf,otf,woff,woff2,mp4,web,css}", lambda route: route.abort())
            # Navigate to the tool's URL
            await page.goto(Tools[tool][0])
            # Fill the input field with the provided URL
            await page.fill(Tools[tool][1], url)
            # Press Enter to initiate the search
            await page.press(Tools[tool][1], "Enter")
            # Wait for the selector to appear on the page
            await page.wait_for_selector(Tools[tool][2])
            # Get the inner text of the selector
            result = await page.inner_text(Tools[tool][2])
            # Print the result and the current page URL
            print(result, page.url)
        except Exception as e:
            print(f"An error occurred while scraping {tool}: {e}")
        finally:
            # Close the browser after completion
            await browser.close()


async def main(url):
    tasks = []
    for tool in Tools:
        tasks.append(scrape_tool(tool, url))
    # Gather all the tasks to execute concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        # Retrieve the URL from command line arguments
        url = argv[1]
        # Validate the URL
        if not validators.url(url):
            print("Please provide a valid URL")
            exit(2)
        # Run the main function with the provided URL
        asyncio.run(main(url))
    except IndexError:
        print("Please provide a URL")
        exit(1)
