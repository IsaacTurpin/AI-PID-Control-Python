import time

class PIDController:
    def __init__(self):
        self.Kp = 0.85  # Proportional gain
        self.Ki = 0.9  # Integral gain
        self.Kd = 0.03   # Derivative gain
        self.setpoint = 0.0
        self.previous_error = 0.0
        self.previous_measured = 0.0
        self.integral = 0.0
        self.output_min = 0.0
        self.output_max = 5.0
        self.last_time = time.time()

    def set_setpoint(self, setpoint: float):
        """Set the desired voltage (setpoint) and reset PID terms."""
        self.setpoint = setpoint
        self.previous_error = 0.0
        self.previous_measured = 0.0
        self.integral = 0.0
        self.last_time = time.time()

    def compute(self, measured_value: float) -> float:
        """Compute the PID output based on the measured value."""
        current_time = time.time()
        dt = current_time - self.last_time
        if dt <= 0:  # Prevent division by zero
            dt = 1e-3  # Smallest reasonable time step

        error = self.setpoint - measured_value

        # Proportional term
        proportional = self.Kp * error

        # Integral term with proper anti-windup
        self.integral += error * dt
        integral = self.Ki * self.integral
        integral = max(-1.0, min(integral, 1.0))  # Limit integral contribution

        # Derivative term (on measured value)
        derivative = -self.Kd * (measured_value - self.previous_measured) / dt

        # Compute final PID output
        output = proportional + integral + derivative

        # Clamp output to valid range
        output = max(self.output_min, min(output, self.output_max))

        # Store previous values
        self.previous_error = error
        self.previous_measured = measured_value
        self.last_time = current_time

        return output
