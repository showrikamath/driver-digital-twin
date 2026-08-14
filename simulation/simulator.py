import random
import time

from simulation.trip_data import save_trip
from digital_twin.digital_twin import DigitalTwin


# ============================================================
# DRIVER BEHAVIOUR CONFIGURATION
# ============================================================

DRIVER_PROFILES = {
    "calm": {
        "target_speed": (40, 55),
        "acceleration": (0.5, 1.5),
        "braking": (-1.5, -0.5),
        "hard_brake_probability": 0.03,
    },

    "normal": {
        "target_speed": (50, 70),
        "acceleration": (1.0, 2.2),
        "braking": (-2.2, -0.8),
        "hard_brake_probability": 0.08,
    },

    "aggressive": {
        "target_speed": (65, 90),
        "acceleration": (1.8, 3.2),
        "braking": (-3.8, -1.5),
        "hard_brake_probability": 0.15,
    },
}


# ============================================================
# SIMULATION SETTINGS
# ============================================================

TIME_STEP = 1.0
SIMULATION_DURATION = 30

MIN_SPEED = 0
MAX_SPEED = 100

DESIRED_SPEED_CHANGE_INTERVAL = 10
TARGET_ADJUSTMENT_RATE = 0.20

BRAKE_EVENT_CHECK_INTERVAL = 5
BRAKE_COOLDOWN = 7

FAST_MODE = True


# ============================================================
# DYNAMIC PROFILE SUPPORT
# ============================================================

def load_dynamic_profiles():

    try:
        from driver_profiles.dynamic_profile import load_profiles

        return load_profiles()

    except (ImportError, ModuleNotFoundError):

        return []


def get_dynamic_profile(driver_id):

    profiles = load_dynamic_profiles()

    for profile in profiles:

        if profile.get("driver_id") == driver_id:
            return profile

    return None


def dynamic_profile_to_simulation_profile(profile):
    """
    Convert a learned driver profile into parameters
    that the simulator can use.

    Learned profile contains:

        average_speed
        average_acceleration
        hard_braking_rate

    Simulator needs:

        target_speed range
        acceleration range
        braking range
        hard-brake probability
    """

    average_speed = float(
        profile.get(
            "average_speed",
            60
        )
    )

    average_acceleration = float(
        profile.get(
            "average_acceleration",
            1.0
        )
    )

    hard_braking_rate = float(
        profile.get(
            "hard_braking_rate",
            5.0
        )
    )

    # --------------------------------------------------------
    # Target speed
    # --------------------------------------------------------

    speed_min = max(
        20,
        average_speed - 5
    )

    speed_max = min(
        95,
        average_speed + 5
    )

    # --------------------------------------------------------
    # Acceleration
    # --------------------------------------------------------

    acceleration_min = max(
        0.2,
        average_acceleration - 0.35
    )

    acceleration_max = max(
        acceleration_min + 0.1,
        average_acceleration + 0.35
    )

    acceleration_max = min(
        acceleration_max,
        3.5
    )

    # --------------------------------------------------------
    # Braking
    #
    # Learned profiles currently store hard-braking rate,
    # not exact braking force. Use a realistic range.
    # --------------------------------------------------------

    braking_strength = min(
        3.5,
        max(
            1.0,
            abs(average_acceleration) + 1.5
        )
    )

    braking = (
        -braking_strength,
        -0.8
    )

    # --------------------------------------------------------
    # Convert trip-level percentage into probability
    #
    # The simulator checks for a hard brake roughly once
    # every 5 seconds, giving about 6 opportunities in a
    # 30-second trip.
    # --------------------------------------------------------

    hard_brake_probability = (
        hard_braking_rate
        / 100
        * 6
    )

    hard_brake_probability = min(
        0.75,
        max(
            0.01,
            hard_brake_probability
        )
    )

    return {
        "target_speed": (
            speed_min,
            speed_max
        ),

        "acceleration": (
            acceleration_min,
            acceleration_max
        ),

        "braking": braking,

        "hard_brake_probability":
            hard_brake_probability
    }


def get_simulation_profile(driver_style):

    # --------------------------------------------------------
    # Predefined driver
    # --------------------------------------------------------

    if driver_style in DRIVER_PROFILES:

        return DRIVER_PROFILES[
            driver_style
        ]

    # --------------------------------------------------------
    # Dynamically learned driver
    # --------------------------------------------------------

    dynamic_profile = get_dynamic_profile(
        driver_style
    )

    if dynamic_profile is not None:

        return dynamic_profile_to_simulation_profile(
            dynamic_profile
        )

    raise ValueError(
        f"Unknown driver profile: {driver_style}"
    )


# ============================================================
# NEW DRIVER PROFILE
# ============================================================

def get_new_driver_profile():

    """
    Behaviour used specifically for the
    'New Driver' learning demonstration.

    It is intentionally different from the
    predefined Calm / Normal / Aggressive profiles.
    """

    return {
        "target_speed": (58, 64),

        "acceleration": (
            0.35,
            0.75
        ),

        "braking": (
            -2.8,
            -1.6
        ),

        "hard_brake_probability":
            0.35
    }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_target_speed(driver):

    minimum, maximum = driver[
        "target_speed"
    ]

    return random.uniform(
        minimum,
        maximum
    )


def update_target_speed(
    current_target,
    desired_target
):

    difference = (
        desired_target
        - current_target
    )

    adjustment = (
        difference
        * TARGET_ADJUSTMENT_RATE
    )

    return (
        current_target
        + adjustment
    )


def choose_action(
    current_speed,
    target_speed
):

    speed_difference = (
        target_speed
        - current_speed
    )

    if speed_difference > 5:

        return "ACCELERATE"

    elif speed_difference < -5:

        return "BRAKE"

    else:

        return "CRUISE"


def generate_acceleration(
    driver,
    action
):

    if action == "ACCELERATE":

        minimum, maximum = driver[
            "acceleration"
        ]

        return random.uniform(
            minimum,
            maximum
        )

    elif action == "BRAKE":

        minimum, maximum = driver[
            "braking"
        ]

        return random.uniform(
            minimum,
            maximum
        )

    else:

        return random.uniform(
            -0.1,
            0.1
        )


def update_speed(
    current_speed,
    acceleration
):

    speed_change = (
        acceleration
        * 3.6
        * TIME_STEP
    )

    new_speed = (
        current_speed
        + speed_change
    )

    return max(
        MIN_SPEED,
        min(
            new_speed,
            MAX_SPEED
        )
    )


def should_trigger_sudden_brake(
    driver,
    simulation_time,
    cooldown
):

    if simulation_time == 0:

        return False

    if cooldown > 0:

        return False

    if (
        simulation_time
        % BRAKE_EVENT_CHECK_INTERVAL
        != 0
    ):

        return False

    probability = driver[
        "hard_brake_probability"
    ]

    return (
        random.random()
        < probability
    )


def generate_hard_braking():

    return random.uniform(
        -4.0,
        -3.0
    )


# ============================================================
# MAIN SIMULATION FUNCTION
# ============================================================

def run_simulation(
    driver_style,
    twin=None,
    telemetry_callback=None
):

    # --------------------------------------------------------
    # Select driver profile
    # --------------------------------------------------------

    if driver_style == "new_driver":

        driver = get_new_driver_profile()

    else:

        driver = get_simulation_profile(
            driver_style
        )

    if twin is None:

        twin = DigitalTwin()

    # --------------------------------------------------------
    # Initial vehicle state
    # --------------------------------------------------------

    current_speed = 40.0

    simulation_time = 0

    desired_target_speed = (
        generate_target_speed(
            driver
        )
    )

    current_target_speed = (
        desired_target_speed
    )

    brake_cooldown = 0

    # --------------------------------------------------------
    # Telemetry storage
    # --------------------------------------------------------

    speed_history = []
    target_speed_history = []
    desired_speed_history = []
    acceleration_history = []
    braking_history = []
    action_history = []
    time_history = []

    # ========================================================
    # SIMULATION LOOP
    # ========================================================

    while (
        simulation_time
        < SIMULATION_DURATION
    ):

        # ----------------------------------------------------
        # Occasionally choose a new desired speed
        # ----------------------------------------------------

        if (
            simulation_time > 0
            and
            simulation_time
            % DESIRED_SPEED_CHANGE_INTERVAL
            == 0
        ):

            desired_target_speed = (
                generate_target_speed(
                    driver
                )
            )

            print(
                f"\n>>> Driver wants a new speed: "
                f"{desired_target_speed:.2f} km/h"
            )

        # ----------------------------------------------------
        # Gradually move target toward desired speed
        # ----------------------------------------------------

        current_target_speed = (
            update_target_speed(
                current_target_speed,
                desired_target_speed
            )
        )

        # ----------------------------------------------------
        # Check for sudden braking
        # ----------------------------------------------------

        sudden_brake = (
            should_trigger_sudden_brake(
                driver,
                simulation_time,
                brake_cooldown
            )
        )

        # ----------------------------------------------------
        # Determine action
        # ----------------------------------------------------

        if sudden_brake:

            action = "HARD BRAKE"

            acceleration = (
                generate_hard_braking()
            )

            brake_cooldown = (
                BRAKE_COOLDOWN
            )

        else:

            action = choose_action(
                current_speed,
                current_target_speed
            )

            acceleration = (
                generate_acceleration(
                    driver,
                    action
                )
            )

        # ----------------------------------------------------
        # Determine braking value
        # ----------------------------------------------------

        if action in (
            "BRAKE",
            "HARD BRAKE"
        ):

            braking = acceleration

        else:

            braking = 0.0

        # ----------------------------------------------------
        # Update speed
        # ----------------------------------------------------

        current_speed = (
            update_speed(
                current_speed,
                acceleration
            )
        )

        # ----------------------------------------------------
        # Update Digital Twin
        # ----------------------------------------------------

        twin.update_vehicle_state(

            speed=current_speed,

            desired_speed=
                desired_target_speed,

            target_speed=
                current_target_speed,

            acceleration=
                acceleration,

            braking=
                braking,

            action=
                action,

            elapsed_time=
                simulation_time
        )

        # ====================================================
        # DIGITAL TWIN FEEDBACK
        # ====================================================

        feedback = (
            twin.evaluate_behaviour()
        )

        print(
            f"TWIN FEEDBACK | "
            f"Risk: "
            f"{feedback['risk_level']} | "
            f"Status: "
            f"{feedback['behaviour_status']} | "
            f"Action: "
            f"{feedback['feedback_action']} | "
            f"Recommended Target: "
            f"{feedback['recommended_target_speed']:.2f}"
        )

        # ----------------------------------------------------
        # Dashboard callback
        # ----------------------------------------------------

        if telemetry_callback is not None:

            telemetry_callback(
                twin.get_state()
            )

        # ----------------------------------------------------
        # Store telemetry
        # ----------------------------------------------------

        time_history.append(
            simulation_time
        )

        speed_history.append(
            current_speed
        )

        target_speed_history.append(
            current_target_speed
        )

        desired_speed_history.append(
            desired_target_speed
        )

        acceleration_history.append(
            acceleration
        )

        braking_history.append(
            braking
        )

        action_history.append(
            action
        )

        # ----------------------------------------------------
        # Console telemetry
        # ----------------------------------------------------

        print(
            f"Time: "
            f"{simulation_time:02.0f}s | "
            f"Action: "
            f"{action:10} | "
            f"Desired: "
            f"{desired_target_speed:6.2f} | "
            f"Target: "
            f"{current_target_speed:6.2f} | "
            f"Speed: "
            f"{current_speed:6.2f} km/h | "
            f"Acceleration: "
            f"{acceleration:6.2f} m/s² | "
            f"Braking: "
            f"{braking:6.2f} m/s²"
        )

        # ----------------------------------------------------
        # Timers
        # ----------------------------------------------------

        simulation_time += TIME_STEP

        if brake_cooldown > 0:

            brake_cooldown -= TIME_STEP

        # ----------------------------------------------------
        # Real-time mode
        # ----------------------------------------------------

        if not FAST_MODE:

            time.sleep(
                TIME_STEP
            )

    # ========================================================
    # TRIP METRICS
    # ========================================================

    average_speed = (
        sum(speed_history)
        / len(speed_history)
    )

    average_acceleration = (
        sum(acceleration_history)
        / len(acceleration_history)
    )

    hard_braking_events = (
        action_history.count(
            "HARD BRAKE"
        )
    )

    hard_braking_rate = (
        hard_braking_events
        / len(action_history)
    ) * 100

    # ========================================================
    # CREATE TRIP RECORD
    # ========================================================

    trip = {

        "driver_style":
            driver_style,

        "average_speed":
            round(
                average_speed,
                2
            ),

        "average_acceleration":
            round(
                average_acceleration,
                2
            ),

        "hard_braking_events":
            hard_braking_events,

        "hard_braking_rate":
            round(
                hard_braking_rate,
                2
            )
    }

    # ========================================================
    # SAVE TRIP
    # ========================================================

    save_trip(
        trip
    )

    # ========================================================
    # DISPLAY TRIP SUMMARY
    # ========================================================

    print(
        "\n"
        + "=" * 50
    )

    print(
        "TRIP SUMMARY"
    )

    print(
        "=" * 50
    )

    print(
        f"Driver style: "
        f"{driver_style}"
    )

    print(
        f"Average speed: "
        f"{average_speed:.2f} km/h"
    )

    print(
        f"Average acceleration: "
        f"{average_acceleration:.2f} m/s²"
    )

    print(
        f"Hard braking events: "
        f"{hard_braking_events}"
    )

    print(
        f"Hard braking rate: "
        f"{hard_braking_rate:.2f}%"
    )

    print(
        "=" * 50
    )

    return {

        "trip":
            trip,

        "telemetry": {

            "time":
                time_history,

            "speed":
                speed_history,

            "target_speed":
                target_speed_history,

            "desired_speed":
                desired_speed_history,

            "acceleration":
                acceleration_history,

            "braking":
                braking_history,

            "action":
                action_history
        }
    }


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    DRIVER_STYLE = "aggressive"

    run_simulation(
        DRIVER_STYLE
    )