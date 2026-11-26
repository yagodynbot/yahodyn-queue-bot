import os
import json
import logging
from datetime import datetime

import requests

# ==========================================
# YAHODIN QUEUE BOT
# Ягодин — Дорогуськ
# Тільки кількість вантажівок понад 7,5 т
# ==========================================

API_URL = (
    "https://back.echerha.gov.ua/api/v5/"
    "workload/1/checkpoints/1/details/1/30?page=1"
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = [
    os.getenv("TELEGRAM_CHAT_ID"),
    "390756867",
]

STATE_FILE = "queue_state.json"
ALERT_INCREASE = 30

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://echerha.gov.ua",
    "Referer": "https://echerha.gov.ua/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/27.2 Safari/605.1.15"
    ),
    "x-client-locale": "uk",
    "x-device-id": "8cb50a23-b3f2-400a-8cbb-4fa7dd57d7a7",
    "x-device-name": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/27.2 Safari/605.1.15"
    ),
    "x-user-agent": "UABorder/3.14.0 Web/1.1.0 User/guest",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def get_queue_count():
    response = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=30
    )

    logging.info("HTTP status: %s", response.status_code)

    response.raise_for_status()

    result = response.json()
    meta = result.get("meta", {})
    total = meta.get("total")

if not isinstance(total, int):
    raise ValueError("Total queue count is missing or invalid")

return total


def load_state():
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        state = json.load(file)

    return state.get("previous_count")


def save_state(count):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            {"previous_count": count},
            file
        )


def send_telegram(message):
    if not BOT_TOKEN:
        raise ValueError("Telegram bot token is missing")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for chat_id in CHAT_IDS:
        if not chat_id:
            continue

        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message
            },
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):
            raise RuntimeError(
                f"Telegram rejected message for chat_id {chat_id}"
            )

        logging.info(f"Telegram notification sent to {chat_id}")

def main():
    logging.info("YAHODIN MONITOR STARTED")
    
    current_count = get_queue_count()
    previous_count = load_state()

    now = datetime.now().astimezone().strftime(
        "%d.%m.%Y %H:%M:%S"
    )

    logging.info(
        "Previous: %s | Current: %s",
        previous_count,
        current_count
    )

    if previous_count is None:
        message = (
            "🚛 YAHODIN BOT\n\n"
            "Ягодин — Дорогуськ\n"
            "Початкова перевірка черги\n\n"
            f"🚚 У черзі: {current_count} машин\n"
            f"🕒 Оновлено: {now}"
        )

        send_telegram(message)

    else:
        difference = current_count - previous_count

        if difference >= ALERT_INCREASE:
            message = (
                "🚛 YAHODIN BOT\n\n"
                "📈 ЗБІЛЬШЕННЯ ЧЕРГИ!\n"
                "Ягодин — Дорогуськ\n\n"
                f"Було: {previous_count} машин\n"
                f"Стало: {current_count} машин\n"
                f"Збільшення: +{difference} машин\n\n"
                f"🕒 {now}"
            )

            send_telegram(message)

        elif difference < 0:
            message = (
                "🚛 YAHODIN BOT\n\n"
                "📉 ЗМЕНШЕННЯ ЧЕРГИ!\n"
                "Ягодин — Дорогуськ\n\n"
                f"Було: {previous_count} машин\n"
                f"Стало: {current_count} машин\n"
                f"Зменшення: {abs(difference)} машин\n\n"
                f"🕒 {now}"
            )

            send_telegram(message)

        else:
            logging.info("No significant queue change")

    save_state(current_count)

    logging.info("YAHODIN MONITOR SUCCESSFUL")


if __name__ == "__main__":
    main()
