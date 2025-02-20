import asyncio
import json
import random
import logging
import cloudscraper
from loguru import logger
import time
import sys

POLLING_INTERVAL = 90  # in seconds
KEEP_ALIVE_INTERVAL = 3  # in seconds
CHECK_BROWSER_STATE_INTERVAL = 30  # in seconds
API_URL = "https://api.depined.org/api/user/widget-connect"
EARNINGS_URL = "https://api.depined.org/api/stats/epoch-earnings"

connection_state = True
access_token = None  # Define as global variable

user_agent = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
]
random_user_agent = random.choice(user_agent)

scraper = cloudscraper.create_scraper()

def get_access_token():
    try:
        with open('token.txt', 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading access token from file: {e}")
        return None

def get_headers():
    """Generate headers for API requests."""
    if not access_token:
        logger.error("Access token is missing!")
        sys.exit(1)

    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": random_user_agent,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://api.depined.org/",
        "Origin": "https://api.depined.org",
        "DNT": "1",
        "Connection": "keep-alive"
    }

async def fetch_earnings():
    """Fetch and display earnings from API."""
    try:
        response = scraper.get(EARNINGS_URL, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            earnings = data.get("data", {}).get("earnings", 0)
            formatted_earnings = f"{earnings:,.2f}"  # Format as 1,000.00
            logger.info(f"📈 Earnings: ({formatted_earnings})")
        else:
            logger.warning(f"Failed to fetch earnings. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching earnings: {e}")

async def keep_alive():
    while True:
        await asyncio.sleep(KEEP_ALIVE_INTERVAL)

async def poll_api():
    global connection_state
    while connection_state:
        try:
            payload = {"connected": True}
            logger.info(f"Sending request payload: {json.dumps(payload)}")
            response = scraper.post(API_URL, headers=get_headers(), json=payload)
            logger.info(f"Response Status: {response.status_code}")
            response_text = response.text
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("✅ Ping Successful!")
                    await fetch_earnings()
                    logger.info("Sending ping...")
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON response: {response_text}")
            else:
                logger.warning(f"API call failed with status: {response.status_code}, Response: {response_text}")
        except Exception as e:
            logger.error(f"Polling error: {e}")
        await asyncio.sleep(POLLING_INTERVAL + random.uniform(-5, 5))

async def check_browser_state():
    global connection_state
    while True:
        await asyncio.sleep(CHECK_BROWSER_STATE_INTERVAL)

async def main():
    global access_token
    logger.info("Splekenesis Depined Bot")
    access_token = get_access_token()  # Set access_token globally

    if not access_token:
        logger.error("Failed to retrieve access token. Exiting...")
        sys.exit(1)

    await asyncio.gather(
        poll_api(),
        keep_alive(),
        check_browser_state()
    )

if __name__ == '__main__':
    asyncio.run(main())
