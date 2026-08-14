from driver_profiles.driver_identifier import identify_driver
from digital_twin.digital_twin import DigitalTwin
from driver_profiles.profile_builder import build_profiles


# ============================================================
# TEST TRIPS
# ============================================================

profiles = build_profiles()

TEST_TRIPS = {

    "CALM": {
        "average_speed": profiles["calm"]["average_speed"],
        "average_acceleration": profiles["calm"]["average_acceleration"],
        "hard_braking_rate": profiles["calm"]["hard_braking_rate"]
    },

    "NORMAL": {
        "average_speed": profiles["normal"]["average_speed"],
        "average_acceleration": profiles["normal"]["average_acceleration"],
        "hard_braking_rate": profiles["normal"]["hard_braking_rate"]
    },

    "AGGRESSIVE": {
        "average_speed": profiles["aggressive"]["average_speed"],
        "average_acceleration": profiles["aggressive"]["average_acceleration"],
        "hard_braking_rate": profiles["aggressive"]["hard_braking_rate"]
    },

    "UNKNOWN": {
        "average_speed": 61.0,
        "average_acceleration": 0.04,
        "hard_braking_rate": 7.0
    }
}

# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":

    for expected, trip in TEST_TRIPS.items():

        print("\n" + "#" * 60)
        print(f"TESTING EXPECTED DRIVER: {expected}")
        print("#" * 60)

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

        print(
            f"\nExpected: {expected}"
        )

        print(
            f"Result:   {driver.upper()}"
        )

        print(
            f"Distance: "
            f"{closest_distance:.3f}"
            if closest_distance is not None
            else "Distance: N/A"
        )

        print(
            f"Twin profile: "
            f"{twin.get_state()['driver_profile']}"
        )

        if expected == driver.upper():
            print("✓ TEST PASSED")
        else:
            print("✗ TEST RESULT DIFFERENT")