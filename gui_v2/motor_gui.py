from picamera import PiCamera
from tflite_runtime.interpreter import Interpreter
import motor_controller as mc
import tkinter as tk
from tkinter import ttk
from functools import partial
from PIL import Image, ImageTk
import numpy as np

class CalculateWidth(ttk.Frame):
    def __init__(self, container):

        super().__init__(container)
        self.img_array = None
        self.container = container
        self.create_widgets()
        motor_controller.go_home_position()
        self.orig_x = None
        self.orig_y = None
        self.dx = None
        self.dy = None

    def create_widgets(self):
        # button to move
        self.start_button = ttk.Button(self.container, text='Mover a la coordenada')
        self.start_button.place(x = 390, y = 30)
        self.start_button.configure(command=self.move_interest_coord)
        #x_orig
        self.o1 = tk.Entry(self.master)
        self.o1.place(x = 370, y = 90)
        #y_orig
        self.o2 = tk.Entry(self.master)
        self.o2.place(x = 320, y = 90)
        #x
        self.e1 = tk.Entry(self.master)
        self.e1.place(x = 200, y = 150)
        #y
        self.e2 = tk.Entry(self.master)
        self.e2.place(x = 200, y = 180)
        # button to print and return drill up
        self.start_button = ttk.Button(self.container, text='IMPRIMIR dx, dy Y subir Motor')
        self.start_button.place(x = 390, y = 210)
        self.start_button.configure(command=self.print_difference)

    def move(self):
        dx, dy = int(self.e1.get()), int(self.e2.get())
        self.dx += dx
        self.dy += dy
        new_pos_x = motor_controller.motors["x"]["position"] + dx
        new_pos_y = motor_controller.motors["y"]["position"] + dy
        pulses_x, direc_x = motor_controller.get_pulses_and_direction("x", new_pos_x)
        pulses_y, direc_y = motor_controller.get_pulses_and_direction("y", new_pos_y)
        motor_controller.move_motor(pulses_x, direc_x, "x")
        motor_controller.move_motor(pulses_y, direc_y, "y")

    def move_interest_coord(self):
        self.origx, self.origy = int(self.o1.get()), int(self.o2.get())
        pulses_y, direc_y = motor_controller.get_pulses_and_direction("y", self.origy)
        pulses_x, direc_x = motor_controller.get_pulses_and_direction("x", self.origx)
        motor_controller.move_motor(pulses_x, direc_x, "x")
        motor_controller.move_motor(pulses_y, direc_y, "y")
        motor_controller.move_motor(700, False, "z")

    def print_difference(self):
        motor_controller.move_motor(700, True, "z")
        print("dx = ", self.dx, "dy = ", self.dy)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("900x650")
        self.title('BARRENADORA AUTOMATIZADA')
        self.resizable(False, False)

if __name__ == "__main__":

    motor_controller = mc.MotorController()
    app = App()
    CalculateWidth(app)
    app.mainloop()