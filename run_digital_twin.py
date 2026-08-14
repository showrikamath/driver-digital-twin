from simulation.simulator import run_simulation
from driver_profiles.driver_identifier import identify_driver
from digital_twin.digital_twin import DigitalTwin
from visualization.visualization import LiveDashboard
import matplotlib.pyplot as plt

# ============================================================
# FINAL DIGITAL TWIN DEMO
# ============================================================

def run_demo(driver_style):

    print("\n")
    print("=" * 60)
    print("DRIVER DIGITAL TWIN — INTEGRATED DEMO")
    print("=" * 60)

    # --------------------------------------------------------
    # Create ONE Digital Twin
    # --------------------------------------------------------

    twin = DigitalTwin()
    dashboard = LiveDashboard()
    # --------------------------------------------------------
    # Run vehicle simulation
    # --------------------------------------------------------

    print("\nStarting simulation...\n")

    result = run_simulation(
        driver_style,
        twin,
        telemetry_callback=dashboard.update
    )

    trip = result["trip"]

    telemetry = result["telemetry"]

    # --------------------------------------------------------
    # Identify driver
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Final Digital Twin
    # --------------------------------------------------------

    state = twin.get_state()

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

    # ========================================================
    # VISUALIZATION
    # ========================================================

    dashboard.finalize(
    state
    )

    # Keep final dashboard open
    import matplotlib.pyplot as plt

    plt.ioff()
    plt.show()

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    run_demo(
        "aggressive"
    )