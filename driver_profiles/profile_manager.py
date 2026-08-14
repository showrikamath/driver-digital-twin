import json
import math
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROFILE_FILE = BASE_DIR / "driver_profiles.json"
UNKNOWN_TRIPS_FILE = BASE_DIR / "unknown_trips.json"

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
    trip_a,
    trip_b,
    all_trips
):

    SPEED_MIN = 0.0
    SPEED_MAX = 120.0

    ACCELERATION_MIN = 0.0
    ACCELERATION_MAX = 4.0

    BRAKING_MIN = 0.0
    BRAKING_MAX = 10.0


    # --------------------------------------------------------
    # Speed
    # --------------------------------------------------------

    speed_a = normalize(
        trip_a["average_speed"],
        SPEED_MIN,
        SPEED_MAX
    )

    speed_b = normalize(
        trip_b["average_speed"],
        SPEED_MIN,
        SPEED_MAX
    )


    # --------------------------------------------------------
    # Acceleration
    # --------------------------------------------------------

    acceleration_a = normalize(
        trip_a["average_acceleration"],
        ACCELERATION_MIN,
        ACCELERATION_MAX
    )

    acceleration_b = normalize(
        trip_b["average_acceleration"],
        ACCELERATION_MIN,
        ACCELERATION_MAX
    )


    # --------------------------------------------------------
    # Hard braking
    # --------------------------------------------------------

    braking_a = normalize(
        trip_a["hard_braking_rate"],
        BRAKING_MIN,
        BRAKING_MAX
    )

    braking_b = normalize(
        trip_b["hard_braking_rate"],
        BRAKING_MIN,
        BRAKING_MAX
    )


    # --------------------------------------------------------
    # Euclidean distance
    # --------------------------------------------------------

    distance = math.sqrt(

        (speed_a - speed_b) ** 2

        +

        (acceleration_a - acceleration_b) ** 2

        +

        (braking_a - braking_b) ** 2

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


    # --------------------------------------------------------
    # Compare every unknown trip with every other trip.
    # --------------------------------------------------------

    distances = []


    for i in range(len(trips)):

        for j in range(i + 1, len(trips)):

            trip_a = trips[i]
            trip_b = trips[j]


            # Use trip_a as the "group average" argument.
            # The function only needs the feature values.
            distance = calculate_unknown_group_distance(
                trip_b,
                trip_a,
                trips
            )


            distances.append(distance)


    # --------------------------------------------------------
    # Find the largest difference.
    #
    # We use the maximum rather than the average because
    # EVERY trip should be reasonably similar.
    # --------------------------------------------------------

    max_distance = max(distances)


    print(
        f"\n>>> Maximum unknown-trip distance: "
        f"{max_distance:.3f}"
    )


    # --------------------------------------------------------
    # Consistent group
    # --------------------------------------------------------

    if max_distance <= UNKNOWN_GROUP_THRESHOLD:

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


    # --------------------------------------------------------
    # Inconsistent group
    # --------------------------------------------------------

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