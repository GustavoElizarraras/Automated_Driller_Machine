#from picamera import PiCamera
import tkinter as tk
from tkinter import ttk
from functools import partial
from PIL import Image, ImageTk
import numpy as np
import cv2
import os
import csv
import glob
import time
import re

class PiCameraPhoto(ttk.Frame):
    def __init__(self, container, dir):
        super().__init__(container)
        self.container = container
        self.create_widgets()
        self.camera = PiCamera()
        self.camera.resolution = (640,640)
        self.dir = dir
        self.last_img_path = self.get_last_file_dir()
        self.img_name = self.get_img_name(self.last_img_path)
        self.take_photo()

    def take_photo(self):
        label = tk.Label(self.container, text= "Tomando foto")
        label.place(x = 380, y=150)
        self.camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        self.camera.capture(self.dir + self.img_name)
        time.sleep(2)
        self.display_binarizing_panel()

    def get_last_file_dir(self):
        list_of_files = glob.glob(self.dir + "*")
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    def get_img_name(self, img_path_name):
        last_img = img_path_name[:-11]
        last_img_num = re.findall(r'\d+', last_img)
        img_name = "img_" + str(last_img_num[-1] + 1) + ".jpg"
        return img_name

    def create_widgets(self):
        self.instructions = tk.Text(self.master, height=1, width=70)
        text='Una vez que la placa esté fijada, presione el botón "Tomar Foto"'
        self.instructions.insert("e", text)
        self.instructions.place(x = 200, y = 100)
        # button
        self.start_button = ttk.Button(self.container, text='Tomar foto')
        self.start_button.place(x = 390, y = 130)
        self.start_button.configure(command=self.take_photo)

    def display_binarizing_panel(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = BinarizingFrame(self.container, self.img_name)
        frame.tkraise()

class BinarizingFrame(ttk.Frame):
    def __init__(self, container, img_name):
        super().__init__(container)
        self.container = container
        self.img_name = img_name
        # Hardcoded path, to remove later
        #self.img_path = os.getcwd() + "/dataset/useful_handpicked_rot/12300111_temp_2.jpg"
        self.img_path = "/Documents/pcb_images/" + self.img_name

        # PCB Image
        self.img = Image.open(self.img_path)
        # image for opencv
        # self.img_array = cv2.merge([np.asarray(self.img), np.asarray(self.img), np.asarray(self.img)])

        self.img_array = np.asarray(self.img)

        self.render_img(self.img_array)
        self.create_widgets()

    def render_img(self, img_array):
        self.render = ImageTk.PhotoImage(Image.fromarray(img_array))
        self.img_label = ttk.Label(self.container, image=self.render, cursor="cross")
        self.img_label.place(x = 0, y = 0)

    def create_widgets(self):

        self.slider1 = tk.Scale(self.container, from_=0, to=255, orient="horizontal")
        self.slider1.bind("<ButtonRelease-1>", self.binarize)
        self.slider1.place(x=700, y=10)

        self.slider1_2 = tk.Scale(self.container, from_=0, to=255, orient="horizontal")
        self.slider1_2.bind("<ButtonRelease-1>", self.binarize)
        self.slider1_2.place(x=700, y=50)

        self.slider2 = tk.Scale(self.container, from_=0, to=5, orient="horizontal")
        self.slider2.bind("<ButtonRelease-1>", self.dilate)
        self.slider2.place(x=700, y=90)

        self.slider3 = tk.Scale(self.container, from_=0, to=5, orient="horizontal")
        self.slider3.bind("<ButtonRelease-1>", self.erode)
        self.slider3.place(x=700, y=130)

        # button
        self.continue_button = ttk.Button(self.container, text='Detectar barrenos')
        self.continue_button.place(x = 700, y = 10)
        self.continue_button.configure(command=self.display_control_panel)

    def binarize(self, event):
        threshold_low = self.slider1.get()
        threshold_high = self.slider1_2.get()
        _, new_image = cv2.threshold(self.img_array, threshold_low , threshold_high, cv2.THRESH_BINARY)
        self.render_img(new_image)

    def dilate(self, event):
        k = self.slider2.get()
        kernel = np.ones((k,k), np.uint8)
        new_image = cv2.dilate(self.img_array, kernel, iterations = 1)
        self.render_img(new_image)

    def erode(self, event):
        k = self.slider3.get()
        kernel = np.ones((k,k), np.uint8)
        new_image = cv2.erode(self.img_array, kernel, iterations = 1)
        self.render_img(new_image)

    def display_control_panel(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, [])
        frame.tkraise()

class ImageInitializer(ttk.Frame):
    def __init__(self, container, coords=None):
        super().__init__(container)
        self.container = container

        self.dir = "/Documents/pcb_images/"
        #self.img_path = self.get_last_img_dir()

        # Hardcoded path, to remove later
        #self.img_path = os.getcwd() + "/dataset/useful_handpicked_rot/12300111_temp_2.jpg"
        self.img_path = self.get_last_img_dir()
        # PCB Image
        self.img = Image.open(self.img_path)
        # image for opencv
        self.img_array = cv2.merge([np.asarray(self.img), np.asarray(self.img), np.asarray(self.img)])
        #self.img_array = np.asarray(self.img)
        # List of coordinates (dummy for now)
        if coords is None:
            coords_center_obj = ProcessPinHolesCenters(self.img_array, [84,555,58,529,83,474,57,448,83,392,57,366,84,312,58,286,83,230,57,204,84,150,58,124,84,68,58,42])
            self.coords = coords_center_obj.coords_processed
        else:
            self.coords = coords
        # pin-holes identifiers
        self.holes = { (i,):coord for i, coord in enumerate(self.coords)}
        self.show_green_holes()

    def get_last_img_dir(self):
        list_of_files = glob.glob(self.dir + "*.jpg")
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    def render_img(self, img_array, binding=None):
        self.render = ImageTk.PhotoImage(Image.fromarray(img_array))
        self.img_label = ttk.Label(self.container, image=self.render, cursor="cross")
        self.img_label.place(x = 0, y = 0)
        self.img_label.bind("<Button-1>", binding)

    def show_green_holes(self, binding=None):
        for coord in  self.coords:
            center = (coord[0], coord[1])
            radius = coord[2]
            color = (0,255,0)
            cv2.circle(self.img_array, center, radius, color, 3)
            cv2.circle(self.img_array, center, 2, color, -1)
        self.holes = { (i,):coord for i, coord in enumerate(self.coords)}
        self.draw_hole_number()
        self.render_img(self.img_array, binding)

    def colour_selected(self, center, color, radius=5):
        cv2.circle(img=self.img_array, center=center,
                   radius=radius, color=color, thickness=4)
        self.render_img(self.img_array)

    def draw_hole_number(self):
        for num, coord in self.holes.items():
            cv2.putText(self.img_array, f"B{num[0]}", (coord[0]-10, coord[1]-11), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,135,160), 2)


class ControlFrame(ImageInitializer):
    def __init__(self, container, coords):
        super().__init__(container, coords)
        self.create_widgets()

    def create_widgets(self):

        # button
        self.move_button = ttk.Button(self.container, text='Añadir o Mover barreno')
        self.move_button.place(x = 700, y = 10)
        self.move_button.configure(command=self.press_move_add)

        # button
        self.del_button = ttk.Button(self.container, text='Eliminar barreno')
        self.del_button.place(x = 700, y = 50)
        self.del_button.configure(command=self.press_delete)

        # button
        self.del_button = ttk.Button(self.container, text='Iniciar barrenado')
        self.del_button.place(x = 700, y = 90)
        self.del_button.configure(command=self.press_delete)

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def press_move_add(self):
        self.clear_frame()
        frame = AddMovePCBHole(self.container, self.coords)
        frame.tkraise()

    def press_delete(self):
        self.clear_frame()
        frame = DeletePCBHole(self.container, self.coords)
        frame.tkraise()

class AddMovePCBHole(ImageInitializer):
    def __init__(self, container, coords):
        super().__init__(container, coords)
        self.posx, self.posy = None, None
        self.selected_hole_name = None
        self.dummy_img = self.img_array
        self.img_label.bind("<Button-1>", self.new_circle)
        self.create_widgets()
        self.insert_cursor()

    def create_widgets(self):
        self.instructions = tk.Text(self.master, height=8, width=28)
        text='Para añadir un barreno da \nclick sobre la imagen, para mover un barreno, seleccionael barreno y presiona los \nbotones correspondientes'
        self.instructions.insert("e", text)
        self.instructions.place(x = 680, y = 10)

        self.holes = { (i,):coord for i, coord in enumerate(self.coords)}
        self.langs_var = tk.StringVar(value=[f"Barreno {i}" for i in range(len(self.holes.keys()))])
        self.listbox = tk.Listbox(
            self.container,
            listvariable=self.langs_var,
            height=6)
        self.listbox.place(x = 700, y = 130)
        self.listbox.bind('<<ListboxSelect>>', self.move_selected)

        # button
        self.return_button = ttk.Button(self.container, text='Volver')
        self.return_button.place(x = 700, y = 420)
        self.return_button.configure(command=self.return_main)

    def move_selected(self, event):
        # get pin hole
        self.selected_hole_name = self.listbox.curselection()
        self.posx, self.posy = self.holes[self.selected_hole_name][0], self.holes[self.selected_hole_name][1]
        self.radius = self.holes[self.selected_hole_name][2]
        self.show_green_holes()
        self.colour_selected((self.posx, self.posy), (255,227,51), self.radius)
        #self.holes.pop(self.selected_hole_name)

    def insert_cursor(self):
        # move methods
        self.move_up = partial(self.move_pin_hole, "up")
        self.move_down = partial(self.move_pin_hole, "down")
        self.move_left = partial(self.move_pin_hole, "left")
        self.move_right = partial(self.move_pin_hole, "right")
        # buttons
        self.button_up = ttk.Button(self.container, text='arriba', command=self.move_up)
        self.button_up.place(x = 700, y = 250)

        self.button_down = ttk.Button(self.container, text='abajo', command=self.move_down)
        self.button_down.place(x = 700, y = 290)

        self.button_left = ttk.Button(self.container, text='izquierda', command=self.move_left)
        self.button_left.place(x = 700, y = 330)

        self.button_right = ttk.Button(self.container, text='derecha', command=self.move_right)
        self.button_right.place(x = 700, y = 370)

    def move_pin_hole(self, direction):
        self.img_label.destroy()
        self.render_img(self.dummy_img, self.new_circle)
        # remove actual circle
        cv2.circle(img=self.dummy_img, center = (self.posx, self.posy),
                   radius=2, color =(255,255,255), thickness=-1)

        if direction == "up":
            self.posy -= 1
        elif direction == "down":
            self.posy += 1
        elif direction == "left":
            self.posx -= 1
        elif direction == "right":
            self.posx += 1
        cv2.circle(img=self.dummy_img, center = (self.posx, self.posy),
                   radius=2, color =(0,0,255), thickness=-1)
        # new coordinate and overwrite all the pin-holes coords
        self.holes[self.selected_hole_name] = (self.posx, self.posy, self.radius)
        self.coords = list(self.holes.values())
        self.img_label.destroy()
        self.render_img(self.dummy_img, self.new_circle)

    def new_circle(self, event):
        self.coords.append((event.x, event.y, 9))
        self.listbox.destroy()
        self.create_widgets()
        self.show_green_holes(binding=self.new_circle)

    def return_main(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, self.coords)
        frame.tkraise()

class DeletePCBHole(ImageInitializer):
    def __init__(self, container, coords):
        super().__init__(container, coords)
        self.selected_hole_name = None
        self.create_listbox()

    def create_widgets(self):
        self.instructions = tk.Text(self.master, height=2, width=30)
        text='Selecciona y presiona eliminar'
        self.instructions.insert("e", text)
        self.instructions.place(x = 680, y = 10)

        # button
        self.delete_button = ttk.Button(self.container, text='Eliminar')
        self.delete_button.place(x = 700, y = 180)
        self.delete_button.configure(command=self.delete_selected)

        # button
        self.return_button = ttk.Button(self.container, text='Volver')
        self.return_button.place(x = 700, y = 230)
        self.return_button.configure(command=self.return_main)

    def select(self, event):
        # get pin hole
        self.selected_hole_name = self.listbox.curselection()
        self.center = (self.holes[self.selected_hole_name][0], self.holes[self.selected_hole_name][1])
        self.radius = self.holes[self.selected_hole_name][2]
        self.show_green_holes()
        self.colour_selected(self.center, (255,0,255), self.radius)

    def delete_selected(self):
        self.colour_selected(self.center, (255,255,255), self.radius)
        self.holes.pop(self.selected_hole_name)
        self.coords = list(self.holes.values())
        self.create_listbox()

    def create_listbox(self):
        self.langs_var = tk.StringVar(value=[f"Barreno {i}" for i in range(len(self.holes.keys()))])
        self.listbox = tk.Listbox(
            self.container,
            listvariable=self.langs_var,
            height=6)
        self.listbox.place(x = 700, y = 60)
        self.listbox.bind('<<ListboxSelect>>', self.select)
        self.create_widgets()

    def return_main(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, self.coords)
        frame.tkraise()

class ProcessPinHolesCenters():
    def __init__(self, img, raw_coords):
        self.img = img
        self.one_channel, _, _ = cv2.split(self.img)
        self.image_bin_not = cv2.bitwise_not(self.one_channel)
        #self.image_bin_not = cv2.bitwise_not(self.img)
        self.raw_coords = raw_coords
        self.coords_processed = []
        self.get_img_coords()

    def get_img_coords(self):
        for i in range(0, len(self.raw_coords), 4):
            # IMPORTANT: It seems that the coords in the csv are not in the order of x1,y1,x2,y2
            x2, y2 = int(self.raw_coords[i]), int(self.raw_coords[i+1])
            x1, y1 = int(self.raw_coords[i+2]), int(self.raw_coords[i+3])
            half_x = (x2-x1) // 2
            half_y = (y2-y1) // 2
            # Big box to detect the center
            x1 = x1 - half_x if x1 - half_x > 0 else 0
            x2 = x2 + half_x
            y1 = y1 - half_y if y1 - half_y > 0 else 0
            y2 = y2 + half_y
            self.get_sub_image_center(x1,y1,x2,y2)

    def get_sub_image_center(self, x1, y1, x2, y2):
        sub_image = self.image_bin_not[y1:y2, x1:x2]
        sub = self.img[y1:y2, x1:x2, :]
        detected_circles = cv2.HoughCircles(
                                sub_image,
                                cv2.HOUGH_GRADIENT, 1, 40,
                                param1 = 50,
                                param2 = 13,
                                minRadius = 5,
                                maxRadius = 20
                            )

        for pt in detected_circles[0, :]:
            # circle coords
            a, b, r = int(pt[0]), int(pt[1]), int(pt[2])
            new_x1 = x1 + a
            new_y1 = y1 + b
            self.coords_processed.append((new_x1, new_y1, r))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("900x700")
        self.title('BARRENADORA AUTOMATIZADA')
        self.resizable(False, False)

if __name__ == "__main__":
    app = App()
    #PiCameraPhoto(app, "/")
    BinarizingFrame(app)
    app.mainloop()