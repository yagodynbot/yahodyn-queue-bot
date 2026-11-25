import requests
import sys
from datetime import datetime


API_URL = (
    "https://back.echerha.gov.ua/api/v5/"
    "workload/1/checkpoints/1/details/1/30?page=1"
)

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


def inspect_queue():
    print("=" * 65)
    print("             YAHODYN QUEUE BOT")
    print("=" * 65)

    print("Connecting to eCherha API...")

    try:
        response = requests.get(
            API_URL,
            headers=HEADERS,
            timeout=30
        )

        print("HTTP status:", response.status_code)

        response.raise_for_status()

        result = response.json()
        vehicles = result.get("data", [])

        if not isinstance(vehicles, list):
            raise ValueError("Unexpected API response format")

        vehicles.sort(
            key=lambda v: int(v.get("position") or 999999)
        )

        print("\n" + "=" * 65)
        print("             YAHODYN QUEUE MONITOR")
        print("=" * 65)

        print("Vehicles found:", len(vehicles))

        print(
            "Updated:",
            datetime.now().astimezone().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        print("-" * 65)

        for vehicle in vehicles:
            print()
            print("Position:", vehicle.get("position", "-"))
            print("Truck:", vehicle.get("plate_number", "-"))
            print(
                "Trailer:",
                vehicle.get("semi_trailer_number", "-")
            )
            print(
                "Queue number:",
                vehicle.get("position_number", "-")
            )
            print(
                "Registered:",
                vehicle.get("confirmed_at", "-")
            )
            print(
                "Estimated:",
                vehicle.get("estimated_time", "-")
            )

            print("-" * 65)

        print("\nAPI CONNECTION SUCCESSFUL")
        print("Vehicles displayed:", len(vehicles))

    except requests.exceptions.RequestException as error:
        print("\nAPI REQUEST ERROR:", error)

        if getattr(error, "response", None) is not None:
            print("SERVER RESPONSE:", error.response.text[:2000])

        sys.exit(1)

    except (ValueError, TypeError) as error:
        print("\nDATA ERROR:", error)
        sys.exit(1)


if __name__ == "__main__":
    inspect_queue()
