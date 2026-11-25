
import os
import json
import time
import logging
from datetime import datetime, timezone

import requests

# Yahodin Bot
# Основна черга завантажених вантажівок понад 7,5 т

QUEUE_URL = (
    "https://echerha.gov.ua/"
    "workload/truck/checkpoints/1/1/30"
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 600
ALERT_INCREASE = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

session = requests.Session()
session.headers.update({
    "User-Agent": "YahodinQueueBot/1.0"
})


def get_queue_data():
    response = session.get(QUEUE_URL, timeout=30)
    response.raise_for_status()

    return response.text


def get_queue_count():
    """
    Тут буде підключено перевірений
    формат даних API єЧерги.

    Не використовуємо кількість HTML-рядків
    як кількість вантажівок.
    """
    raise NotImplementedError(
        "Потрібно підтвердити API та поле "
        "з кількістю автомобілів."
    )


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        logging.error("BOT_TOKEN або CHAT_ID не задані")
        return

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


def monitor():
    previous_count = None

    logging.info("Yahodin Bot started")

    while True:
        try:
            current_count = get_queue_count()

            if previous_count is None:
                previous_count = current_count
                logging.info(
                    "Initial queue: %s", current_count
                )

            else:
                difference = current_count - previous_count

                logging.info(
                    "Previous: %s | Current: %s | Change: %+d",
                    previous_count,
                    current_count,
                    difference
                )

                if difference >= ALERT_INCREASE:
                    send_telegram(
                        "🚛 YAHODIN BOT\n\n"
                        "Збільшення черги Ягодин — Дорогуск!\n"
                        f"Було: {previous_count} машин\n"
                        f"Стало: {current_count} машин\n"
                        f"Збільшення: +{difference}"
                    )

                previous_count = current_count

        except Exception:
            logging.exception("Monitoring error")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor()
