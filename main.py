import os
import json
import logging
from datetime import datetime

import requests

# ==========================================
# YAHODIN QUEUE MONITOR
# ==========================================

API_URL = (
    "https://back.echerha.gov.ua/api/v5/"
    "workload/1/checkpoints/1/details/1/30?page=1"
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STATE_FILE = "queue_state.json"
ALERT_INCREASE = 30

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://echerha.gov.ua",
    "Referer": "https://echerha.gov.ua/",
    "User-Agent": "Mozilla/5.0",
    "X-Client-Locale": "uk"
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)



def get_queue_data():
    """Отримання черги з API єЧерги."""

    response = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=30
    )

    logging.info("HTTP status: %s", response.status_code)

    if response.status_code != 200:
        logging.error(
            "API response body: %s",
            response.text[:3000]
        )

    response.raise_for_status()

    result = response.json()

    vehicles = result.get("data", [])

    if not isinstance(vehicles, list):
        raise ValueError("Invalid API response")

    logging.info("Vehicles received: %s", len(vehicles))

    return vehicles


def load_state():
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        state = json.load(file)

    return state.get("queue_count")


def save_state(count):
    temporary_file = STATE_FILE + ".tmp"

    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(
            {"queue_count": count},
            file
        )

    os.replace(temporary_file, STATE_FILE)


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("Telegram credentials missing")

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError("Telegram rejected message")


def main():
    logging.info("YAHODIN MONITOR STARTED")

    vehicles = get_queue_data()
    current_count = len(vehicles)

    logging.info("Vehicles found: %s", current_count)

    previous_count = load_state()

    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    if previous_count is None:

        message = (
            "🚛 YAHODIN BOT\n\n"
            "Моніторинг черги запущено!\n"
            f"Автомобілів: {current_count}\n"
            f"Оновлено: {now}"
        )

        send_telegram(message)
        save_state(current_count)

        logging.info("Initial queue saved")

    else:

        difference = current_count - previous_count

        logging.info(
            "Previous: %s | Current: %s | Change: %+d",
            previous_count,
            current_count,
            difference
        )

        if difference >= ALERT_INCREASE:

            message = (
                "🚨 YAHODIN BOT — УВАГА!\n\n"
                "Збільшення черги Ягодин — Дорогуськ!\n\n"
                f"Було: {previous_count} машин\n"
                f"Стало: {current_count} машин\n"
                f"Збільшення: +{difference} машин\n\n"
                f"Час: {now}"
            )

            send_telegram(message)

            logging.info("Increase alert sent")

        else:
            logging.info("No significant queue increase")

        save_state(current_count)

    logging.info("YAHODIN MONITOR SUCCESSFUL")


if __name__ == "__main__":
    main()
