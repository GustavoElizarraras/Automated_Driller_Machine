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
        super(MotorController, self).__init__()
        # True - al fin de carrera
        self.motors = {
            "x" : {"pins": [15, 14], "position": 0, "limit_race": 0},
            "y" : {"pins": [2, 18], "position": 0, "limit_race": 0},
            "z" : {"pins": [4, 3], "position": 0, "limit_race": 0},
            "table" : {"pins": [20, 21], "position": 0},
            "pistons" : {"pins": [17, 25], "position": 0},
            "driller": {"pins": [27], "position": 0}
        }

    def send_pulse_500Hz(self, pwm_pin):
        GPIO.output(pwm_pin, False)
        time.sleep(0.005)
        GPIO.output(pwm_pin, True)
        time.sleep(0.01)
        GPIO.output(pwm_pin, False)
        time.sleep(0.005)

    def send_pulse_1KHz(self, pwm_pin):
        GPIO.output(pwm_pin, False)
        time.sleep(0.000125)
        GPIO.output(pwm_pin, True)
        time.sleep(0.00025)
        GPIO.output(pwm_pin, False)
        time.sleep(0.000125)

    def send_pulse(self, pwm_pin, motor):
        if motor == "pistons":
            self.send_pulse_500Hz(pwm_pin)
        elif motor == "z":
            if self.motors["z"]["position"] > 900:
                self.send_pulse_500Hz(pwm_pin)
            else:
                self.send_pulse_1KHz(pwm_pin)
        else:
            self.send_pulse_1KHz(pwm_pin)

    def move_motor(self, pulses, direction, motor):

        GPIO.output(self.motors[motor]["pins"][0], direction)

        if pulses > 1:

            for _ in range(pulses):

                self.motors["x"]["limit_race"] = 0
                self.motors["y"]["limit_race"] = 0
                self.motors["z"]["limit_race"] = 0

                if direction:
                    self.motors[motor]["position"] -= 1
                else:
                    self.motors[motor]["position"] += 1

                if  self.motors["y"]["position"] > 11.5e4:
                    break

                if  self.motors["x"]["position"] > 8.5e3:
                    break

                if  self.motors["z"]["position"] > 1100:
                    break

                while not GPIO.input(11):
                    # door
                    self.move_motor(1, False, "driller")
                    time.sleep(0.000005)

                while GPIO.input(22):
                    self.motors["x"]["limit_race"] += 1
                    if self.motors["x"]["limit_race"] == 10 and GPIO.input(22):
                        self.rebound_limit_switch("x")
                        self.motors["x"]["position"] = 0
                        return

                while GPIO.input(10):
                    self.motors["y"]["limit_race"] += 1
                    if self.motors["y"]["limit_race"] == 10 and GPIO.input(10):
                        self.rebound_limit_switch("y")
                        self.motors["y"]["position"] = 0
                        return

                while GPIO.input(9):
                    self.motors["z"]["limit_race"] += 1
                    if self.motors["z"]["limit_race"] == 10 and GPIO.input(9):
                        self.rebound_limit_switch("z")
                        self.motors["z"]["position"] = 0
                        return

                self.send_pulse(self.motors[motor]["pins"][1], motor)

    def rebound_limit_switch(self, motor):
        GPIO.output(self.motors[motor]["pins"][0], False)
        if motor == "z":
            pulses = 100
        else:
            pulses = 280
        for _ in range(pulses):
            self.send_pulse(self.motors[motor]["pins"][1], motor)

    def go_default_position(self):
        pulses_z, direction_z = self.get_pulses_and_direction("z", -1100)
        self.move_motor(pulses_z, direction_z, "z")
        pulses_x, direction_x = self.get_pulses_and_direction("x", -10000)
        self.move_motor(pulses_x, direction_x, "x")
        pulses_y, direction_y = self.get_pulses_and_direction("y", -12000)
        self.move_motor(pulses_y, direction_y, "y")

    def go_home(self):
        pulses_z, direction_z = self.get_pulses_and_direction("z", 500)
        self.move_motor(pulses_z, direction_z, "z")
        pulses_x, direction_x = self.get_pulses_and_direction("x", 0)
        self.move_motor(pulses_x, direction_x, "x")
        pulses_y, direction_y = self.get_pulses_and_direction("y", 5000)
        self.move_motor(pulses_y, direction_y, "y")

    def move_x_y(self, pos_x, pos_y):
        pulses_x, direction_x = self.get_pulses_and_direction("x", pos_x)
        self.move_motor(pulses_x, direction_x, "x")
        pulses_y, direction_y = self.get_pulses_and_direction("y", pos_y)
        self.move_motor(pulses_y, direction_y, "y")

    def drill(self):
        self.move_motor(600, False, "z")
        time.sleep(0.25)
        self.move_motor(600, True, "z")

    def set_grabber(self, width_pulses, grab=True):
        if grab:
            self.move_motor(width_pulses, False, "pistons")
        if not grab:
            self.move_motor(width_pulses, True, "pistons")

    def move_y_to_user(self):
        # good img at this position
        pulses, direction = self.get_pulses_and_direction("y", 9300)
        self.move_motor(pulses, direction, "y")

    def convert_pixels_utils(self, pixels, motor):
        if motor == "pistons":
            pulses = int((130 - (pixels / 5.4 )) * 5.25)
            return pulses
        else:
            px_x, px_y = pixels
            x = px_x / 640
            y = px_y / 640
            pos_x = int(1661.590361+6292.048193*x+(132.5-0.1315*px_x-0.7548*px_y+9.017e-5*(px_x**2)+0.001072*px_x*px_y+0.00139*(px_y**2)-6.27e-7*(px_x**3)-7.266e-7*(px_x**2)*px_y-1.025e-6*px_x*(px_y**2)-9.297e-7*(px_y**3)))
            pos_x -= 20
            pos_y = int(8249.387309-5825.820569*y+(182.9-0.4563*px_x-0.3153*px_y+0.0002233*(px_x**2)+0.0008337*px_x*px_y-3.802e-5*(px_y**2)-1.106e-7*(px_x**3)+5.377e-8*(px_x**2)*px_y-4.826e-7*(px_y**2)*px_x-5.642e-8*(px_y**3)))
            pos_y -= 85
            return pos_x, pos_y

    def get_pulses_and_direction(self, motor, destination):
        actual_y = self.motors[motor]["position"]
        pulses = destination - actual_y
        direction = False
        if pulses < 0:
            direction = True
        return abs(pulses), direction