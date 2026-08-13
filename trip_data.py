import json
from pathlib import Path


DATA_FILE = Path("trip_data.json")


def save_trip(trip):
    """Save a completed trip to trip_data.json."""

    # Start with an empty list if the file
    # doesn't exist or is empty/corrupted.
    trips = []

    if DATA_FILE.exists():

        try:
            with open(DATA_FILE, "r") as file:
                content = file.read().strip()

                if content:
                    trips = json.loads(content)

        except (json.JSONDecodeError, OSError):
            print(
                "\nWarning: trip_data.json was empty "
                "or corrupted. Starting fresh."
            )

            trips = []


    # Add the new trip.
    trips.append(trip)


    # Save everything back to the file.
    with open(DATA_FILE, "w") as file:
        json.dump(
            trips,
            file,
            indent=4
        )