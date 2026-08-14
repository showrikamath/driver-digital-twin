import math

from driver_profiles.profile_builder import build_profiles

from driver_profiles.profile_manager import (
    add_unknown_trip,
    check_unknown_group,
    load_profiles,
)

from digital_twin.digital_twin import DigitalTwin


# ============================================================
# CONFIGURATION
# ============================================================

DISTANCE_THRESHOLD = 0.5


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value, minimum, maximum):

    if maximum == minimum:
        return 0.0

    return (
        (value - minimum)
        / (maximum - minimum)
    )


# ============================================================
# EUCLIDEAN DISTANCE
# ============================================================

def calculate_distance(trip, profile, ranges):

    trip_speed = normalize(
        trip["average_speed"],
        ranges["speed_min"],
        ranges["speed_max"]
    )

    profile_speed = normalize(
        profile["average_speed"],
        ranges["speed_min"],
        ranges["speed_max"]
    )

    trip_acceleration = normalize(
        trip["average_acceleration"],
        ranges["acceleration_min"],
        ranges["acceleration_max"]
    )

    profile_acceleration = normalize(
        profile["average_acceleration"],
        ranges["acceleration_min"],
        ranges["acceleration_max"]
    )

    trip_braking = normalize(
        trip["hard_braking_rate"],
        ranges["braking_min"],
        ranges["braking_max"]
    )

    profile_braking = normalize(
        profile["hard_braking_rate"],
        ranges["braking_min"],
        ranges["braking_max"]
    )

    distance = math.sqrt(
        (trip_speed - profile_speed) ** 2
        +
        (trip_acceleration - profile_acceleration) ** 2
        +
        (trip_braking - profile_braking) ** 2
    )

    return distance


# ============================================================
# DRIVER IDENTIFICATION
# ============================================================

def identify_driver(trip, twin=None):

    profiles = build_profiles()

    dynamic_profiles = load_profiles()

    for profile in dynamic_profiles:

        profiles[profile["driver_id"]] = {
            "average_speed":
                profile["average_speed"],

            "average_acceleration":
                profile["average_acceleration"],

            "hard_braking_rate":
                profile["hard_braking_rate"]
    }

    # --------------------------------------------------------
    # No reference profiles
    # --------------------------------------------------------

    if not profiles:

        add_unknown_trip(trip)

        if twin:
            twin.update_driver_state(
                driver_profile="UNKNOWN",
                identification_distance=None,
                confidence=0.0
            )

        return (
            "UNKNOWN",
            {},
            None,
            True
        )


    # --------------------------------------------------------
    # Feature ranges
    # --------------------------------------------------------

    speeds = [
        profile["average_speed"]
        for profile in profiles.values()
    ]

    accelerations = [
        profile["average_acceleration"]
        for profile in profiles.values()
    ]

    braking_rates = [
        profile["hard_braking_rate"]
        for profile in profiles.values()
    ]

    ranges = {

        "speed_min": min(speeds),
        "speed_max": max(speeds),

        "acceleration_min":
            min(accelerations),

        "acceleration_max":
            max(accelerations),

        "braking_min":
            min(braking_rates),

        "braking_max":
            max(braking_rates)
    }


    # --------------------------------------------------------
    # Calculate distances
    # --------------------------------------------------------

    distances = {}

    for style, profile in profiles.items():

        distance = calculate_distance(
            trip,
            profile,
            ranges
        )

        distances[style] = distance


    # --------------------------------------------------------
    # Find closest profile
    # --------------------------------------------------------

    closest_driver = min(
        distances,
        key=distances.get
    )

    closest_distance = distances[
        closest_driver
    ]


    # --------------------------------------------------------
    # KNOWN DRIVER
    # --------------------------------------------------------

    if closest_distance <= DISTANCE_THRESHOLD:

        # Convert distance into a simple confidence score.
        confidence = max(
            0.0,
            1.0 - (
                closest_distance
                / DISTANCE_THRESHOLD
            )
        )

        if twin:
            twin.update_driver_state(
                driver_profile=closest_driver,
                identification_distance=closest_distance,
                confidence=confidence
            )

        return (
            closest_driver,
            distances,
            closest_distance,
            False
        )


    # ========================================================
    # UNKNOWN DRIVER
    # ========================================================

    print(
        "\n>>> No existing profile is close enough."
    )

    unknown_count = add_unknown_trip(
        trip
    )

    print(
        f">>> Unknown trip stored: "
        f"{unknown_count}/3"
    )


    # --------------------------------------------------------
    # Need at least 3 observations
    # --------------------------------------------------------

    if unknown_count < 3:

        if twin:
            twin.update_driver_state(
                driver_profile="UNKNOWN",
                identification_distance=closest_distance,
                confidence=0.0
            )

        return (
            "UNKNOWN",
            distances,
            closest_distance,
            True
        )


    # --------------------------------------------------------
    # Check unknown group
    # --------------------------------------------------------

    profile_created, new_profile = (
        check_unknown_group()
    )


    # --------------------------------------------------------
    # New driver profile created
    # --------------------------------------------------------

    if profile_created:

        new_driver_id = new_profile["driver_id"]

        if twin:
            twin.update_driver_state(
                driver_profile=new_driver_id,
                identification_distance=closest_distance,
                confidence=0.0
            )

        return (
            new_driver_id,
            distances,
            closest_distance,
            True
        )


    # --------------------------------------------------------
    # Trips were too different
    # --------------------------------------------------------

    if twin:
        twin.update_driver_state(
            driver_profile="UNKNOWN",
            identification_distance=closest_distance,
            confidence=0.0
        )

    return (
        "UNKNOWN",
        distances,
        closest_distance,
        True
    )


# ============================================================
# DISPLAY
# ============================================================

def display_result(
    trip,
    driver,
    distances,
    closest_distance
):

    print("\n" + "=" * 60)

    print("DRIVER IDENTIFICATION")

    print("=" * 60)

    print("\nTrip metrics:")

    print(
        f"Average speed: "
        f"{trip['average_speed']:.2f} km/h"
    )

    print(
        f"Average acceleration: "
        f"{trip['average_acceleration']:.3f} m/s²"
    )

    print(
        f"Hard braking rate: "
        f"{trip['hard_braking_rate']:.2f}%"
    )

    print("\nDistances:")

    for style, distance in distances.items():

        print(
            f"{style.capitalize():12} → "
            f"{distance:.3f}"
        )

    if closest_distance is not None:

        print(
            f"\nClosest distance: "
            f"{closest_distance:.3f}"
        )

        print(
            f"Threshold: "
            f"{DISTANCE_THRESHOLD:.3f}"
        )

    print("\n" + "-" * 60)

    if driver == "UNKNOWN":

        print(
            "RESULT: UNKNOWN "
            "(collecting more evidence)"
        )

    elif driver.startswith("driver_"):

        print(
            f"RESULT: NEW PROFILE → "
            f"{driver.upper()}"
        )

    else:

        print(
            f"RESULT: "
            f"{driver.upper()}"
        )

    print("-" * 60)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    twin = DigitalTwin()

    test_trips = [

        {
            "name": "Unknown Trip A",
            "average_speed": 60.0,
            "average_acceleration": 0.05,
            "hard_braking_rate": 8.0
        },

        {
            "name": "Unknown Trip B",
            "average_speed": 68.0,
            "average_acceleration": 0.50,
            "hard_braking_rate": 1.0
        },

        {
            "name": "Unknown Trip C",
            "average_speed": 52.0,
            "average_acceleration": 0.15,
            "hard_braking_rate": 6.0
        }
    ]

    for trip in test_trips:

        print("\n\n" + "#" * 60)

        print(
            f"TESTING: {trip['name']}"
        )

        print("#" * 60)

        trip_data = {

            "average_speed":
                trip["average_speed"],

            "average_acceleration":
                trip["average_acceleration"],

            "hard_braking_rate":
                trip["hard_braking_rate"]
        }

        (
            driver,
            distances,
            closest_distance,
            is_unknown
        ) = identify_driver(
            trip_data,
            twin
        )

        display_result(
            trip_data,
            driver,
            distances,
            closest_distance
        )

        print(
            "\nDIGITAL TWIN DRIVER STATE:"
        )

        print(
            twin.get_state()
        )