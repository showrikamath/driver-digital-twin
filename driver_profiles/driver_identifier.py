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

# IMPORTANT:
# These are fixed feature ranges for driver identification.
# Do NOT calculate them from the current profiles.
#
# The old version used min/max values from the available
# profiles. That made the distance scale change whenever a
# dynamic driver profile was added, which could turn a normal
# known driver into UNKNOWN.
#
# These ranges match the simulation's feature space.
SPEED_MIN = 0.0
SPEED_MAX = 100.0

ACCELERATION_MIN = -4.0
ACCELERATION_MAX = 4.0

BRAKING_MIN = -10.0
BRAKING_MAX = 0.0

# Maximum normalized Euclidean distance accepted as a known
# driver. This is intentionally moderate so genuinely different
# behaviour can still become UNKNOWN.
DISTANCE_THRESHOLD = 0.55

# Minimum confidence we display for an accepted known profile.
# This does NOT force recognition; the distance threshold still
# decides whether the driver is known.
MIN_ACCEPTED_CONFIDENCE = 0.05


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value, minimum, maximum):

    if maximum == minimum:
        return 0.0

    normalized = (
        (value - minimum)
        / (maximum - minimum)
    )

    # Keep values inside the feature space.
    return max(
        0.0,
        min(1.0, normalized)
    )


# ============================================================
# EUCLIDEAN DISTANCE
# ============================================================

def calculate_distance(trip, profile):

    trip_speed = normalize(
        trip["average_speed"],
        SPEED_MIN,
        SPEED_MAX
    )

    profile_speed = normalize(
        profile["average_speed"],
        SPEED_MIN,
        SPEED_MAX
    )

    trip_acceleration = normalize(
        trip["average_acceleration"],
        ACCELERATION_MIN,
        ACCELERATION_MAX
    )

    profile_acceleration = normalize(
        profile["average_acceleration"],
        ACCELERATION_MIN,
        ACCELERATION_MAX
    )

    trip_braking = normalize(
        -abs(trip["hard_braking_rate"]),
        BRAKING_MIN,
        BRAKING_MAX
    )

    profile_braking = normalize(
        -abs(profile["hard_braking_rate"]),
        BRAKING_MIN,
        BRAKING_MAX
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
# CONFIDENCE
# ============================================================

def calculate_confidence(distance):

    if distance >= DISTANCE_THRESHOLD:
        return 0.0

    confidence = (
        1.0
        -
        (
            distance
            /
            DISTANCE_THRESHOLD
        )
    )

    return max(
        MIN_ACCEPTED_CONFIDENCE,
        min(1.0, confidence)
    )


# ============================================================
# DRIVER IDENTIFICATION
# ============================================================

def identify_driver(trip, twin=None):

    # --------------------------------------------------------
    # Load built-in reference profiles.
    # --------------------------------------------------------

    profiles = build_profiles()

    # --------------------------------------------------------
    # Add dynamically learned profiles.
    # --------------------------------------------------------

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
    # No profiles available.
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
    # Calculate distance to every profile.
    # --------------------------------------------------------

    distances = {}

    for driver_id, profile in profiles.items():

        distance = calculate_distance(
            trip,
            profile
        )

        distances[driver_id] = distance

    # --------------------------------------------------------
    # Closest profile.
    # --------------------------------------------------------

    closest_driver = min(
        distances,
        key=distances.get
    )

    closest_distance = distances[
        closest_driver
    ]

    confidence = calculate_confidence(
        closest_distance
    )

    # --------------------------------------------------------
    # Diagnostic information.
    # --------------------------------------------------------

    print("\n>>> DRIVER MATCHING")

    print(
        f">>> Closest profile: "
        f"{closest_driver.upper()}"
    )

    print(
        f">>> Distance: "
        f"{closest_distance:.3f}"
    )

    print(
        f">>> Threshold: "
        f"{DISTANCE_THRESHOLD:.3f}"
    )

    print(
        f">>> Confidence: "
        f"{confidence * 100:.1f}%"
    )

    # Show all distances so the matching process is visible
    # during the presentation/demo.
    print("\n>>> Profile distances:")

    for driver_id, distance in sorted(
        distances.items(),
        key=lambda item: item[1]
    ):

        print(
            f"    {driver_id:12} "
            f"→ {distance:.3f}"
        )

    # ========================================================
    # KNOWN DRIVER
    # ========================================================

    if closest_distance <= DISTANCE_THRESHOLD:

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
    # First / second unknown observation.
    # --------------------------------------------------------

    if unknown_count < 3:

        remaining = 3 - unknown_count

        print(
            f">>> More evidence required."
        )

        print(
            f">>> Waiting for "
            f"{remaining} more "
            f"unknown trip(s)."
        )

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

    # ========================================================
    # THREE UNKNOWN TRIPS AVAILABLE
    # ========================================================

    print(
        "\n>>> Three unknown trips collected."
    )

    print(
        ">>> Checking whether they represent "
        "one consistent new driver..."
    )

    profile_created, new_profile = (
        check_unknown_group()
    )

    # --------------------------------------------------------
    # New driver successfully created.
    # --------------------------------------------------------

    if profile_created:

        new_driver_id = (
            new_profile["driver_id"]
        )

        print(
            f">>> NEW DRIVER CREATED: "
            f"{new_driver_id.upper()}"
        )

        if twin:

            twin.update_driver_state(
                driver_profile=new_driver_id,
                identification_distance=closest_distance,
                confidence=confidence
            )

        return (
            new_driver_id,
            distances,
            closest_distance,
            True
        )

    # --------------------------------------------------------
    # Three trips were not consistent.
    # --------------------------------------------------------

    print(
        "\n>>> Trips were not consistent enough."
    )

    print(
        ">>> No new driver profile was created."
    )

    print(
        ">>> More evidence is required."
    )

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
# DISPLAY RESULT
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

    for style, distance in sorted(
        distances.items(),
        key=lambda item: item[1]
    ):

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

        print(
            f"Confidence: "
            f"{calculate_confidence(closest_distance) * 100:.1f}%"
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
            "name": "Test Calm",
            "average_speed": 50.0,
            "average_acceleration": 0.35,
            "hard_braking_rate": 3.33
        },

        {
            "name": "Test Normal",
            "average_speed": 60.0,
            "average_acceleration": 0.35,
            "hard_braking_rate": 3.33
        },

        {
            "name": "Test Aggressive",
            "average_speed": 75.0,
            "average_acceleration": 0.35,
            "hard_braking_rate": 3.33
        }
    ]

    for trip in test_trips:

        print(
            "\n\n"
            + "#" * 60
        )

        print(
            f"TESTING: {trip['name']}"
        )

        print(
            "#" * 60
        )

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