
import requests
from bs4 import BeautifulSoup

URL = (
    "https://echerha.gov.ua/"
    "workload/truck/checkpoints/1/1/30"
)

def inspect_queue():
    print("YAHODYN QUEUE BOT")
    print("Перевірка офіційної єЧерги")

    headers = {
        "User-Agent": "YahodynQueueBot/1.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    print("HTTP status:", response.status_code)
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    print("Page title:", soup.title.get_text(strip=True)
          if soup.title else "Не знайдено")

    tables = soup.find_all("table")
    print("Знайдено таблиць:", len(tables))

    found = False

    for number, table in enumerate(tables, start=1):
        rows = table.find_all("tr")
        headers_text = [
            cell.get_text(" ", strip=True).lower()
            for cell in table.find_all("th")
        ]

        print(f"\nТаблиця №{number}")
        print("Заголовки:", headers_text)
        print("Кількість рядків:", max(0, len(rows) - 1))

        header_text = " ".join(headers_text)

        if (
            "номер транспорту" in header_text
            and "реєстрація в черзі" in header_text
        ):
            found = True
            print("Знайдено таблицю черги Ягодин!")

    if not found:
        print("\nУвага: таблицю черги не вдалося визначити.")
        print("Можливо, дані завантажуються через JavaScript.")

    print("\nПеревірку завершено.")

if __name__ == "__main__":
    try:
        inspect_queue()
    except Exception as error:
        print("ПОМИЛКА:", type(error).__name__, str(error))
        raise
