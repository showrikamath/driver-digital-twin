import json
from pathlib import Path


# ============================================================
# DATA FILES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PROFILE_FILE = BASE_DIR / "driver_profiles.json"
UNKNOWN_TRIPS_FILE = BASE_DIR / "unknown_trips.json"


# ============================================================
# RESET
# ============================================================

def reset_data():

    print("\n" + "=" * 60)
    print("RESETTING DRIVER DATA")
    print("=" * 60)

    # Clear dynamic driver profiles
    with open(PROFILE_FILE, "w") as file:
        json.dump([], file, indent=4)

    print("✓ Dynamic driver profiles cleared")

    # Clear unknown trips
    with open(UNKNOWN_TRIPS_FILE, "w") as file:
        json.dump([], file, indent=4)

    print("✓ Unknown trips cleared")

    print("=" * 60)
    print("RESET COMPLETE")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    reset_data()