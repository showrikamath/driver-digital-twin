import random
import time

from trip_data import save_trip


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
# HELPER FUNCTIONS
# ============================================================

def generate_target_speed(driver):
    """Generate a desired speed within the driver's normal range."""

    minimum, maximum = driver["target_speed"]

    return random.uniform(minimum, maximum)


def update_target_speed(current_target, desired_target):
    """
    Gradually move the current target toward the desired target.
    """

    difference = desired_target - current_target

    adjustment = difference * TARGET_ADJUSTMENT_RATE

    return current_target + adjustment


def choose_action(current_speed, target_speed):
    """Decide whether the driver accelerates, cruises or brakes."""

    speed_difference = target_speed - current_speed

    if speed_difference > 5:
        return "ACCELERATE"

    elif speed_difference < -5:
        return "BRAKE"

    else:
        return "CRUISE"


def generate_acceleration(driver, action):
    """Generate acceleration based on driver behaviour."""

    if action == "ACCELERATE":

        minimum, maximum = driver["acceleration"]

        return random.uniform(minimum, maximum)

    elif action == "BRAKE":

        minimum, maximum = driver["braking"]

        return random.uniform(minimum, maximum)

    else:

        # Small natural variation while cruising.
        return random.uniform(-0.1, 0.1)


def update_speed(current_speed, acceleration):
    """
    Physics:

        v_new = v_old + a × Δt

    Acceleration = m/s²
    Speed = km/h

    1 m/s = 3.6 km/h
    """

    speed_change = acceleration * 3.6 * TIME_STEP

    new_speed = current_speed + speed_change

    return max(MIN_SPEED, min(new_speed, MAX_SPEED))


def should_trigger_sudden_brake(
    driver,
    simulation_time,
    cooldown
):
    """
    Decide whether a sudden braking event should occur.
    """

    # Never start a trip with hard braking.
    if simulation_time == 0:
        return False

    # Don't allow another hard brake during cooldown.
    if cooldown > 0:
        return False

    # Only check at specific intervals.
    if simulation_time % BRAKE_EVENT_CHECK_INTERVAL != 0:
        return False

    probability = driver["hard_brake_probability"]

    return random.random() < probability


def generate_hard_braking():
    """Generate strong negative acceleration."""

    return random.uniform(-4.0, -3.0)


# ============================================================
# MAIN SIMULATION FUNCTION
# ============================================================

def run_simulation(driver_style):

    # --------------------------------------------------------
    # Select driver profile
    # --------------------------------------------------------

    driver = DRIVER_PROFILES[driver_style]


    # --------------------------------------------------------
    # Initial vehicle state
    # --------------------------------------------------------

    current_speed = 40.0

    simulation_time = 0

    desired_target_speed = generate_target_speed(driver)

    current_target_speed = desired_target_speed

    brake_cooldown = 0


    # --------------------------------------------------------
    # Lists for collecting trip data
    # --------------------------------------------------------

    speed_history = []

    acceleration_history = []

    braking_history = []

    action_history = []


    # ========================================================
    # SIMULATION LOOP
    # ========================================================

    while simulation_time < SIMULATION_DURATION:

        # ----------------------------------------------------
        # Occasionally choose a new desired speed
        # ----------------------------------------------------

        if (
            simulation_time > 0
            and simulation_time % DESIRED_SPEED_CHANGE_INTERVAL == 0
        ):

            desired_target_speed = generate_target_speed(driver)

            print(
                f"\n>>> Driver wants a new speed: "
                f"{desired_target_speed:.2f} km/h"
            )


        # ----------------------------------------------------
        # Gradually move target toward desired speed
        # ----------------------------------------------------

        current_target_speed = update_target_speed(
            current_target_speed,
            desired_target_speed
        )


        # ----------------------------------------------------
        # Check for sudden braking event
        # ----------------------------------------------------

        sudden_brake = should_trigger_sudden_brake(
            driver,
            simulation_time,
            brake_cooldown
        )


        # ----------------------------------------------------
        # Determine action and acceleration
        # ----------------------------------------------------

        if sudden_brake:

            action = "HARD BRAKE"

            acceleration = generate_hard_braking()

            brake_cooldown = BRAKE_COOLDOWN

        else:

            action = choose_action(
                current_speed,
                current_target_speed
            )

            acceleration = generate_acceleration(
                driver,
                action
            )


        # ----------------------------------------------------
        # Determine braking value
        # ----------------------------------------------------

        if action in ("BRAKE", "HARD BRAKE"):

            braking = acceleration

        else:

            braking = 0.0


        # ----------------------------------------------------
        # Update vehicle speed
        # ----------------------------------------------------

        current_speed = update_speed(
            current_speed,
            acceleration
        )


        # ----------------------------------------------------
        # Store telemetry
        # ----------------------------------------------------

        speed_history.append(current_speed)

        acceleration_history.append(acceleration)

        braking_history.append(braking)

        action_history.append(action)


        # ----------------------------------------------------
        # Print telemetry
        # ----------------------------------------------------

        print(
            f"Time: {simulation_time:02.0f}s | "
            f"Action: {action:10} | "
            f"Desired: {desired_target_speed:6.2f} | "
            f"Target: {current_target_speed:6.2f} | "
            f"Speed: {current_speed:6.2f} km/h | "
            f"Acceleration: {acceleration:6.2f} m/s² | "
            f"Braking: {braking:6.2f} m/s²"
        )


        # ----------------------------------------------------
        # Update timers
        # ----------------------------------------------------

        simulation_time += TIME_STEP

        if brake_cooldown > 0:

            brake_cooldown -= TIME_STEP


        # ----------------------------------------------------
        # Wait for next simulation tick
        # ----------------------------------------------------
        if not FAST_MODE:
            time.sleep(TIME_STEP)


    # ========================================================
    # CALCULATE TRIP METRICS
    # ========================================================

    average_speed = (
        sum(speed_history)
        / len(speed_history)
    )


    average_acceleration = (
        sum(acceleration_history)
        / len(acceleration_history)
    )


    hard_braking_events = action_history.count(
        "HARD BRAKE"
    )


    hard_braking_rate = (
        hard_braking_events
        / len(action_history)
    ) * 100


    # ========================================================
    # CREATE TRIP RECORD
    # ========================================================

    trip = {
        "driver_style": driver_style,

        "average_speed": round(
            average_speed,
            2
        ),

        "average_acceleration": round(
            average_acceleration,
            2
        ),

        "hard_braking_events": hard_braking_events,

        "hard_braking_rate": round(
            hard_braking_rate,
            2
        )
    }


    # ========================================================
    # SAVE TRIP
    # ========================================================

    save_trip(trip)


    # ========================================================
    # DISPLAY TRIP SUMMARY
    # ========================================================

    print("\n" + "=" * 50)

    print("TRIP SUMMARY")

    print("=" * 50)

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

    print("=" * 50)


    # Return the trip so another program
    # can use its metrics.
    return trip


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    DRIVER_STYLE = "aggressive"

    run_simulation(DRIVER_STYLE)