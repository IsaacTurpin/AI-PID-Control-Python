class PIDController:
    def __init__(self):
        self.Kp = 1.0  # Proportional gain
        self.Ki = 0.05  # Integral gain
        self.Kd = 0.2  # Derivative gain
        self.setpoint = 0.0  # Desired voltage
        self.previous_error = 0.0
        self.integral = 0.0
        self.output_min = 0.0  # Minimum output voltage
        self.output_max = 5.0  # Maximum output voltage

    def set_setpoint(self, setpoint: float):
        """Set the desired voltage (setpoint) and reset PID terms."""
        self.setpoint = setpoint
        self.previous_error = 0.0  # Reset previous error
        self.integral = 0.0  # Reset integral term

    def compute(self, measured_value: float) -> float:
        """Compute the PID output based on the measured value."""
        error = self.setpoint - measured_value

        # Debug: Print the error
        print(f"Error: {error:.3f}V")

        # Proportional term
        proportional = self.Kp * error

        # Integral term with anti-windup
        self.integral += error
        if self.integral > self.output_max:
            self.integral = self.output_max
        elif self.integral < self.output_min:
            self.integral = self.output_min
        integral = self.Ki * self.integral

        # Derivative term
        derivative = self.Kd * (error - self.previous_error)

        # PID output
        output = proportional + integral + derivative

        # Debug: Print the PID terms
        print(f"Proportional: {proportional:.3f}, Integral: {integral:.3f}, Derivative: {derivative:.3f}")

        # Clamp the output to the valid range
        output = max(self.output_min, min(output, self.output_max))

        # Update previous error
        self.previous_error = error

        return output