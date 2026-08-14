import json
import math
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROFILE_FILE = BASE_DIR / "driver_profiles.json"
UNKNOWN_TRIPS_FILE = BASE_DIR / "unknown_trips.json"

MIN_TRIPS_FOR_NEW_PROFILE = 3
UNKNOWN_GROUP_THRESHOLD = 0.75


# ============================================================
# JSON HELPERS
# ============================================================

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


# ============================================================
# DYNAMIC PROFILES
# ============================================================

def load_profiles():

    return load_json(
        PROFILE_FILE,
        []
    )


def save_new_profile(profile):

    profiles = load_profiles()

    profiles.append(profile)

    save_json(
        PROFILE_FILE,
        profiles
    )


def get_next_profile_id():

    profiles = load_profiles()

    # Find the highest existing dynamic driver number.
    # This prevents duplicate IDs if profiles are ever
    # removed manually.
    highest_number = 0

    for profile in profiles:

        driver_id = str(
            profile.get(
                "driver_id",
                ""
            )
        )

        if driver_id.startswith(
            "driver_"
        ):

            try:

                number = int(
                    driver_id.split(
                        "_"
                    )[1]
                )

                highest_number = max(
                    highest_number,
                    number
                )

            except (
                ValueError,
                IndexError
            ):

                pass

    return f"driver_{highest_number + 1}"


# ============================================================
# UNKNOWN TRIPS
# ============================================================

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

    unknown_trips.append(
        trip
    )

    save_unknown_trips(
        unknown_trips
    )

    return len(
        unknown_trips
    )


def clear_unknown_trips():

    """
    Clear only the temporary unknown-trip queue.

    IMPORTANT:
    This does NOT delete driver_1, driver_2, etc.
    """

    save_unknown_trips(
        []
    )


def get_learning_progress():

    """
    Return the current unknown-driver learning progress.

    Example:
        0/3
        1/3
        2/3
        3/3
    """

    count = len(
        get_unknown_trips()
    )

    return min(
        count,
        MIN_TRIPS_FOR_NEW_PROFILE
    )


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

        "average_speed":
            average_speed,

        "average_acceleration":
            average_acceleration,

        "hard_braking_rate":
            average_braking_rate
    }


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(
    value,
    minimum,
    maximum
):

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
    all_trips=None
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

        "driver_id":
            profile_id,

        "trip_count":
            len(trips),

        "average_speed":
            round(
                group_average[
                    "average_speed"
                ],
                2
            ),

        "average_acceleration":
            round(
                group_average[
                    "average_acceleration"
                ],
                3
            ),

        "hard_braking_rate":
            round(
                group_average[
                    "hard_braking_rate"
                ],
                2
            )
    }

    return profile


# ============================================================
# CHECK UNKNOWN GROUP
# ============================================================

def check_unknown_group():

    all_trips = get_unknown_trips()

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Only the most recent 3 observations are considered
    # for the current learning decision.
    #
    # This prevents an old, unrelated unknown observation
    # from being included in a new learning group.
    # --------------------------------------------------------

    trips = all_trips[
        -MIN_TRIPS_FOR_NEW_PROFILE:
    ]

    if len(trips) < MIN_TRIPS_FOR_NEW_PROFILE:

        return False, None

    # --------------------------------------------------------
    # Compare every current learning trip with every other
    # current learning trip.
    # --------------------------------------------------------

    distances = []

    for i in range(
        len(trips)
    ):

        for j in range(
            i + 1,
            len(trips)
        ):

            trip_a = trips[i]
            trip_b = trips[j]

            distance = (
                calculate_unknown_group_distance(
                    trip_b,
                    trip_a,
                    trips
                )
            )

            distances.append(
                distance
            )

    # --------------------------------------------------------
    # Find largest difference.
    #
    # Every observation must be reasonably similar.
    # --------------------------------------------------------

    max_distance = max(
        distances
    )

    print(
        f"\n>>> Maximum unknown-trip distance: "
        f"{max_distance:.3f}"
    )

    # --------------------------------------------------------
    # CONSISTENT GROUP
    # --------------------------------------------------------

    if (
        max_distance
        <= UNKNOWN_GROUP_THRESHOLD
    ):

        profile_id = (
            get_next_profile_id()
        )

        new_profile = (
            create_new_profile(
                trips,
                profile_id
            )
        )

        save_new_profile(
            new_profile
        )

        # The observations have now been consumed
        # to create the new profile.
        clear_unknown_trips()

        print(
            "\n>>> UNKNOWN TRIPS ARE CONSISTENT"
        )

        print(
            f">>> Created {profile_id}"
        )

        return (
            True,
            new_profile
        )

    # --------------------------------------------------------
    # INCONSISTENT GROUP
    # --------------------------------------------------------

    print(
        "\n>>> UNKNOWN TRIPS ARE TOO DIFFERENT"
    )

    print(
        ">>> More evidence is required."
    )

    # --------------------------------------------------------
    # Keep only the newest two observations.
    #
    # This prevents an old incompatible trip from remaining
    # forever and contaminating future learning.
    # --------------------------------------------------------

    save_unknown_trips(
        trips[
            -(MIN_TRIPS_FOR_NEW_PROFILE - 1):
        ]
    )

    return (
        False,
        None
    )


# ============================================================
# TEST / STATUS
# ============================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 60
    )

    print(
        "PROFILE MANAGER"
    )

    print(
        "=" * 60
    )

    print(
        f"Dynamic profiles: "
        f"{len(load_profiles())}"
    )

    print(
        f"Unknown trips waiting: "
        f"{len(get_unknown_trips())}"
    )

    print(
        f"Learning progress: "
        f"{get_learning_progress()}/"
        f"{MIN_TRIPS_FOR_NEW_PROFILE}"
    )

    print(
        f"Required trips: "
        f"{MIN_TRIPS_FOR_NEW_PROFILE}"
    )

    print(
        f"Group threshold: "
        f"{UNKNOWN_GROUP_THRESHOLD}"
    )

    print(
        "=" * 60
    )