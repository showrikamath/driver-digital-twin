class DigitalTwin:

    def __init__(self):
        # Vehicle state
        self.speed = 0.0
        self.desired_speed = 0.0
        self.target_speed = 0.0
        self.acceleration = 0.0
        self.braking = 0.0
        self.action = "IDLE"

        # Driver state
        self.driver_profile = "UNKNOWN"
        self.identification_distance = None
        self.confidence = 0.0

        # Trip state
        self.elapsed_time = 0

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

    def update_driver_state(
        self,
        driver_profile,
        identification_distance=None,
        confidence=0.0
    ):
        self.driver_profile = driver_profile
        self.identification_distance = identification_distance
        self.confidence = confidence

    def get_state(self):
        return {
            "speed": self.speed,
            "desired_speed": self.desired_speed,
            "target_speed": self.target_speed,
            "acceleration": self.acceleration,
            "braking": self.braking,
            "action": self.action,
            "driver_profile": self.driver_profile,
            "identification_distance": self.identification_distance,
            "confidence": self.confidence,
            "elapsed_time": self.elapsed_time
        }