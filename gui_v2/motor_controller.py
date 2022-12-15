import time
import RPi.GPIO as GPIO

class PinsSetup():
    def __init__(self):
        # Use BCM GPIO references
        # Instead of physical pin numbers
        GPIO.setmode(GPIO.BCM)
        # Define GPIO signals to use Pins
        self.output_pins = [2, 3, 4, 14, 15, 18, 17, 20, 21, 25, 27]
        self.input_pins = [22, 11, 10, 9]
        # Set all pins as output and input
        GPIO.setwarnings(False)
        self.setup_pins()

    def setup_pins(self):
        for pin in self.output_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

        for pin in self.input_pins:
            GPIO.setup(pin, GPIO.IN)

class MotorController(PinsSetup):
    def __init__(self):
        super(self, MotorController).__init__()
        # True - al fin de carrera
        self.motors = {
            "x" : {"pins": [15, 14], "position": 0},
            "y" : {"pins": [2, 18], "position": 0},
            "z" : {"pins": [4, 3], "position": 0},
            "table" : {"pins": [20, 21], "position": 0},
            "pistons" : {"pins": [17, 25], "position": 0},
            "driller": 27
        }

    def send_pulse(self, pwm_pin, motor):
        if motor == "pistons":
            # 500
            GPIO.output(pwm_pin, False)
            time.sleep(0.005)
            GPIO.output(pwm_pin, True)
            time.sleep(0.01)
            GPIO.output(pwm_pin, False)
            time.sleep(0.005)
        else:
            # 1KHz
            GPIO.output(pwm_pin, False)
            time.sleep(0.000125)
            GPIO.output(pwm_pin, True)
            time.sleep(0.00025)
            GPIO.output(pwm_pin, False)
            time.sleep(0.000125)

    def move_motor(self, pulses, direction, motor):

        GPIO.output(self.motors[motor]["pins"][0], direction)

        for _ in range(pulses):

            if direction:
                self.motors[motor]["position"] += 1
            else:
                self.motors[motor]["position"] -= 1

            if  self.motors["y"]["position"] > 1e4:
                break

            if  self.motors["x"]["position"] > 7e3:
                break

            if GPIO.input(11):
                # door
                break

            if GPIO.input(22):
                self.rebound_limit_switch("x")
                self.motors["x"]["position"] = 0
                break
            if GPIO.input(10):
                self.rebound_limit_switch("y")
                self.motors["y"]["position"] = 0
                break
            if GPIO.input(9):
                self.rebound_limit_switch("z")
                self.motors["z"]["position"] = 0
                break

            self.send_pulse(self.motors[motor]["pins"][1], motor)

    def rebound_limit_switch(self, motor):
        GPIO.output(self.motors[motor]["pins"][0], False)
        for _ in range(125):
            self.send_pulse(self.motors[motor]["pins"][1], motor)

    def go_default_position(self):
        pulses_z, direction_z = self.get_pulses_and_direction("z", -2000)
        self.move_motor(pulses_z, direction_z, "z")
        pulses_x, direction_x = self.get_pulses_and_direction("x", -6000)
        self.move_motor(pulses_x, direction_x, "x")
        pulses_y, direction_y = self.get_pulses_and_direction("y", -10000)
        self.move_motor(pulses_y, direction_y, "y")


    def go_home(self):
        # position for taking the photo
        pulses_z, direction_z = self.get_pulses_and_direction("z", 0)
        self.move_motor(pulses_z, direction_z, "z")
        pulses_x, direction_x = self.get_pulses_and_direction("x", 0)
        self.move_motor(pulses_x, direction_x, "x")
        pulses_y, direction_y = self.get_pulses_and_direction("y", 0)
        self.move_motor(pulses_y, direction_y, "y")

    def set_table_height(self, direction):
        if direction == "raise":
            self.move_motor(1000, False, "table")
        elif direction == "down":
            self.move_motor(1000, True, "table")

    def set_motor_z_height(self, direction):
        if direction == "raise":
            self.move_motor(5000, True, "z")
        elif direction == "down":
            self.move_motor(5000, False, "z")

    def move_x_y(self, pulses_x, direction_x, pulses_y, direction_y):
        self.move_motor(pulses_x, direction_x, "x")
        self.move_motor(pulses_y, direction_y, "y")

    def drill(self):
        self.move_motor(1500, True, "z")
        self.move_motor(1500, False, "z")

    def set_grabber(self, width_pulses, grab=True):
        if grab:
            # TODO: convert width to pulses (?) try out if it works
            self.move_motor(width_pulses, False, "pistons")
        if not grab:
            self.move_motor(width_pulses, True, "pistons")

    def move_y_to_user(self):
        pulses, direction = self.get_pulses_and_direction("y", 10000)
        self.move_motor(pulses, direction, "y")

    def convert_pixels_to_pulses(self, pixels, motor):
        # for x and y motors, 50 pulses = 1mm
        # for other motors, 100 pulses = 1mm
        # 5.4 is a hardcoded unit conversor (px/mm), 4.92 should be the real value

        # TODO: Implent correctly the pulses for the drilling sequence
        if motor == "y" or motor == "x":
            pulses = int((pixels / 5.4 ) * 50)
        elif motor == "pistons":
            pulses = int(130 - (pixels / 5.4 ) * 7)
        return pulses

    def get_pulses_and_direction(self, motor, destination):
        actual_y = self.motors[motor]["position"]
        pulses = destination - actual_y
        direction = False
        if pulses < 0:
            direction = True
        return abs(pulses), direction

