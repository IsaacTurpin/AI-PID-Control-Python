import time

class PIDController:
    def __init__(self):
        self.Kp = 0.3  # Proportional gain
        self.Ki = 0.1  # Integral gain
        self.Kd = 0.02  # Derivative gain
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

        # Integral term with improved anti-windup
        self.integral += error * dt
        integral = self.Ki * self.integral

        # Ensure integral stays within output limits to prevent windup
        if integral > self.output_max:
            integral = self.output_max
        elif integral < self.output_min:
            integral = self.output_min

        # Derivative term based on error change, not measured value
        derivative = self.Kd * (error - self.previous_error) / dt

        # Compute final PID output
        output = proportional + integral + derivative

        # Clamp output to valid range
        output = max(self.output_min, min(output, self.output_max))

        # Adjust integral term to avoid windup during saturation
        if output == self.output_max:
            self.integral -= error * dt  # Undo integral buildup if output is maxed
        elif output == self.output_min:
            self.integral += error * dt  # Undo integral buildup if output is min

        # Store previous values
        self.previous_error = error
        self.previous_measured = measured_value
        self.last_time = current_time

        return output

