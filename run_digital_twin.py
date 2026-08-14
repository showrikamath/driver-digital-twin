from simulation.simulator import run_simulation
from driver_profiles.driver_identifier import identify_driver
from driver_profiles.profile_manager import (
    load_profiles,
    clear_unknown_trips,
    add_unknown_trip,
    check_unknown_group,
    get_unknown_trips,
)
from digital_twin.digital_twin import DigitalTwin
from visualization.visualization import LiveDashboard

import matplotlib.pyplot as plt
import random


# ============================================================
# DIGITAL TWIN DEMO
# ============================================================

def run_demo(driver_style):

    print("\n")
    print("=" * 60)
    print("DRIVER DIGITAL TWIN — INTEGRATED DEMO")
    print("=" * 60)

    print(
        f"\nSimulating driver: "
        f"{driver_style.upper()}"
    )

    twin = DigitalTwin()
    dashboard = LiveDashboard()

    print("\nStarting simulation...\n")

    result = run_simulation(
        driver_style,
        twin,
        telemetry_callback=dashboard.update
    )

    trip = result["trip"]

    print("\n")
    print("=" * 60)
    print("DRIVER IDENTIFICATION")
    print("=" * 60)

    (
        driver,
        distances,
        closest_distance,
        is_unknown
    ) = identify_driver(
        trip,
        twin
    )

    state = twin.get_state()

    # Make the final identification visible in the
    # already-open dashboard.
    dashboard.update(state)
    dashboard.finalize(state)

    print("\n")
    print("=" * 60)
    print("FINAL DIGITAL TWIN")
    print("=" * 60)

    print(
        f"Speed:                 "
        f"{state['speed']:.2f} km/h"
    )

    print(
        f"Desired speed:         "
        f"{state['desired_speed']:.2f} km/h"
    )

    print(
        f"Target speed:          "
        f"{state['target_speed']:.2f} km/h"
    )

    print(
        f"Acceleration:          "
        f"{state['acceleration']:.2f} m/s²"
    )

    print(
        f"Braking:               "
        f"{state['braking']:.2f} m/s²"
    )

    print(
        f"Action:                "
        f"{state['action']}"
    )

    print(
        f"Driver profile:        "
        f"{state['driver_profile']}"
    )

    print(
        f"Identification distance: "
        f"{state['identification_distance']}"
        if state["identification_distance"] is not None
        else
        "Identification distance: N/A"
    )

    print(
        f"Confidence:            "
        f"{state['confidence']:.2f}"
    )

    print(
        f"Elapsed time:          "
        f"{state['elapsed_time']:.0f}s"
    )

    print("=" * 60)

    print(
        f"\nFINAL RESULT: "
        f"{driver.upper()}"
    )

    print("=" * 60)

    plt.ioff()
    plt.show()


# ============================================================
# DASHBOARD LEARNING STATUS
# ============================================================

def update_learning_dashboard(
    dashboard,
    twin,
    trip_number,
    total_trips,
    status,
    profile_name="UNKNOWN"
):
    """
    Update the existing dashboard with learning progress.

    We reuse the same dashboard window instead of opening
    a new graph for every training trip.
    """

    state = twin.get_state()

    # Keep the real Twin state, but display the learning
    # progress in the dashboard header.
    try:

        dashboard.header_text.set_text(
            "DRIVER DIGITAL TWIN\n\n"
            f"Profile: {profile_name.upper()}    "
            f"Confidence: "
            f"{state['confidence']:.0%}    "
            f"Speed: "
            f"{state['speed']:.2f} km/h\n\n"
            "NEW DRIVER LEARNING\n"
            f"Progress: {trip_number}/{total_trips} trips\n"
            f"Status: {status}"
        )

        dashboard.footer.set_text(
            f"Learning progress: "
            f"{trip_number}/{total_trips}    |    "
            f"Elapsed: "
            f"{state['elapsed_time']:.0f}s"
        )

        dashboard.fig.canvas.draw()
        dashboard.fig.canvas.flush_events()

        plt.pause(0.05)

    except AttributeError:

        # Fallback for an older visualization module.
        dashboard.update(
            state
        )


# ============================================================
# NEW DRIVER LEARNING DEMO
# ============================================================

def run_new_driver_demo():

    print("\n")
    print("=" * 60)
    print("NEW DRIVER LEARNING DEMO")
    print("=" * 60)

    print(
        "\nThe Digital Twin will collect "
        "three behavioural observations."
    )

    print(
        "Known profiles are NOT used during "
        "these learning trips."
    )

    print(
        "The same dashboard will remain open "
        "throughout the learning process."
    )

    print("=" * 60)

    # Start a completely fresh learning session.
    # This clears only temporary observations.
    # Existing driver_1 / driver_2 profiles remain.
    clear_unknown_trips()

    dashboard = LiveDashboard()

    created_profile = None

    # --------------------------------------------------------
    # Three learning trips
    # --------------------------------------------------------

    for trip_number in range(1, 4):

        print("\n")
        print("-" * 60)

        print(
            f"NEW DRIVER LEARNING — TRIP "
            f"{trip_number}/3"
        )

        print("-" * 60)

        if trip_number == 1:

            status = (
                "COLLECTING FIRST BEHAVIOURAL "
                "OBSERVATION"
            )

        elif trip_number == 2:

            status = (
                "COLLECTING MORE EVIDENCE"
            )

        else:

            status = (
                "COLLECTING FINAL OBSERVATION"
            )

        print(
            f"\nStatus: {status}"
        )

        twin = DigitalTwin()

        # IMPORTANT:
        # Do NOT call identify_driver() here.
        #
        # A New Driver learning session is not supposed
        # to be classified as Calm/Normal/Aggressive.
        # The trip is stored directly as evidence.
        result = run_simulation(
            "new_driver",

            twin,
            telemetry_callback=dashboard.update
        )

        trip = result["trip"]

        # Store the completed trip directly as a learning
        # observation.
        unknown_count = add_unknown_trip(
            trip
        )

        print(
            f"\n>>> Learning observation stored: "
            f"{unknown_count}/3"
        )

        if trip_number < 3:

            print(
                ">>> More evidence required."
            )

            print(
                f">>> Waiting for "
                f"{3 - unknown_count} more "
                f"observation(s)."
            )

            status = (
                "COLLECTING MORE EVIDENCE"
            )

        else:

            print(
                "\n>>> Three observations collected."
            )

            print(
                ">>> Figuring out whether the "
                "behaviour is consistent..."
            )

            status = (
                "ANALYZING BEHAVIOURAL "
                "CONSISTENCY"
            )

        # Show learning progress on the existing dashboard.
        update_learning_dashboard(
            dashboard,
            twin,
            trip_number,
            3,
            status,
            "UNKNOWN"
        )

        print(
            f"\nLearning progress: "
            f"{unknown_count}/3"
        )

    # --------------------------------------------------------
    # Analyze the three observations.
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("LEARNING ANALYSIS")
    print("=" * 60)

    print(
        "\nComparing the three behavioural observations..."
    )

    print(
        "The Twin is checking whether they "
        "represent one consistent driver."
    )

    profile_created, new_profile = (
        check_unknown_group()
    )

    # --------------------------------------------------------
    # Successful profile creation
    # --------------------------------------------------------

    if profile_created:

        created_profile = (
            new_profile["driver_id"]
        )

        print("\n")
        print("=" * 60)

        print(
            f"✓ NEW PROFILE CREATED: "
            f"{created_profile.upper()}"
        )

        print("=" * 60)

        try:

            dashboard.header_text.set_text(
                "DRIVER DIGITAL TWIN\n\n"
                f"Profile: {created_profile.upper()}\n"
                "Confidence: LEARNING COMPLETE\n\n"
                "NEW DRIVER LEARNING COMPLETE\n"
                "Progress: 3/3 trips\n"
                f"Status: NEW PROFILE CREATED — "
                f"{created_profile.upper()}"
            )

            dashboard.footer.set_text(
                "Learning complete    |    "
                f"New profile: "
                f"{created_profile.upper()}"
            )

            dashboard.fig.canvas.draw()
            dashboard.fig.canvas.flush_events()

        except AttributeError:
            pass

        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        print("\n")
        print("=" * 60)
        print("VERIFYING NEW DRIVER")
        print("=" * 60)

        print(
            f"\nExpected result: "
            f"{created_profile.upper()}"
        )

        print(
            "\nRunning verification trip..."
        )

        verification_twin = DigitalTwin()

        result = run_simulation(
            "new_driver",
            verification_twin,
            telemetry_callback=dashboard.update
        )

        verification_trip = result["trip"]

        (
            detected_driver,
            distances,
            closest_distance,
            is_unknown
        ) = identify_driver(
            verification_trip,
            verification_twin
        )

        final_state = (
            verification_twin.get_state()
        )

        try:

            dashboard.header_text.set_text(
                "DRIVER DIGITAL TWIN\n\n"
                f"Profile: "
                f"{detected_driver.upper()}    "
                f"Confidence: "
                f"{final_state['confidence']:.0%}    "
                f"Speed: "
                f"{final_state['speed']:.2f} km/h\n\n"
                "NEW DRIVER LEARNING COMPLETE\n"
                f"Learned Profile: "
                f"{created_profile.upper()}\n"
                f"Verification Result: "
                f"{detected_driver.upper()}"
            )

            dashboard.footer.set_text(
                "Learning complete    |    "
                f"Profile: {created_profile.upper()}    |    "
                f"Verification: {detected_driver.upper()}"
            )

            dashboard.fig.canvas.draw()
            dashboard.fig.canvas.flush_events()

        except AttributeError:

            dashboard.update(
                final_state
            )

        print("\n")
        print("=" * 60)

        print(
            f"EXPECTED: "
            f"{created_profile.upper()}"
        )

        print(
            f"RESULT:   "
            f"{detected_driver.upper()}"
        )

        if (
            detected_driver.lower()
            ==
            created_profile.lower()
        ):

            print(
                "\n✓ NEW DRIVER SUCCESSFULLY RECOGNIZED"
            )

        else:

            print(
                "\n✗ NEW DRIVER WAS NOT RECOGNIZED"
            )

        print("=" * 60)

        print(
            "\nThe dashboard will remain open."
        )

        plt.ioff()
        plt.show()

        return

    # --------------------------------------------------------
    # Profile was NOT created.
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("NEW DRIVER WAS NOT CREATED")
    print("=" * 60)

    print(
        "\nThe three observations were not "
        "consistent enough."
    )

    print(
        "More evidence is required."
    )

    print(
        f"\nCurrent learning queue: "
        f"{len(get_unknown_trips())}/3 observations"
    )

    print(
        "\nThe dashboard will remain open so "
        "the three learning trips can be inspected."
    )

    try:

        dashboard.header_text.set_text(
            "DRIVER DIGITAL TWIN\n\n"
            "Profile: UNKNOWN\n"
            "Confidence: 0%\n\n"
            "NEW DRIVER LEARNING\n"
            "Progress: 3/3 trips\n"
            "Status: INCONSISTENT BEHAVIOUR\n\n"
            "More evidence required."
        )

        dashboard.footer.set_text(
            "Learning incomplete    |    "
            "MORE EVIDENCE REQUIRED"
        )

        dashboard.fig.canvas.draw()
        dashboard.fig.canvas.flush_events()

    except AttributeError:
        pass

    plt.ioff()
    plt.show()


# ============================================================
# RANDOM DRIVER
# ============================================================

def run_random_demo():

    available_profiles = [
        "calm",
        "normal",
        "aggressive"
    ]

    dynamic_profiles = load_profiles()

    available_profiles.extend(
        profile["driver_id"]
        for profile in dynamic_profiles
    )

    driver_style = random.choice(
        available_profiles
    )

    print(
        f"\nRandomly selected behaviour: "
        f"{driver_style.upper()}"
    )

    run_demo(
        driver_style
    )


# ============================================================
# MENU
# ============================================================

def show_menu():

    dynamic_profiles = load_profiles()

    print("\n")
    print("=" * 60)
    print("DRIVER DIGITAL TWIN — DEMO MENU")
    print("=" * 60)

    print(
        "\n1. Calm Driver"
    )

    print(
        "2. Normal Driver"
    )

    print(
        "3. Aggressive Driver"
    )

    menu_number = 4

    for profile in dynamic_profiles:

        print(
            f"{menu_number}. "
            f"{profile['driver_id'].upper()}"
        )

        menu_number += 1

    new_driver_option = menu_number

    print(
        f"{new_driver_option}. New Driver"
    )

    menu_number += 1

    random_option = menu_number

    print(
        f"{random_option}. Random"
    )

    print(
        "0. Exit"
    )

    print("=" * 60)

    return (
        dynamic_profiles,
        new_driver_option,
        random_option
    )


# ============================================================
# MENU LOOP
# ============================================================

if __name__ == "__main__":

    while True:

        (
            dynamic_profiles,
            new_driver_option,
            random_option
        ) = show_menu()

        choice = input(
            "\nEnter choice: "
        ).strip()

        if choice == "0":

            print(
                "\nExiting Digital Twin demo."
            )

            break

        elif choice == "1":

            run_demo(
                "calm"
            )

        elif choice == "2":

            run_demo(
                "normal"
            )

        elif choice == "3":

            run_demo(
                "aggressive"
            )

        else:

            try:

                numeric_choice = int(
                    choice
                )

            except ValueError:

                print(
                    "\nInvalid choice."
                )

                continue

            # ------------------------------------------------
            # Dynamic profile options
            # ------------------------------------------------

            dynamic_start = 4

            dynamic_end = (
                4
                + len(dynamic_profiles)
            )

            if (
                dynamic_start
                <= numeric_choice
                < dynamic_end
            ):

                profile_index = (
                    numeric_choice
                    - dynamic_start
                )

                driver_id = (
                    dynamic_profiles[
                        profile_index
                    ]["driver_id"]
                )

                run_demo(
                    driver_id
                )

            elif (
                numeric_choice
                == new_driver_option
            ):

                run_new_driver_demo()

            elif (
                numeric_choice
                == random_option
            ):

                run_random_demo()

            else:

                print(
                    "\nInvalid choice."
                )