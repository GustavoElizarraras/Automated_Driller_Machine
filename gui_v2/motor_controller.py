import time
import RPi.GPIO as GPIO

class PinsSetup():
    def __init__(self):
        # Use BCM GPIO references
        # Instead of physical pin numbers
        GPIO.setmode(GPIO.BCM)
        # Define GPIO signals to use Pins
        self.output_pins = [2,3,4,14,15,18,17,27,22,23,24]
        self.input_pins = [25,8,7,1]
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
        super().__init__()

        self.motors = {
            "x" : {"pins": [3, 2], "position": 0},
            "y" : {"pins": [14, 4], "position": 0},
            "z" : {"pins": [18, 15], "position": 0},
            "table" : {"pins": [27, 17], "position": 0},
            "pistons" : {"pins": [23, 22], "position": 0},
            "driller": 14
        }

    def send_pulse(self, pwm_pin):
        # 1KHz
        GPIO.output(pwm_pin, False)
        time.sleep(0.00025)
        GPIO.output(pwm_pin, True)
        time.sleep(0.0005)
        GPIO.output(pwm_pin, False)
        time.sleep(0.00025)

    def move_motor(self, pulses, direcc, motor):

        GPIO.output(self.motors[motor]["pins"][0], direcc)

        for _ in range(pulses):

            if direcc:
                self.motors[motor]["position"] += 1
            else:
                self.motors[motor]["position"] -= 1

            if  self.motors[motor]["position"] > 1e4:
                break

            if GPIO.input(25):
                # supposing x
                self.motors["x"]["position"] = 0
                break
            if GPIO.input(8):
                # supposing y
                self.motors["y"]["position"] = 0
                break
            if GPIO.input(7):
                # supposing z
                self.motors["z"]["position"] = 0
                break

            self.send_pulse(self.motors[motor]["pins"][1])

            while GPIO.input(1):
                # open door or from the interface
                time.sleep(0.000005)
                GPIO.output(self.driller, False)

    def go_default_position(self):
        pulses_z, direction_z = self.get_pulses_direction("z", -10000)
        self.move_motor(pulses_z, direction_z, "z")
        pulses_x, direction_x = self.get_pulses_direction("x", -10000)
        self.move_motor(pulses_x, direction_x, "x")
        pulses_y, direction_y = self.get_pulses_direction("y", -10000)
        self.move_motor(pulses_y, direction_y, "y")


    def go_home(self):
        # position for taking the photo
        pulses_z, direction_z = self.get_pulses_direction("z", 0)
        self.move_motor(pulses_z, direction_z, "z")
        pulses_x, direction_x = self.get_pulses_direction("x", 0)
        self.move_motor(pulses_x, direction_x, "x")
        pulses_y, direction_y = self.get_pulses_direction("y", 0)
        self.move_motor(pulses_y, direction_y, "y")

    def set_table_height(self, direction):
        if direction == "raise":
            self.move_motor(1000, True, "table")
        elif direction == "down":
            self.move_motor(1000, False, "table")

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

    def set_grabber(self, width, grab=True):
        if grab:
            # TODO: convert width to pulses
            self.move_motor(width_pulses, True, "pistons")
        if not grab:
            self.move_motor(width_pulses, False, "pistons")

    def move_y_to_user(self):
        pulses, direction = self.get_pulses_direction("y", 10000)
        self.move_motor(pulses, direction, "y")

    def get_pulses_direction(self, motor, destination):
        actual_y = self.motors[motor]["position"]
        pulses = destination - actual_y
        direction = True
        if pulses < 0:
            direction = False
        return abs(pulses), direction

