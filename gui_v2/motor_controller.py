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
            "driller": 27
        }

    def send_pulse(self, pwm_pin, motor):
        if motor == "pistons" or motor == "z":
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
        for i in range(pulses):
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

    def move_x_y(self, pos_x, pos_y):
        pulses_x, direction_x = self.get_pulses_and_direction("x", pos_x)
        self.move_motor(pulses_x, direction_x, "x")
        pulses_y, direction_y = self.get_pulses_and_direction("y", pos_y)
        self.move_motor(pulses_y, direction_y, "y")

    def drill(self):
        self.move_motor(600, False, "z")
        time.sleep(1)
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

    def convert_pixels_to_pulses(self, pixels, motor):
        # for x and y motors, 50 pulses = 1mm
        # for pistons is not clear, hardcoded 7 pulses = 1mm per side
        # 5.4 is a hardcoded unit conversor (px/mm), 4.92 should be the real value

        if motor == "x":
            posx = pixels / 640
            pulses = int(1661.590361+6292.048193*x+(132.5-0.1315*posx-0.7548*posy+9.017e-5*(posx**2)+0.001072*posx*posy+0.00139*(posy**2)-6.27e-7*(posx**3)-7.266e-7*(posx**2)*posy-1.025e-6*posx*(posy**2)-9.297e-7*(posy**3)))
            #pulses = int(1611.590361 + (6292.048193*pixels // 640))
        elif motor == "y":
            posy = pixels / 640
            pulses = int(8249.387309-5825.820569*y+(182.9-0.4563*posx-0.3153*posy+0.0002233*(posx**2)+0.0008337*posx*posy-3.802e-5*(posy**2)-1.106e-7*(posx**3)+5.377e-8*(posx**2)*posy-4.826e-7*(posy**2)*posx-5.642e-8*(posy**3)))
            #pulses = int(8219.387309 - (5825.820569*pixels // 640))
        elif motor == "pistons":
            pulses = int((130 - (pixels / 5.4 )) * 5.25)
        return pulses

    def get_pulses_and_direction(self, motor, destination):
        actual_y = self.motors[motor]["position"]
        pulses = destination - actual_y
        direction = False
        if pulses < 0:
            direction = True
        return abs(pulses), direction
