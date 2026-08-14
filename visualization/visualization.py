import matplotlib.pyplot as plt


class LiveDashboard:

    def __init__(self):

        self.fig = plt.figure(
            figsize=(10, 5)
        )

        grid = self.fig.add_gridspec(
            4,
            1,
            height_ratios=[
                0.7,
                2.2,
                2.2,
                2.2
            ],
            hspace=0.55
        )

        # ====================================================
        # HEADER
        # ====================================================

        self.header = self.fig.add_subplot(
            grid[0]
        )

        self.header.axis("off")

        self.header_text = self.header.text(
            0.5,
            0.5,
            "DRIVER DIGITAL TWIN\n\n"
            "Profile: IDENTIFYING...    "
            "Confidence: --    "
            "Action: IDLE",
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold"
        )

        # ====================================================
        # SPEED GRAPH
        # ====================================================

        self.ax_speed = self.fig.add_subplot(
            grid[1]
        )

        self.speed_line, = self.ax_speed.plot(
            [],
            [],
            label="Actual Speed"
        )

        self.target_line, = self.ax_speed.plot(
            [],
            [],
            label="Target Speed",
            linestyle="--"
        )

        self.desired_line, = self.ax_speed.plot(
            [],
            [],
            label="Desired Speed",
            linestyle=":"
        )

        self.ax_speed.set_title(
            "Vehicle Speed"
        )

        self.ax_speed.set_ylabel(
            "Speed (km/h)"
        )

        self.ax_speed.legend()

        self.ax_speed.grid(True)

        # ====================================================
        # ACCELERATION / BRAKING
        # ====================================================

        self.ax_accel = self.fig.add_subplot(
            grid[2]
        )

        self.accel_line, = self.ax_accel.plot(
            [],
            [],
            label="Acceleration"
        )

        self.brake_line, = self.ax_accel.plot(
            [],
            [],
            label="Braking",
            linestyle="--"
        )

        self.ax_accel.axhline(
            0,
            linewidth=1
        )

        self.ax_accel.set_title(
            "Acceleration & Braking"
        )

        self.ax_accel.set_ylabel(
            "m/s²"
        )

        self.ax_accel.legend()

        self.ax_accel.grid(True)

        # ====================================================
        # DRIVER ACTION
        # ====================================================

        self.ax_action = self.fig.add_subplot(
            grid[3]
        )

        self.action_line, = self.ax_action.step(
            [],
            [],
            where="post"
        )

        self.ax_action.set_yticks(
            [-2, -1, 0, 1]
        )

        self.ax_action.set_yticklabels(
            [
                "Hard Brake",
                "Brake",
                "Cruise",
                "Accelerate"
            ]
        )

        self.ax_action.set_title(
            "Driver Behaviour"
        )

        self.ax_action.set_ylabel(
            "Action"
        )

        self.ax_action.set_xlabel(
            "Time (s)"
        )

        self.ax_action.grid(True)

        # ====================================================
        # FOOTER
        # ====================================================

        self.footer = self.fig.text(
            0.5,
            0.015,
            "Waiting for simulation...",
            ha="center",
            va="bottom",
            fontsize=10
        )

        self.fig.subplots_adjust(
            top=0.96,
            bottom=0.07,
            left=0.08,
            right=0.97
        )

        plt.ion()

        self.fig.show()

        self.telemetry = {
            "time": [],
            "speed": [],
            "target_speed": [],
            "desired_speed": [],
            "acceleration": [],
            "braking": [],
            "action": []
        }


    # ========================================================
    # UPDATE DASHBOARD
    # ========================================================

    def update(
        self,
        twin_state
    ):

        # ----------------------------------------------------
        # Store current telemetry
        # ----------------------------------------------------

        self.telemetry["time"].append(
            twin_state["elapsed_time"]
        )

        self.telemetry["speed"].append(
            twin_state["speed"]
        )

        self.telemetry["target_speed"].append(
            twin_state["target_speed"]
        )

        self.telemetry["desired_speed"].append(
            twin_state["desired_speed"]
        )

        self.telemetry["acceleration"].append(
            twin_state["acceleration"]
        )

        self.telemetry["braking"].append(
            twin_state["braking"]
        )

        self.telemetry["action"].append(
            twin_state["action"]
        )

        # ----------------------------------------------------
        # Update speed graph
        # ----------------------------------------------------

        self.speed_line.set_data(
            self.telemetry["time"],
            self.telemetry["speed"]
        )

        self.target_line.set_data(
            self.telemetry["time"],
            self.telemetry["target_speed"]
        )

        self.desired_line.set_data(
            self.telemetry["time"],
            self.telemetry["desired_speed"]
        )

        # ----------------------------------------------------
        # Update acceleration graph
        # ----------------------------------------------------

        self.accel_line.set_data(
            self.telemetry["time"],
            self.telemetry["acceleration"]
        )

        self.brake_line.set_data(
            self.telemetry["time"],
            self.telemetry["braking"]
        )

        # ----------------------------------------------------
        # Update action graph
        # ----------------------------------------------------

        action_map = {
            "HARD BRAKE": -2,
            "BRAKE": -1,
            "CRUISE": 0,
            "ACCELERATE": 1
        }

        action_values = [
            action_map.get(
                action,
                0
            )
            for action in self.telemetry["action"]
        ]

        self.action_line.set_data(
            self.telemetry["time"],
            action_values
        )

        # ----------------------------------------------------
        # Automatically adjust axes
        # ----------------------------------------------------

        self.ax_speed.relim()
        self.ax_speed.autoscale_view()

        self.ax_accel.relim()
        self.ax_accel.autoscale_view()

        self.ax_action.relim()
        self.ax_action.autoscale_view()

        # ----------------------------------------------------
        # Update header
        # ----------------------------------------------------

        self.header_text.set_text(
            "DRIVER DIGITAL TWIN\n\n"
            f"Profile: {twin_state['driver_profile'].upper()}    "
            f"Confidence: {twin_state['confidence']:.0%}    "
            f"Action: {twin_state['action']}    "
            f"Speed: {twin_state['speed']:.2f} km/h"
        )

        # ----------------------------------------------------
        # Update footer
        # ----------------------------------------------------

        distance = twin_state[
            "identification_distance"
        ]

        distance_text = (
            f"{distance:.3f}"
            if distance is not None
            else "N/A"
        )

        self.footer.set_text(
            f"Target: {twin_state['target_speed']:.2f} km/h    |    "
            f"Acceleration: {twin_state['acceleration']:.2f} m/s²    |    "
            f"Braking: {twin_state['braking']:.2f} m/s²    |    "
            f"Distance: {distance_text}    |    "
            f"Elapsed: {twin_state['elapsed_time']:.0f}s"
        )

        # ----------------------------------------------------
        # Refresh window
        # ----------------------------------------------------

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        plt.pause(0.001)


    # ========================================================
    # FINAL UPDATE
    # ========================================================

    def finalize(
        self,
        final_state
    ):

        self.header_text.set_text(
            "DRIVER DIGITAL TWIN\n\n"
            f"Profile: "
            f"{final_state['driver_profile'].upper()}    "
            f"Confidence: "
            f"{final_state['confidence']:.0%}    "
            f"Action: "
            f"{final_state['action']}    "
            f"Speed: "
            f"{final_state['speed']:.2f} km/h"
        )

        distance = final_state[
            "identification_distance"
        ]

        distance_text = (
            f"{distance:.3f}"
            if distance is not None
            else "N/A"
        )

        self.footer.set_text(
            f"Target: {final_state['target_speed']:.2f} km/h    |    "
            f"Acceleration: {final_state['acceleration']:.2f} m/s²    |    "
            f"Braking: {final_state['braking']:.2f} m/s²    |    "
            f"Distance: {distance_text}    |    "
            f"Elapsed: {final_state['elapsed_time']:.0f}s"
        )

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        plt.ioff()
        plt.close(self.fig)