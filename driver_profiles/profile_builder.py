import json
from pathlib import Path


DATA_FILE = Path("trip_data.json")


def load_trips():
    """Load all stored trips."""

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def calculate_average(trips, metric):
    """Calculate the average value of a metric."""

    values = [trip[metric] for trip in trips]

    return sum(values) / len(values)


def build_profiles():

    trips = load_trips()

    profiles = {}

    driver_styles = [
        "calm",
        "normal",
        "aggressive"
    ]

    for style in driver_styles:

        # Get only trips belonging to this style.
        style_trips = [
            trip
            for trip in trips
            if trip["driver_style"] == style
        ]

        if not style_trips:
            print(f"No trips found for {style}.")
            continue


        # Calculate average metrics.
        average_speed = calculate_average(
            style_trips,
            "average_speed"
        )

        average_acceleration = calculate_average(
            style_trips,
            "average_acceleration"
        )

        average_braking_rate = calculate_average(
            style_trips,
            "hard_braking_rate"
        )


        # Create reference profile.
        profiles[style] = {
            "average_speed": round(
                average_speed,
                2
            ),

            "average_acceleration": round(
                average_acceleration,
                3
            ),

            "hard_braking_rate": round(
                average_braking_rate,
                2
            )
        }


    return profiles


if __name__ == "__main__":

    profiles = build_profiles()


    print("\n" + "=" * 60)
    print("REFERENCE DRIVER PROFILES")
    print("=" * 60)


    for style, profile in profiles.items():

        print(f"\n{style.upper()}")

        print(
            f"Average speed: "
            f"{profile['average_speed']:.2f} km/h"
        )

        print(
            f"Average acceleration: "
            f"{profile['average_acceleration']:.3f} m/s²"
        )

        print(
            f"Average hard-braking rate: "
            f"{profile['hard_braking_rate']:.2f}%"
        )


    print("\n" + "=" * 60)