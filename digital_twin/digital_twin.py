class DigitalTwin:

    def __init__(self):

        # ========================================================
        # VEHICLE STATE
        # ========================================================

        self.speed = 0.0
        self.desired_speed = 0.0
        self.target_speed = 0.0
        self.acceleration = 0.0
        self.braking = 0.0
        self.action = "IDLE"

        # ========================================================
        # DRIVER STATE
        # ========================================================

        self.driver_profile = "UNKNOWN"
        self.identification_distance = None
        self.confidence = 0.0

        # ========================================================
        # TWIN ANALYSIS
        # ========================================================

        self.risk_level = "LOW"

        self.behaviour_status = "NORMAL"

        # Feedback sent back to simulator

        self.recommended_target_speed = None

        self.max_acceleration = None

        self.feedback_action = "NONE"

        # ========================================================
        # TRIP STATE
        # ========================================================

        self.elapsed_time = 0


    # ============================================================
    # RECEIVE VEHICLE TELEMETRY
    # ============================================================

    def update_vehicle_state(
        self,
        speed,
        desired_speed,
        target_speed,
        acceleration,
        braking,
        action,
        elapsed_time
    ):

        self.speed = speed

        self.desired_speed = desired_speed

        self.target_speed = target_speed

        self.acceleration = acceleration

        self.braking = braking

        self.action = action

        self.elapsed_time = elapsed_time


    # ============================================================
    # DRIVER IDENTIFICATION
    # ============================================================

    def update_driver_state(
        self,
        driver_profile,
        identification_distance=None,
        confidence=0.0
    ):

        self.driver_profile = driver_profile

        self.identification_distance = (
            identification_distance
        )

        self.confidence = confidence


    # ============================================================
    # TWIN BEHAVIOUR ANALYSIS
    # ============================================================

    def evaluate_behaviour(self):

        speed_difference = (
            self.speed
            - self.target_speed
        )

        absolute_acceleration = abs(
            self.acceleration
        )


        # --------------------------------------------------------
        # HIGH RISK
        # --------------------------------------------------------

        if (

            self.action == "HARD BRAKE"

            or

            absolute_acceleration >= 3.0

            or

            speed_difference >= 10.0

        ):

            self.risk_level = "HIGH"

            self.behaviour_status = (
                "AGGRESSIVE BEHAVIOUR"
            )

            self.recommended_target_speed = max(
                self.target_speed - 8.0,
                40.0
            )

            self.max_acceleration = 1.5

            self.feedback_action = (
                "REDUCE SPEED"
            )


        # --------------------------------------------------------
        # MODERATE RISK
        # --------------------------------------------------------

        elif (

            absolute_acceleration >= 2.0

            or

            speed_difference >= 5.0

        ):

            self.risk_level = "MEDIUM"

            self.behaviour_status = (
                "ELEVATED BEHAVIOUR"
            )

            self.recommended_target_speed = max(
                self.target_speed - 3.0,
                40.0
            )

            self.max_acceleration = 2.0

            self.feedback_action = (
                "MODERATE ACCELERATION"
            )


        # --------------------------------------------------------
        # NORMAL
        # --------------------------------------------------------

        else:

            self.risk_level = "LOW"

            self.behaviour_status = (
                "NORMAL BEHAVIOUR"
            )

            self.recommended_target_speed = (
                self.target_speed
            )

            self.max_acceleration = 3.0

            self.feedback_action = (
                "MAINTAIN"
            )


        return self.get_feedback()


    # ============================================================
    # FEEDBACK FOR SIMULATOR
    # ============================================================

    def get_feedback(self):

        return {

            "risk_level":
                self.risk_level,

            "behaviour_status":
                self.behaviour_status,

            "recommended_target_speed":
                self.recommended_target_speed,

            "max_acceleration":
                self.max_acceleration,

            "feedback_action":
                self.feedback_action
        }


    # ============================================================
    # COMPLETE TWIN STATE
    # ============================================================

    def get_state(self):

        return {

            # Vehicle state

            "speed":
                self.speed,

            "desired_speed":
                self.desired_speed,

            "target_speed":
                self.target_speed,

            "acceleration":
                self.acceleration,

            "braking":
                self.braking,

            "action":
                self.action,


            # Driver state

            "driver_profile":
                self.driver_profile,

            "identification_distance":
                self.identification_distance,

            "confidence":
                self.confidence,


            # Twin intelligence

            "risk_level":
                self.risk_level,

            "behaviour_status":
                self.behaviour_status,

            "recommended_target_speed":
                self.recommended_target_speed,

            "max_acceleration":
                self.max_acceleration,

            "feedback_action":
                self.feedback_action,


            # Trip state

            "elapsed_time":
                self.elapsed_time
        }