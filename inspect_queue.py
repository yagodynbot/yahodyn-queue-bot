
import requests
import json
import sys

API_URL = (
    "https://back.echerha.gov.ua/api/v5/"
    "workload/1/checkpoints/1/details/1/30?page=1"
)

HEADERS = {
    "Accept": "application/json",
    "Origin": "https://echerha.gov.ua",
    "Referer": "https://echerha.gov.ua/",
    "User-Agent": "Mozilla/5.0",
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
        response.raise_for_status()

        result = response.json()
        vehicles = result.get("data", [])

        if not isinstance(vehicles, list):
            raise ValueError("Unexpected API response format")

        print(f"\nVehicles found: {len(vehicles)}\n")

        for vehicle in vehicles:
            print("-" * 40)
            print("Truck:", vehicle.get("plate_number"))
            print("Trailer:", vehicle.get("semi_trailer_number"))
            print("Position:", vehicle.get("position"))
            print("Queue number:", vehicle.get("position_number"))
            print("Registered:", vehicle.get("confirmed_at"))
            print("Estimated:", vehicle.get("estimated_time"))

        print("\nAPI CONNECTION SUCCESSFUL")

    except requests.RequestException as error:
        print("API REQUEST ERROR:", error)
        sys.exit(1)

    except (ValueError, json.JSONDecodeError) as error:
        print("DATA ERROR:", error)
        sys.exit(1)


if __name__ == "__main__":
    inspect_queue()
