import matplotlib.pyplot as plt


class LiveDashboard:

    def __init__(self):
        self.fig = plt.figure(
            figsize=(13, 11)
        )

        grid = self.fig.add_gridspec(
            4,
            1,
            height_ratios=[
                1.25,
                2.2,
                2.2,
                2.2
            ],
            hspace=0.45
        )

        # ====================================================
        # HEADER / DIGITAL TWIN FEEDBACK
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
            "Action: IDLE    "
            "Speed: -- km/h\n\n"
            "DIGITAL TWIN FEEDBACK\n"
            "Risk: --    "
            "Behaviour: --    "
            "Recommendation: --\n"
            "Recommended Target: -- km/h    "
            "Max Acceleration: -- m/s²",
            ha="center",
            va="center",
            fontsize=10.5,
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

        # Keep the latest Twin feedback so it remains visible
        # even if the final driver identification happens later.
        self.last_feedback = {
            "risk_level": "--",
            "behaviour_status": "--",
            "feedback_action": "--",
            "recommended_target_speed": None,
            "max_acceleration": None
        }

    # ========================================================
    # DIGITAL TWIN FEEDBACK
    # ========================================================

    def _update_feedback(self, twin_state):
        """
        Read feedback fields supplied by the simulator.

        The .get() calls keep the dashboard compatible with
        older Twin states until feedback is passed through.
        """

        if "risk_level" in twin_state:
            self.last_feedback["risk_level"] = twin_state[
                "risk_level"
            ]

        if "behaviour_status" in twin_state:
            self.last_feedback["behaviour_status"] = twin_state[
                "behaviour_status"
            ]

        if "feedback_action" in twin_state:
            self.last_feedback["feedback_action"] = twin_state[
                "feedback_action"
            ]

        if "recommended_target_speed" in twin_state:
            self.last_feedback[
                "recommended_target_speed"
            ] = twin_state[
                "recommended_target_speed"
            ]

        if "max_acceleration" in twin_state:
            self.last_feedback[
                "max_acceleration"
            ] = twin_state[
                "max_acceleration"
            ]

    def _feedback_text(self):
        feedback = self.last_feedback

        recommended_target = feedback[
            "recommended_target_speed"
        ]

        max_acceleration = feedback[
            "max_acceleration"
        ]

        target_text = (
            f"{recommended_target:.2f} km/h"
            if recommended_target is not None
            else "--"
        )

        acceleration_text = (
            f"{max_acceleration:.2f} m/s²"
            if max_acceleration is not None
            else "--"
        )

        return (
            "DIGITAL TWIN FEEDBACK\n"
            f"Risk: {feedback['risk_level']}    "
            f"Behaviour: {feedback['behaviour_status']}    "
            f"Recommendation: {feedback['feedback_action']}\n"
            f"Recommended Target: {target_text}    "
            f"Max Acceleration: {acceleration_text}"
        )

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
        # Update Twin feedback
        # ----------------------------------------------------

        self._update_feedback(
            twin_state
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
            f"Profile: "
            f"{twin_state['driver_profile'].upper()}    "
            f"Confidence: "
            f"{twin_state['confidence']:.0%}    "
            f"Action: {twin_state['action']}    "
            f"Speed: "
            f"{twin_state['speed']:.2f} km/h\n\n"
            f"{self._feedback_text()}"
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
            f"Target: "
            f"{twin_state['target_speed']:.2f} km/h    |    "
            f"Acceleration: "
            f"{twin_state['acceleration']:.2f} m/s²    |    "
            f"Braking: "
            f"{twin_state['braking']:.2f} m/s²    |    "
            f"Distance: {distance_text}    |    "
            f"Elapsed: "
            f"{twin_state['elapsed_time']:.0f}s"
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

        # Pick up any final feedback if supplied.
        self._update_feedback(
            final_state
        )

        self.header_text.set_text(
            "DRIVER DIGITAL TWIN\n\n"
            f"Profile: "
            f"{final_state['driver_profile'].upper()}    "
            f"Confidence: "
            f"{final_state['confidence']:.0%}    "
            f"Action: "
            f"{final_state['action']}    "
            f"Speed: "
            f"{final_state['speed']:.2f} km/h\n\n"
            f"{self._feedback_text()}"
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
            f"Target: "
            f"{final_state['target_speed']:.2f} km/h    |    "
            f"Acceleration: "
            f"{final_state['acceleration']:.2f} m/s²    |    "
            f"Braking: "
            f"{final_state['braking']:.2f} m/s²    |    "
            f"Distance: {distance_text}    |    "
            f"Elapsed: "
            f"{final_state['elapsed_time']:.0f}s"
        )

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):
        plt.ioff()
        plt.close(self.fig)