from tflite_runtime.interpreter import Interpreter
from skimage.filters import unsharp_mask
from picamera import PiCamera
import motor_controller as mc
import tkinter as tk
from tkinter import ttk
from functools import partial
from PIL import Image, ImageTk
import numpy as np
import cv2
import os
import glob
import time
import re

class PiCameraPhoto():
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (2592, 1944)
        self.dir = "/home/pi/Documents/pcb_images/"

    def take_photo(self):
        new_img_path = self.get_new_path()
        self.camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        self.camera.capture(new_img_path)
        self.camera.stop_preview()
        time.sleep(0.5)

    def get_last_img_dir(self):
        list_of_files = glob.glob(self.dir + "*.jpg")
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    def get_img_name(self, img_path_name):
        last_img = img_path_name[-11:-1]
        last_img_num = re.findall(r'\d+', last_img)
        img_name = "img_" + str(int(last_img_num[-1]) + 1) + ".jpg"
        return img_name

    def get_new_path(self):
        last_img_path = self.get_last_img_dir()
        img_name = self.get_img_name(last_img_path)
        new_img_path = self.dir + img_name
        return new_img_path

class ImagePreprocessing():
    def __init__(self, img_path):
        self.img_path = img_path
        self.img_array = cv2.imread(img_path, 0)

    def crop_rotate(self, img, crops_coords=None, angle=0):
        if crops_coords:
            y1, y2, x1, x2 = crops_coords
            img = img[y1: y2, x1: x2]
        image_center = tuple(np.array(img.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        img = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
        return img

    def crop_resize_home(self):
        img_home = self.crop_rotate(self.img_array, (700,1660,550,1540), -2.75)
        img_home = self.crop_rotate(img_home, None, 180)
        img_home = cv2.resize(img_home, (640, 640), interpolation= cv2.INTER_LINEAR)
        return img_home

    def do_multiple_images(self):
        _, img_array = cv2.threshold(self.img_array, 230, 255, cv2.THRESH_BINARY)
        ym = img_array.shape[0] // 3
        xm = img_array.shape[1] // 3
        imgs = []
        for j in range(1,4):
            for i in range(1,4):
                sub_img = img_array[(j-1)*ym: (j*ym), (i-1)*xm: i*xm]
                sub_img = cv2.resize(sub_img, (640, 640), interpolation= cv2.INTER_LINEAR)
                # if the binary image has the pin holes color black, invert it:
                # sub_img = cv2.bitwise_not(sub_img)
                sub_img = cv2.medianBlur(sub_img, 5)
                sub_img = unsharp_mask(sub_img, radius=5, amount=11)
                sub_img *= 255
                np.floor(sub_img)
                sub_img = sub_img.astype(np.float32)
                imgs.append(np.expand_dims(sub_img, axis=-1))
        return imgs

class CalculateWidth(ttk.Frame):
    def __init__(self, container):
        """
        This class implements the following behaviour in the machine:
            1.- Move table to user
            2.- User puts the circuit board
            3.- User press button to grab the PCB
                3.1.1 .- Gets the width of the table using computer vision
            4.- Grab the PCB
            5.- Table down
            6.- Be able to grab it harder or release it
            7.- Display control frame while going home
        """
        super().__init__(container)
        self.img_array = None
        self.container = container
        self.create_widgets()
        motor_controller.go_default_position()
        time.sleep(1)
        motor_controller.move_y_to_user()
        # table up
        motor_controller.move_motor(295, False, "table")

    def create_widgets(self):
        # release or grab harder methods
        self.release = partial(self.adjust_grab, "release")
        self.grab_harder = partial(self.adjust_grab, "harder")

        self.instructions = tk.Text(self.container, height=1, width=65, font=('Times New Roman', 15))
        text = 'Coloque la placa en el centro de la mesa y presione el botón "Sujetar PCB"'
        self.instructions.insert("e", text)
        self.instructions.place(x = 160, y = 100)
        # grab button
        self.grab_button = ttk.Button(self.container, text='Sujetar PCB', style='Accent.TButton')
        self.grab_button.place(x = 415, y = 150)
        self.grab_button.configure(command=self.do_sequence)
        # grab harder button
        self.harder_button = ttk.Button(self.container, text='Incrementar presión', style='Accent.TButton')
        self.harder_button.place(x = 390, y = 200)
        self.harder_button.configure(command=self.grab_harder)
        # release grabber button
        self.release_button = ttk.Button(self.container, text='Liberar presión', style='Accent.TButton')
        self.release_button.place(x = 405, y = 250)
        self.release_button.configure(command=self.release)
        # Go to Controller Frame
        self.next_button = ttk.Button(self.container, text='Detectar barrenos', style='Accent.TButton')
        self.next_button.place(x = 396, y = 400)
        self.next_button.configure(command=self.display_control_panel_panel)

    def get_pcb_width(self):
        _, self.img_array = cv2.threshold(self.img_array, 210 , 255, cv2.THRESH_BINARY)
        self.img_array = cv2.erode(self.img_array, (41,41), iterations = 1)
        canny = cv2.Canny(self.img_array, 100, 255, 1)
        lines = cv2.HoughLinesP(
                    canny, # Input edge image
                    2, # Distance resolution in pixels
                    np.pi/180, # Angle resolution in radians
                    threshold=200, # Min number of votes for valid line
                    minLineLength=50, # Min allowed length of line
                    maxLineGap=100 # Max allowed gap between line for joining them
                    )
        xmax = 0
        xmin = 1000
        # Iterate over points
        for points in lines:
            # Extracted points nested in the list
            x1, _, x2, _ = points[0]
            if x1 < xmin:
                xmin = x1
            if x2 > xmax:
                xmax = x2
        return x2 - x1

    def do_sequence(self):
        pi_camera.take_photo()
        img_path = pi_camera.get_last_img_dir()
        grab_processing = ImagePreprocessing(img_path)
        img_ = grab_processing.img_array
        self.img_array = grab_processing.crop_rotate(img_, (0,1025,500,1525), -2.75)
        self.img_array = cv2.resize(self.img_array, (640, 640), interpolation= cv2.INTER_LINEAR)
        width_px = self.get_pcb_width()
        pulses = motor_controller.convert_pixels_utils(width_px, "pistons")
        if pulses > 700:
            pulses = 700
        motor_controller.set_grabber(pulses, grab=True)

    def adjust_grab(self, grab):
        if grab == "release":
            # 0.5 mm
            motor_controller.move_motor(25, True, "pistons")
        else:
            motor_controller.move_motor(25, False, "pistons")

    def display_control_panel_panel(self):
        # table down
        motor_controller.move_motor(300, True, "table")
        time.sleep(0.5)
        motor_controller.go_home()
        pi_camera.take_photo()
        img_home_path = pi_camera.get_last_img_dir()
        image_home = ImageInitializer(img_home_path)
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, image_home.coords)
        frame.tkraise()

class ImageInitializer():
    def __init__(self, img_path, manual=False):
        # PCB Image
        self.img_path = img_path
        if not manual:
            # Processing and saving the img in home position first time
            self.save_processed_home_img()
        img_processed_home_path = pi_camera.get_last_img_dir()
        self.prep_img_home = ImagePreprocessing(img_processed_home_path)
        # getting 9 zoomed imgs from the photo taken in home
        self.imgs_array = self.prep_img_home.do_multiple_images()
        # calling the tensorflow lite interpreter on those 9 images
        self.pin_holes = ProcessPinHolesCenters(self.imgs_array)
        # getting the precise centers of the detected pin holes
        self.coords = self.pin_holes.coords_processed

    def save_processed_home_img(self):
        img_home_gui = ImagePreprocessing(self.img_path).crop_resize_home()
        # Binarizing
        _, img_home_gui = cv2.threshold(img_home_gui, 215, 255, cv2.THRESH_BINARY)
        img_home_gui = cv2.bitwise_not(img_home_gui)
        # # _, img_home_gui = cv2.threshold(img_home_gui, 215, 255, cv2.THRESH_BINARY)
        img_home_gui = img_home_gui.astype(np.uint8)
        # Saving in a new path for the GUI to display easier
        img_gui_path = pi_camera.get_new_path()
        cv2.imwrite(img_gui_path, img_home_gui)

class ImageUtilsFrame(ttk.Frame):
    def __init__(self, container, coords):
        super().__init__(container)
        self.container = container

        self.img_path = pi_camera.get_last_img_dir()
        # PCB Image
        # binarized image of the pcb that takes the camera
        self.img_array = cv2.imread(self.img_path, 0)
        #self.img_array = cv2.imread("gui_v2/img_212.jpg", 0)
        self.img_array = cv2.merge([self.img_array, self.img_array, self.img_array])
        self.coords = coords
        # pin-holes identifiers
        self.holes = { (i,):coord for i, coord in enumerate(self.coords)}
        self.show_red_centers()

    def render_img(self, img_array, binding=None):
        self.render = ImageTk.PhotoImage(Image.fromarray(img_array))
        self.img_label = ttk.Label(self.container, image=self.render, cursor="cross")
        self.img_label.place(x = 0, y = 0)
        self.img_label.bind("<Button-1>", binding)

    def show_red_centers(self, binding=None):
        for coord in self.coords:
            center = (coord[0], coord[1])
            color = (255,0,0)
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
            cv2.putText(self.img_array, f"B{num[0]}", (coord[0]-10, coord[1]-11), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,135,160), 1)

class ControlFrame(ImageUtilsFrame):
    def __init__(self, container, coords):
        super().__init__(container, coords)
        self.create_widgets()

    def create_widgets(self):

        # button
        self.del_button = ttk.Button(self.container, text='Binarizar manualmente', style='Accent.TButton')
        self.del_button.place(x = 720, y = 100)
        self.del_button.configure(command=self.show_bin_frame)

        # button
        self.move_button = ttk.Button(self.container, text='Añadir o Mover barreno', style='Accent.TButton')
        self.move_button.place(x = 700, y = 200)
        self.move_button.configure(command=self.press_move_add)

        # button
        self.del_button = ttk.Button(self.container, text='Eliminar barreno', style='Accent.TButton')
        self.del_button.place(x = 724, y = 250)
        self.del_button.configure(command=self.press_delete)

        # button
        self.start_button = ttk.Button(self.container, text='Iniciar barrenado', style='Accent.TButton')
        self.start_button.place(x = 723, y = 400)
        self.start_button.configure(command=self.do_drilling_sequence)

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

    def show_bin_frame(self):
        self.clear_frame()
        frame = BinarizingFrame(self.container)
        frame.tkraise()

    def do_drilling_sequence(self):
        motor_controller.move_motor(1, True, "driller")
        for coord in self.coords:
            motor_controller.move_motor(1, True, "driller")
            x, y, _ = coord
            x_pos, y_pos = motor_controller.convert_pixels_utils((x,y), "x")
            motor_controller.move_x_y(x_pos, y_pos)
            motor_controller.drill()
            time.sleep(0.05)
        # stop driller
        motor_controller.move_motor(1, False, "driller")
        time.sleep(0.5)
        # move Y to user
        motor_controller.move_y_to_user()
        time.sleep(0.5)
        # table up
        motor_controller.move_motor(300, False, "table")
        time.sleep(0.5)
        # return pistons to original position
        motor_controller.move_motor(60, True, "pistons")
        time.sleep(0.5)
        #table down
        motor_controller.move_motor(300, True, "table")


class AddMovePCBHole(ImageUtilsFrame):
    def __init__(self, container, coords):
        super().__init__(container, coords)
        self.posx, self.posy = None, None
        self.selected_hole_name = None
        self.dummy_img = self.img_array
        self.img_label.bind("<Button-1>", self.new_circle)
        self.create_widgets()
        self.insert_cursor()

    def create_widgets(self):
        self.instructions = tk.Text(self.master, height=5, width=25, font=('Times New Roman', 13))
        text='Para añadir un barreno da click \nsobre la imagen, para mover un \nbarreno, seleccionalo y \npresiona los botones \ncorrespondientes'
        self.instructions.insert("e", text)
        self.instructions.place(x = 660, y = 10)

        self.holes = { (i,):coord for i, coord in enumerate(self.coords)}
        self.langs_var = tk.StringVar(value=[f"Barreno {i}" for i in range(len(self.holes.keys()))])
        self.listbox = tk.Listbox(
            self.container,
            listvariable=self.langs_var,
            height=6)
        self.listbox.place(x = 660, y = 130)
        self.listbox.bind('<<ListboxSelect>>', self.move_selected)

        # button
        self.return_button = ttk.Button(self.container, text='Volver')
        self.return_button.place(x = 660, y = 450)
        self.return_button.configure(command=self.return_main)

    def move_selected(self, event):
        # get pin hole
        self.selected_hole_name = self.listbox.curselection()
        self.posx, self.posy = self.holes[self.selected_hole_name][0], self.holes[self.selected_hole_name][1]
        self.radius = self.holes[self.selected_hole_name][2]
        self.show_red_centers()
        self.colour_selected((self.posx, self.posy), (255,227,51), self.radius)
        #self.holes.pop(self.selected_hole_name)

    def insert_cursor(self):
        # move methods
        self.move_up = partial(self.move_pin_hole, "up")
        self.move_down = partial(self.move_pin_hole, "down")
        self.move_left = partial(self.move_pin_hole, "left")
        self.move_right = partial(self.move_pin_hole, "right")
        # buttons
        self.button_up = ttk.Button(self.container, text='arriba', command=self.move_up, style='Accent.TButton')
        self.button_up.place(x = 660, y = 280)

        self.button_down = ttk.Button(self.container, text='abajo', command=self.move_down, style='Accent.TButton')
        self.button_down.place(x = 660, y = 320)

        self.button_left = ttk.Button(self.container, text='izquierda', command=self.move_left, style='Accent.TButton')
        self.button_left.place(x = 660, y = 360)

        self.button_right = ttk.Button(self.container, text='derecha', command=self.move_right, style='Accent.TButton')
        self.button_right.place(x = 660, y = 400)

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
        self.show_red_centers(binding=self.new_circle)

    def return_main(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, self.coords)
        frame.tkraise()

class DeletePCBHole(ImageUtilsFrame):
    def __init__(self, container, coords):
        super().__init__(container, coords)
        self.selected_hole_name = None
        self.create_listbox()

    def create_widgets(self):
        self.instructions = tk.Text(self.master, height=2, width=25, font=('Times New Roman', 13))
        text='Selecciona y presiona eliminar'
        self.instructions.insert("e", text)
        self.instructions.place(x = 660, y = 10)

        # button
        self.delete_button = ttk.Button(self.container, text='Eliminar', style='Accent.TButton')
        self.delete_button.place(x = 660, y = 200)
        self.delete_button.configure(command=self.delete_selected)

        # button
        self.return_button = ttk.Button(self.container, text='Volver')
        self.return_button.place(x = 660, y = 250)
        self.return_button.configure(command=self.return_main)

    def select(self, event):
        # get pin hole
        self.selected_hole_name = self.listbox.curselection()
        self.center = (self.holes[self.selected_hole_name][0], self.holes[self.selected_hole_name][1])
        self.radius = self.holes[self.selected_hole_name][2]
        self.show_red_centers()
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
        self.listbox.place(x = 660, y = 60)
        self.listbox.bind('<<ListboxSelect>>', self.select)
        self.create_widgets()

    def return_main(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, self.coords)
        frame.tkraise()

class BinarizingFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        pi_camera.take_photo()
        self.img_path = pi_camera.get_last_img_dir()
        self.img_array = ImagePreprocessing(self.img_path).crop_resize_home()
        self.gray_img = self.img_array.copy()
        self.create_widgets()

    def render_img(self, img_array):
        self.render = ImageTk.PhotoImage(Image.fromarray(img_array))
        self.img_label = ttk.Label(self.container, image=self.render, cursor="cross")
        self.img_label.place(x = 0, y = 0)

    def create_widgets(self):

        self.instructions = tk.Text(self.master, height=5, width=25, font=('Times New Roman', 13))
        text='Entre mas definidos se \nvean los barrenos, hay más \nprobabilidades que la \nred neuronal los detecte'
        self.instructions.insert("e", text)
        self.instructions.place(x = 660, y = 10)

        self.instructions2 = tk.Text(self.master, height=1, width=25, font=('Times New Roman', 12))
        text2 = "Umbral inferior para binarizar"
        self.instructions2.insert("e", text2)
        self.instructions2.place(x = 660, y = 150)

        self.slider1 = ttk.Scale(self.container, from_=127, to=255, orient="horizontal", style="Horizontal.Tick.TScale", length=150)
        self.slider1.bind("<ButtonRelease-1>", self.binarize)
        self.slider1.place(x=700, y=175)

        self.instructions3 = tk.Text(self.master, height=1, width=25, font=('Times New Roman', 12))
        text3 = "Hacer más definidos a los barrenos:"
        self.instructions3.insert("e", text3)
        self.instructions3.place(x = 660, y = 225)

        self.slider3 = tk.Scale(self.container, from_=1, to=5, orient="horizontal")
        self.slider3.bind("<ButtonRelease-1>", self.erode)
        self.slider3.place(x=700, y=250)

        # button
        self.continue_button = ttk.Button(self.container, text='Volver a detectar barrenos')
        self.continue_button.place(x = 700, y = 300)
        self.continue_button.configure(command=self.display_control_panel)

    def binarize(self, event):
        threshold_low = self.slider1.get()
        _, self.gray_img = cv2.threshold(self.img_array, threshold_low , 255, cv2.THRESH_BINARY)
        self.render_img(self.gray_img)

    def erode(self, event):
        k = self.slider3.get()
        kernel = np.ones((k,k), np.uint8)
        new_image = cv2.erode(self.gray_img, kernel, iterations = 1)
        self.render_img(new_image)

    def save_manual_img(self):
        self.gray_img = cv2.bitwise_not(self.gray_img)
        self.gray_img = self.gray_img.astype(np.uint8)
        # Saving in a new path for the GUI to display easier
        img_gui_path = pi_camera.get_new_path()
        cv2.imwrite(img_gui_path, self.gray_img)

    def display_control_panel(self):
        self.save_manual_img()
        img_home_path = pi_camera.get_last_img_dir()
        image_home = ImageInitializer(img_home_path, manual=True)
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, image_home.coords)
        frame.tkraise()

class ProcessPinHolesCenters():
    def __init__(self, imgs):
        self.imgs = imgs
        self.predictions = []
        self.coords_processed = []
        self.predict_cnn()
        self.transform_predictions_to_coords()

    def predict_cnn(self):
        self.model_path = "./fixed_data.tflite"
        self.interpreter = Interpreter(self.model_path)
        self.interpreter.allocate_tensors()

        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        for sub_img in self.imgs:
            self.interpreter.set_tensor(input_details[0]['index'], np.expand_dims(sub_img, axis=0))
            self.interpreter.invoke()
            self.predictions.append(self.interpreter.get_tensor(output_details[0]['index']))

    def transform_predictions_to_coords(self):
        threshold = 0.6
        GRID_SIZE = 8
        for i in range(1,10):
            for mx in range(80):
                for my in range(80):
                    channels = self.predictions[i-1][0][my][mx]
                    prob, x1, y1, x2, y2 = channels

                    if prob < threshold:
                        continue

                    px1, py1 = int((mx * GRID_SIZE) + x1), int((my * GRID_SIZE) + y1)
                    px2, py2 = int((mx * GRID_SIZE) + x2), int((my * GRID_SIZE) + y2)

                    cx, cy, r = self.get_sub_image_center(self.imgs[i-1], px1, py1, px2, py2)

                    if cx == -1:
                        continue
                    #cx, cy = ((mx * GRID_SIZE) + cx) // 3, ((my * GRID_SIZE) + cy) // 3
                    cx = cx // 3
                    cy = cy // 3
                    if i == 2:
                        cx += 213
                        cy += 1
                    if i == 3:
                        cx += 426
                        cy += 1
                    if i == 4:
                        cy += 213
                    if i == 5:
                        cy += 213
                        cx += 213
                    if i == 6:
                        cx += 426
                        cy += 213
                    if i == 7:
                        cy += 426
                    if i == 8:
                        cx += 213
                        cy += 426
                    if i == 9:
                        cx += 426
                        cy += 426

                    self.coords_processed.append((cx, cy, r))

    def get_sub_image_center(self, img, x1, y1, x2, y2):
        sub_image = img[y1:y2, x1:x2]
        sub_image = sub_image.astype(np.uint8)
        try:
            detected_circles = cv2.HoughCircles(
                                    sub_image,
                                    cv2.HOUGH_GRADIENT, 1, 40,
                                    param1 = 50,
                                    param2 = 1,
                                    minRadius = 5,
                                    maxRadius = 9
                            )
        except:
            return (-1, -1, -1)

        try:
            for pt in detected_circles[0, :]:
                # circle coords
                a, b, r = int(pt[0]), int(pt[1]), int(pt[2])
                new_x1 = x1 + a
                new_y1 = y1 + b
                return (new_x1, new_y1, r)
        except:
            return (-1, -1, -1)
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("900x650")
        self.title('BARRENADORA AUTOMATIZADA')
        self.resizable(False, False)

if __name__ == "__main__":

    #motor_controller = mc.MotorController()
    #pi_camera = PiCameraPhoto()
    app = App()
    app.tk.call("source", "gui_v2/azure.tcl")
    app.tk.call("set_theme", "light")
    CalculateWidth(app)
    app.mainloop()