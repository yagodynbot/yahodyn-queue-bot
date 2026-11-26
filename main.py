import os
import logging
from datetime import datetime

import requests

# ==========================================
# YAHODIN QUEUE BOT
# Ягодин — Дорогуськ
# Вантажівки понад 7,5 тонн
# ==========================================

API_URL = (
    "https://back.echerha.gov.ua/api/v5/"
    "workload/1/checkpoints/1/details/1/30?page=1"
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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

    response.raise_for_status()

    result = response.json()
    vehicles = result.get("data", [])

    if not isinstance(vehicles, list):
        raise ValueError("Invalid API response")

    return vehicles


def format_queue(vehicles):
    """Формування списку автомобілів."""

    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    lines = [
        "🚛 ЯГОДИН — ДОРОГУСЬК",
        "Черга вантажівок понад 7,5 тонн",
        "",
        f"🚚 Автомобілів у черзі: {len(vehicles)}",
        f"🕒 Оновлено: {now}",
        ""
    ]

    for vehicle in vehicles:

        lines.extend([
            "━━━━━━━━━━━━━━━━━━",
            f"📍 Позиція: {vehicle.get('position', '-')}",
            f"🚛 Авто: {vehicle.get('plate_number', '-')}",
            f"🚚 Причіп: {vehicle.get('semi_trailer_number', '-')}",
            f"🎫 Номер черги: {vehicle.get('position_number', '-')}",
            f"📝 Реєстрація: {vehicle.get('confirmed_at', '-')}",
            f"⏳ Орієнтовний час: {vehicle.get('estimated_time', '-')}",
            ""
        ])

    return "\n".join(lines)


def send_telegram(message):
    """Надсилання повідомлення в Telegram."""

    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing")

    if not CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is missing")

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    # Розділяємо повідомлення на частини,
    # щоб не перевищувати ліміт Telegram.

    chunks = []
    current = ""

    for line in message.split("\n"):

        if len(current) + len(line) + 1 > 3900:
            if current:
                chunks.append(current)

            current = line
        else:
            current += ("\n" if current else "") + line

    if current:
        chunks.append(current)

    for chunk in chunks:

        response = requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": chunk
            },
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):
            raise RuntimeError(
                "Telegram rejected the message"
            )

    logging.info("Telegram message sent successfully")


def main():

    logging.info("YAHODIN BOT STARTED")

    vehicles = get_queue_data()

    logging.info(
        "Vehicles found: %s",
        len(vehicles)
    )

    message = format_queue(vehicles)

    send_telegram(message)

    logging.info("YAHODIN BOT SUCCESSFUL")


if __name__ == "__main__":
    main()
