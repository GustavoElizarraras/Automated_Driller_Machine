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

    def send_step_pulse(self, pwm_pin):
        # 1KHz
        GPIO.output(pwm_pin, False)
        time.sleep(0.00025)
        GPIO.output(pwm_pin, True)
        time.sleep(0.0005)
        GPIO.output(pwm_pin, False)
        time.sleep(0.00025)

    def move_engine(self, pulsos, direcc, motor):

        GPIO.output(self.motors[motor]["pins"][0], direcc)

        for _ in range(pulsos):

            if direcc:
                self.motors[motor]["position"] += 1
            else:
                self.motors[motor]["position"] -= 1

            if self.motors[motor]["position"] < 0:
                self.motors[motor]["position"] = 0
                break

            if GPIO.input(25) or GPIO.input(8) or GPIO.input(7) or self.motors[motor]["position"] > 1e4:
                break

            self.send_step_pulse(self.motors[motor]["pins"][1])

            while GPIO.input(1):
                # open door or from the interface
                time.sleep(0.000005)
                GPIO.output(self.driller, False)

    def start_position(self):
        self.move_engine(1000, not self.direc_z, "z")
        self.move_engine(10000, not self.direc_x, "x")
        self.move_engine(10000, not self.direc_y, "y")


    def home(self):
        # position for taking the photo
        self.move_engine(10000, not self.direc_z, "z")
        self.move_engine(14000,not self.direc_x, "x")
        self.move_engine(14000,not self.direc_y, "y")

    def set_table_height(self, direction):
        if direction == "raise":
            self.move_engine(1000, True, "table")
        elif direction == "down":
            self.move_engine(1000, False, "table")

    def set_engine_z_height(self, direction):
        if direction == "raise":
            self.move_engine(5000, True, "z")
        elif direction == "down":
            self.move_engine(5000, False, "z")

    def move_x_y(self, pulsos_x, coordenada_x, pulsos_y, coordenada_y):
        #
        self.move_engine(pulsos_x, coordenada_x, "x")
        self.move_engine(pulsos_y, coordenada_y, "y")

    def drill(self):
        self.move_engine(1500, True, "z")
        self.move_engine(1500, False, "z")

    def set_grabber(self, width, grab=True):
        if grab:
            # TODO: convert width to pulses
            self.move_engine(width_pulses, True, "pistons")
        if not grab:
            self.move_engine(width_pulses, False, "pistons")

    def move_y_to_user(self):
        actual_y = self.motors["y"]["position"]
        pulses = 10000 - actual_y
        direction = True
        if pulses < 0:
            direction = False
        self.move_engine(abs(pulses), direction, "y")

