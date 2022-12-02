import time
import RPi.GPIO as GPIO
# Use BCM GPIO references
# Instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
# Define GPIO signals to use Pins 

PinsOutput = [2,3,4,14,15,18,17,27,22,23,24]
PinsInput=[25,8,7,1]
# Set all pins as output and input
GPIO.setwarnings(False)

for pin in PinsOutput:   
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,False)

for pin in PinsInput:   
    GPIO.setup(pin,GPIO.IN)
ctrx=0
ctry=0
ctrz=0
ctrm=0
ctrp=0
MotorX=[2,3]
MotorY=[4,14]
MotorZ=[15,18]
MotorM=[17,27]
MotorP=[22,23]
direcx=True
direcy=True
direcz=True
direcm=True
direcp=True

def pulso(PWM):
    # 1KHz
    GPIO.output(PWM, False)
    time.sleep(0.00025)
    GPIO.output(PWM, True)
    time.sleep(0.0005)
    GPIO.output(PWM, False)
    time.sleep(0.00025)
    
def Motor_bloque(pulsos,direcc,motor):   
    ctr=0
    GPIO.output(motor[0], direcc)
    for i in range(pulsos):
        pulso(motor[1])
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

def Inicio():
    
    Motor_bloque(10000,not direcz,MotorZ)
    Motor_bloque(200,direcz,MotorZ)

    Motor_bloque(10000,not direcx,MotorX)
    Motor_bloque(200,direcx,MotorX)

    Motor_bloque(10000,not direcy,MotorY)
    Motor_bloque(9000,direcy,MotorY)
    
    crtpm += crtpm+Motor_bloque(1000,direcm,MotorM)

def Sujecion(ancho):
    ctrp += Motor_bloque(ancho,direcp,MotorP)

def Home():
    Motor_bloque(10000,not direcz,MotorZ)
    ctrz += Motor_bloque(200,direcz,MotorZ)

    Motor_bloque(14000,not direcx,MotorX)
    ctrx += Motor_bloque(5350,direcx,MotorX)

    Motor_bloque(14000,not direcy,MotorY)
    ctry += Motor_bloque(10500,direcy,MotorY)

def MesaSetup():
    ctrm=ctrm+Motor_bloque(ctrm,not direcm,MotorM)



