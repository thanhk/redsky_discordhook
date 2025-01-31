from dotenv import load_dotenv
import os
import requests
import datetime

load_dotenv()

# RedSky API URL
BASE_API_URL = (
    "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1?"
    "key={key}&tcin="
)
REDSKY_API_KEY = os.getenv("REDSKY_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
LOG_FILE = os.getenv("LOG_FILE")

# Optional headers: helps mimic a real browser user-agent
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TCINS = [
    "93954435",  # Prismatic Evolutions Elite Trainer Box
    "88897904",  # S3.5 Booster Bundle Box
]

def log(message: str):
    """Append a single line to the log file with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)

def check_availability(data):
    """Returns the availability status string, or 'UNKNOWN' if not found."""
    try:
        return data["data"]["product"]["fulfillment"]["shipping_options"]["availability_status"]
    except KeyError:
        return "UNKNOWN"

def send_discord_alert(message):
    """Send a message to your Discord channel via webhook."""
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Discord alert sent!")
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")

def build_redsky_url(tcin: str) -> str:
    """Return a full URL for a given TCIN using the configured key."""
    return BASE_API_URL.format(key=REDSKY_API_KEY) + tcin

def main():
    statuses = []

    for tcin in TCINS:
        url = build_redsky_url(tcin)
        print(f"Checking {url}")

        try:
            response = requests.get(url, headers=HEADERS)
            data = response.json()
            availability = check_availability(data)

            statuses.append(f"{tcin}: {availability}")

            if availability != "OUT_OF_STOCK":
                product_link = f"https://www.target.com/p/-/A-{tcin}"
                send_discord_alert(
                   f"**TCIN {tcin}** might be in stock! {availability}\nCheck Target: {product_link}"
                )

        except Exception as e:
            statuses.append(f"{tcin}: ERROR({e})")

    log_message = ", ".join(statuses)
    log(log_message)

if __name__ == "__main__":
    main()
