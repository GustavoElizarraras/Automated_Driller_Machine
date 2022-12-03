import time
import RPi.GPIO as GPIO
# Use BCM GPIO references
# Instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
# Define GPIO signals to use Pins

output_pins = [2,3,4,14,15,18,17,27,22,23,24]
input_pins = [25,8,7,1]
# Set all pins as output and input
GPIO.setwarnings(False)

for pin in output_pins:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,False)

for pin in input_pins:
    GPIO.setup(pin,GPIO.IN)

ctrx = 0
ctry = 0
ctrz = 0
ctrm = 0
ctrp = 0
motor_x = [2,3]
motor_y = [4,14]
motor_z = [15,18]
motor_mesa = [17,27]
motor_pistones = [22,23]
direc_x = True
direc_y = True
direc_z = True
direc_mesa = True
direc_pistones = True

def mandar_pulso(pwm_pin):
    # 1KHz
    GPIO.output(pwm_pin, False)
    time.sleep(0.00025)
    GPIO.output(pwm_pin, True)
    time.sleep(0.0005)
    GPIO.output(pwm_pin, False)
    time.sleep(0.00025)

def mover_motor(pulsos,direcc,motor):
    ctr=0
    GPIO.output(motor[0], direcc)
    for i in range(pulsos):
        mandar_pulso(motor[1])
        if direcc:
            ctr=ctr+1
        else:
            ctr=ctr-1
        if GPIO.input(25) or GPIO.input(8) or GPIO.input(7):

            return ctr
        while GPIO.input(1):
            time.sleep(0.000005)
            GPIO.output(24,False)
    return ctr

def inicio():

    mover_motor(10000,not direc_z,motor_z)
    mover_motor(200,direc_z,motor_z)

    mover_motor(10000,not direc_x,motor_x)
    mover_motor(200,direc_x,motor_x)

    mover_motor(10000,not direc_y,motor_y)
    mover_motor(9000,direc_y,motor_y)

    crtpm += crtpm+mover_motor(1000,direc_mesa,motor_mesa)

def sujecion(ancho):
    ctrp += mover_motor(ancho,direc_pistones,motor_pistones)

def home():
    mover_motor(10000,not direc_z,motor_z)
    ctrz += mover_motor(200,direc_z,motor_z)

    mover_motor(14000,not direc_x,motor_x)
    ctrx += mover_motor(5350,direc_x,motor_x)

    mover_motor(14000,not direc_y,motor_y)
    ctry += mover_motor(10500,direc_y,motor_y)

def setup_mesa():
    ctrm=ctrm+mover_motor(ctrm,not direc_mesa,motor_mesa)



