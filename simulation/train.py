from simulator import run_simulation


TRAINING_RUNS = 5

driver_styles = [
    "calm",
    "normal",
    "aggressive"
]


for style in driver_styles:

    print("\n" + "=" * 60)
    print(f"TRAINING DRIVER: {style.upper()}")
    print("=" * 60)

    for run in range(1, TRAINING_RUNS + 1):

        print(
            f"\n--- {style.upper()} "
            f"TRIP {run}/{TRAINING_RUNS} ---"
        )

        run_simulation(style)