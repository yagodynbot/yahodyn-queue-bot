import requests
import json
import sys

API_URL = (
    "https://back.echerha.gov.ua/api/v5/"
    "workload/1/checkpoints/1/details/1/30?page=1"
)


HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "uk-UA,uk;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://echerha.gov.ua",
    "Referer": "https://echerha.gov.ua/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/27.2 Safari/605.1.15"
    ),
    "X-Client-Locale": "uk",
    "X-Device-Id": "8cb50a23-b3f2-400a-8cbb-4fa7dd57d7a7",
    "X-Device-Name": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/27.2 Safari/605.1.15"
    ),
    "X-User-Agent": "UABorder/3.14.0 Web/1.1.0 User/guest",
}


def inspect_queue():
    print("YAHODYN QUEUE BOT")
    print("Connecting to eCherha API...")

    try:
        response = requests.get(
            API_URL,
            headers=HEADERS,
            timeout=30
        )

        print("HTTP status:", response.status_code)
        print("SERVER RESPONSE:", response.text[:3000])

        response.raise_for_status()

        
            result = response.json()
            vehicles = result.get("data", [])

            if not isinstance(vehicles, list):
                raise ValueError("Unexpected API response format")

            vehicles.sort(
                key=lambda v: int(v.get("position") or 999999)
            )

            print("\n" + "=" * 65)
            print("       YAHODYN QUEUE MONITOR")
            print("=" * 65)

            print(f"Vehicles found: {len(vehicles)}")
            print("Updated:", __import__("datetime").datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S"))

            print("-" * 65)

            for vehicle in vehicles:
                print(f"\nPosition: {vehicle.get('position', '-')}")
                print(f"Truck:    {vehicle.get('plate_number', '-')}")
                print(f"Trailer:  {vehicle.get('semi_trailer_number', '-')}")
                print(f"Queue ID: {vehicle.get('position_number', '-')}")
                print(f"Registered: {vehicle.get('confirmed_at', '-')}")
                print(f"Estimated:  {vehicle.get('estimated_time', '-')}")

            print("\n" + "=" * 65)
            print("API CONNECTION SUCCESSFUL")
            print("=" * 65)

        print("\nAPI CONNECTION SUCCESSFUL")

    except requests.RequestException as error:
        print("API REQUEST ERROR:", error)
        sys.exit(1)

    except (ValueError, json.JSONDecodeError) as error:
        print("DATA ERROR:", error)
        sys.exit(1)


if __name__ == "__main__":
    inspect_queue()
