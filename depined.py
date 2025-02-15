import asyncio
import json
import random
import cloudscraper
from loguru import logger
import time

POLLING_INTERVAL = 90  # in seconds
KEEP_ALIVE_INTERVAL = 3  # in seconds
CHECK_BROWSER_STATE_INTERVAL = 30  # in seconds
API_URL = "https://api.depined.org/api/user/widget-connect"

token = input('Please Enter your TOKEN: ')
connection_state = True

user_agent = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
]
random_user_agent = random.choice(user_agent)

scraper = cloudscraper.create_scraper()

async def keep_alive():
    while True:
        logger.info("Sending ping")
        await asyncio.sleep(KEEP_ALIVE_INTERVAL)

async def poll_api():
    global connection_state
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": random_user_agent,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://api.depined.org/",
        "Origin": "https://api.depined.org",
        "DNT": "1",
        "Connection": "keep-alive"
    }
    while connection_state:
        try:
            payload = {"connected": True}
            logger.info(f"Sending request payload: {json.dumps(payload)}")
            response = scraper.post(API_URL, headers=headers, json=payload)
            logger.info(f"Response Status: {response.status_code}")
            response_text = response.text
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"Ping Successful!")
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
        logger.info("Checking browser state...")
        if connection_state:
            logger.info("Browser is active!")
        else:
            logger.warning("No active windows!")
            break
        await asyncio.sleep(CHECK_BROWSER_STATE_INTERVAL)

async def main():
    logger.info("Splekenesis Depined Bot")
    await asyncio.gather(
        poll_api(),
        keep_alive(),
        check_browser_state()
    )

if __name__ == '__main__':
    asyncio.run(main())
