import json
import math
from pathlib import Path


PROFILE_FILE = Path("driver_profiles.json")
UNKNOWN_TRIPS_FILE = Path("unknown_trips.json")

MIN_TRIPS_FOR_NEW_PROFILE = 3
UNKNOWN_GROUP_THRESHOLD = 0.5


def load_json(file_path, default):

    if not file_path.exists():
        return default

    try:

        with open(file_path, "r") as file:

            content = file.read().strip()

            if not content:
                return default

            return json.loads(content)

    except (json.JSONDecodeError, OSError):

        return default


def save_json(file_path, data):

    with open(file_path, "w") as file:

        json.dump(
            data,
            file,
            indent=4
        )


def load_profiles():

    return load_json(
        PROFILE_FILE,
        []
    )


def get_unknown_trips():

    return load_json(
        UNKNOWN_TRIPS_FILE,
        []
    )


def save_unknown_trips(trips):

    save_json(
        UNKNOWN_TRIPS_FILE,
        trips
    )


def add_unknown_trip(trip):

    unknown_trips = get_unknown_trips()

    unknown_trips.append(trip)

    save_unknown_trips(
        unknown_trips
    )

    return len(unknown_trips)


def clear_unknown_trips():

    save_unknown_trips([])


# ============================================================
# UNKNOWN GROUP PROFILE
# ============================================================

def calculate_group_average(trips):

    average_speed = (
        sum(
            trip["average_speed"]
            for trip in trips
        )
        / len(trips)
    )

    average_acceleration = (
        sum(
            trip["average_acceleration"]
            for trip in trips
        )
        / len(trips)
    )

    average_braking_rate = (
        sum(
            trip["hard_braking_rate"]
            for trip in trips
        )
        / len(trips)
    )

    return {
        "average_speed": average_speed,

        "average_acceleration":
            average_acceleration,

        "hard_braking_rate":
            average_braking_rate
    }


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value, minimum, maximum):

    if maximum == minimum:

        return 0.0

    return (
        (value - minimum)
        /
        (maximum - minimum)
    )


# ============================================================
# UNKNOWN TRIP SIMILARITY
# ============================================================

def calculate_unknown_group_distance(
    trip,
    group_average,
    all_trips
):

    speeds = [
        t["average_speed"]
        for t in all_trips
    ]

    accelerations = [
        t["average_acceleration"]
        for t in all_trips
    ]

    braking_rates = [
        t["hard_braking_rate"]
        for t in all_trips
    ]


    speed_min = min(speeds)
    speed_max = max(speeds)

    acceleration_min = min(accelerations)
    acceleration_max = max(accelerations)

    braking_min = min(braking_rates)
    braking_max = max(braking_rates)


    trip_speed = normalize(
        trip["average_speed"],
        speed_min,
        speed_max
    )

    group_speed = normalize(
        group_average["average_speed"],
        speed_min,
        speed_max
    )


    trip_acceleration = normalize(
        trip["average_acceleration"],
        acceleration_min,
        acceleration_max
    )

    group_acceleration = normalize(
        group_average["average_acceleration"],
        acceleration_min,
        acceleration_max
    )


    trip_braking = normalize(
        trip["hard_braking_rate"],
        braking_min,
        braking_max
    )

    group_braking = normalize(
        group_average["hard_braking_rate"],
        braking_min,
        braking_max
    )


    distance = math.sqrt(

        (trip_speed - group_speed) ** 2

        +

        (trip_acceleration - group_acceleration) ** 2

        +

        (trip_braking - group_braking) ** 2

    )


    return distance


# ============================================================
# NEW PROFILE
# ============================================================

def create_new_profile(
    trips,
    profile_id
):

    group_average = calculate_group_average(
        trips
    )

    profile = {

        "driver_id": profile_id,

        "trip_count": len(trips),

        "average_speed": round(
            group_average["average_speed"],
            2
        ),

        "average_acceleration": round(
            group_average["average_acceleration"],
            3
        ),

        "hard_braking_rate": round(
            group_average["hard_braking_rate"],
            2
        )
    }

    return profile


def save_new_profile(profile):

    profiles = load_profiles()

    profiles.append(profile)

    save_json(
        PROFILE_FILE,
        profiles
    )


def get_next_profile_id():

    profiles = load_profiles()

    return f"driver_{len(profiles) + 1}"


# ============================================================
# CHECK UNKNOWN GROUP
# ============================================================

def check_unknown_group():

    trips = get_unknown_trips()

    if len(trips) < MIN_TRIPS_FOR_NEW_PROFILE:

        return False, None


    # Use all collected unknown trips
    # to calculate the current group behaviour.

    group_average = calculate_group_average(
        trips
    )


    # Compare every trip against the group average.

    distances = []

    for trip in trips:

        distance = calculate_unknown_group_distance(
            trip,
            group_average,
            trips
        )

        distances.append(distance)


    average_distance = (
        sum(distances)
        /
        len(distances)
    )


    print(
        f"\n>>> Unknown-group distance: "
        f"{average_distance:.3f}"
    )


    # --------------------------------------------------------
    # Decide whether the trips are similar enough.
    # --------------------------------------------------------

    if average_distance <= UNKNOWN_GROUP_THRESHOLD:

        profile_id = get_next_profile_id()

        new_profile = create_new_profile(
            trips,
            profile_id
        )

        save_new_profile(
            new_profile
        )

        clear_unknown_trips()


        print(
            "\n>>> UNKNOWN TRIPS ARE CONSISTENT"
        )

        print(
            f">>> Created {profile_id}"
        )


        return True, new_profile


    print(
        "\n>>> UNKNOWN TRIPS ARE TOO DIFFERENT"
    )

    print(
        ">>> More evidence is required."
    )


    return False, None


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)

    print("PROFILE MANAGER")

    print("=" * 60)

    print(
        f"Dynamic profiles: "
        f"{len(load_profiles())}"
    )

    print(
        f"Unknown trips waiting: "
        f"{len(get_unknown_trips())}"
    )

    print(
        f"Required trips: "
        f"{MIN_TRIPS_FOR_NEW_PROFILE}"
    )

    print(
        f"Group threshold: "
        f"{UNKNOWN_GROUP_THRESHOLD}"
    )

    print("=" * 60)