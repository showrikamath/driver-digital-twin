from driver_profiles.driver_identifier import identify_driver
from digital_twin.digital_twin import DigitalTwin


# ============================================================
# THREE TRAINING TRIPS
# ============================================================
# These three trips represent the SAME unknown driver.
# They are deliberately very similar.

TRAINING_TRIPS = [

    {
        "average_speed": 61.0,
        "average_acceleration": 0.05,
        "hard_braking_rate": 7.0
    },

    {
        "average_speed": 62.0,
        "average_acceleration": 0.06,
        "hard_braking_rate": 7.0
    },

    {
        "average_speed": 60.0,
        "average_acceleration": 0.04,
        "hard_braking_rate": 7.0
    }
]


# ============================================================
# FOURTH TRIP
# ============================================================
# This is another trip from the SAME driver.
# It should be recognized as DRIVER_1 after learning.

FOLLOW_UP_TRIP = {

    "average_speed": 61.5,
    "average_acceleration": 0.05,
    "hard_braking_rate": 7.0
}


# ============================================================
# DISPLAY HELPER
# ============================================================

def display_result(number, trip, driver, twin):

    print(
        f"\nTrip {number}"
    )

    print(
        f"Speed: {trip['average_speed']:.2f} km/h"
    )

    print(
        f"Acceleration: "
        f"{trip['average_acceleration']:.2f} m/s²"
    )

    print(
        f"Hard braking rate: "
        f"{trip['hard_braking_rate']:.2f}%"
    )

    print(
        f"Result: {driver.upper()}"
    )

    print(
        f"Twin profile: "
        f"{twin.get_state()['driver_profile']}"
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "#" * 60)
    print("DYNAMIC DRIVER PROFILE TEST")
    print("#" * 60)


    # ========================================================
    # STEP 1 — TRAINING
    # ========================================================

    print("\n")
    print("=" * 60)
    print("STEP 1 — LEARNING UNKNOWN DRIVER")
    print("=" * 60)


    for number, trip in enumerate(
        TRAINING_TRIPS,
        start=1
    ):

        twin = DigitalTwin()

        (
            driver,
            distances,
            closest_distance,
            is_unknown
        ) = identify_driver(
            trip,
            twin
        )

        display_result(
            number,
            trip,
            driver,
            twin
        )


    # ========================================================
    # STEP 2 — FUTURE TRIP
    # ========================================================

    print("\n")
    print("=" * 60)
    print("STEP 2 — FUTURE TRIP")
    print("=" * 60)

    twin = DigitalTwin()

    (
        driver,
        distances,
        closest_distance,
        is_unknown
    ) = identify_driver(
        FOLLOW_UP_TRIP,
        twin
    )

    display_result(
        4,
        FOLLOW_UP_TRIP,
        driver,
        twin
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n")
    print("=" * 60)
    print("FINAL TEST RESULT")
    print("=" * 60)

    if driver == "driver_1":

        print(
            "✓ SUCCESS"
        )

        print(
            "DRIVER_1 was created and "
            "recognized on the future trip."
        )

    else:

        print(
            "✗ FAILED"
        )

        print(
            "DRIVER_1 was not recognized "
            "on the future trip."
        )

    print("=" * 60)