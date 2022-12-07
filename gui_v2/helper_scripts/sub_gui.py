import tkinter as tk
from tkinter import ttk
from functools import partial
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import csv

class ImageInitializer(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container

        self.reader_img_csv = BetterLabeling("dataset/scrapped_locations.csv")
        self.row_reader = self.reader_img_csv.get_next_line()
        self.row = next(self.row_reader)
        # PCB Image
        self.img_path = None
        # self.img = Image.open(self.img_path)
        self.img = None
        # image for opencv
        # self.img_array = np.asarray(self.img)
        self.img_array = None
        # List of coordinates (dummy for now)
        # self.coords = coords
        self.coords = []
        self.get_img_coords()
        self.show_green_holes()

    def render_img(self, img_array, binding=None):
        self.render = ImageTk.PhotoImage(Image.fromarray(img_array))
        self.img_label = ttk.Label(self.container, image=self.render, cursor="cross")
        self.img_label.place(x = 0, y = 0)
        self.img_label.bind("<Button-1>", binding)

    def show_green_holes(self):
        for c in self.coords:
            center = c[0]
            radius = c[1]
            cv2.circle(self.img_array, center,
                       radius, (0,255,0), 3)
        self.render_img(self.img_array)

    def colour_selected(self, x, y, color):
        cv2.circle(img=self.img_array, center = (x,y),
                   radius=5, color=color, thickness=-1)
        self.render_img(self.img_array)

    def get_img_coords(self):
        self.img_path =  os.getcwd() + "/dataset/pcb_gimp_morph/" + self.row[0]
        self.img = Image.open(self.img_path)
        self.img_array = cv2.merge([np.asarray(self.img), np.asarray(self.img), np.asarray(self.img)])
        # pcb = cv2.imread(img)
        #centers = []
        self.coords = []
        for i in range(1, len(self.row), 4):
            x1, y1 = int(self.row[i]), int(self.row[i+1])
            x2, y2 = int(self.row[i+2]), int(self.row[i+3])
            half_x = (x2-x1) // 2
            half_y = (y1-y2) // 2
            #centers.append(((x2-x1)/2, (y2-y1)/2))

            #cv2.circle(pcb, (x1 + half_x, y1 - half_y), int((y1-y2)/2), (0, 255, 0), 2)
            self.coords.append(((x1 + half_x, y1 - half_y), int((y1-y2)/2)))
class ControlFrame(ImageInitializer):
    def __init__(self, container):
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):

        # button
        self.add_button = ttk.Button(self.container, text='Añadir barreno')
        self.add_button.place(x = 700, y = 10)
        self.add_button.configure(command=self.press_add)

        # button
        self.del_button = ttk.Button(self.container, text='Eliminar barreno')
        self.del_button.place(x = 700, y = 50)
        self.del_button.configure(command=self.press_delete)

        # button
        self.move_button = ttk.Button(self.container, text='Mover barreno')
        self.move_button.place(x = 700, y = 90)
        self.move_button.configure(command=self.press_move)

        # button
        self.save_button = ttk.Button(self.container, text='Guardar')
        self.save_button.place(x = 700, y = 130)
        self.save_button.configure(command=self.save_coords)

        # button
        self.next_img_button = ttk.Button(self.container, text='next img')
        self.next_img_button.place(x = 700, y = 180)
        self.next_img_button.configure(command=self.print_row)

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def press_add(self):
        self.clear_frame()
        frame = AddPCBHole(self.container)
        frame.tkraise()

    def press_move(self):
        self.clear_frame()
        frame = MovePCBHole(self.container, self.coords)
        frame.tkraise()

    def press_delete(self):
        self.clear_frame()
        frame = DeletePCBHole(self.container, self.coords)
        frame.tkraise()

    def save_coords(self):
        pass
    #     with open("dataset/processed_locations/scrapped_good.csv", "a") as file:
    #         coords_writer = csv.writer(file)
    #         coords_writer.writerow(self.)
    def print_row(self):
        self.row = next(self.row_reader)
        self.get_img_coords()
        self.show_green_holes()


class AddPCBHole(ImageInitializer):
    def __init__(self, container):
        super().__init__(container)
        self.img_label.bind("<Button-1>", self.draw_cross)
        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self.master, text='This is the add frame')
        self.label.place(x = 700, y = 10)

        # button
        self.return_button = ttk.Button(self.container, text='Volver')
        self.return_button.place(x = 700, y = 50)
        self.return_button.configure(command=self.return_main)

    def draw_cross(self, event):
            line_thickness = 2
            cv2.line(self.img_array, (event.x - 15, event.y), (event.x + 15, event.y), (0,0,255), thickness=line_thickness)
            cv2.line(self.img_array, (event.x, event.y - 15), (event.x, event.y + 15), (0,0,255), thickness=line_thickness)
            self.img_label.destroy()
            self.coords.append(((event.x, event.y), 2))
            self.render_img(self.img_array, self.draw_cross)

    def return_main(self):
        # for widget in self.container.winfo_children():
        #     widget.destroy()
        # frame = ControlFrame(self.container)
        # frame.tkraise()
        self.show_green_holes()

class MovePCBHole(ImageInitializer):
    def __init__(self, container, coords):
        super().__init__(container, coords)
        self.holes = { (i,):coord for i, coord in enumerate(coords)}
        self.langs_var = tk.StringVar(value=[f"Barreno {i}" for i in range(len(self.holes.keys()))])
        self.posx, self.posy = None, None
        self.selected_hole_name = None
        self.create_widgets()
        self.insert_cursor()

    def create_widgets(self):
        self.label = ttk.Label(self.master, text='This is the move frame')
        self.label.place(x = 700, y = 10)

        self.listbox = tk.Listbox(
            self.container,
            listvariable=self.langs_var,
            height=6)
        self.listbox.place(x = 700, y = 90)
        self.listbox.bind('<<ListboxSelect>>', self.move_selected)

        # button
        self.return_button = ttk.Button(self.container, text='Volver')
        self.return_button.place(x = 700, y = 50)
        self.return_button.configure(command=self.return_main)

    def move_selected(self, event):
        # get pin hole
        self.selected_hole_name = self.listbox.curselection()
        self.posx, self.posy = self.holes[self.selected_hole_name]
        self.holes.pop(self.selected_hole_name)

    def insert_cursor(self):
        # move methods
        self.move_up = partial(self.move_pin_hole, "up")
        self.move_down = partial(self.move_pin_hole, "down")
        self.move_left = partial(self.move_pin_hole, "left")
        self.move_right = partial(self.move_pin_hole, "right")
        # buttons
        self.button_up = ttk.Button(self.container, text='up', command=self.move_up)
        self.button_up.place(x = 700, y = 200)

        self.button_down = ttk.Button(self.container, text='down', command=self.move_down)
        self.button_down.place(x = 700, y = 240)

        self.button_left = ttk.Button(self.container, text='left', command=self.move_left)
        self.button_left.place(x = 700, y = 280)

        self.button_right = ttk.Button(self.container, text='right', command=self.move_right)
        self.button_right.place(x = 700, y = 320)

    def move_pin_hole(self, direction):
        # remove actual circle
        cv2.circle(img=self.img_array, center = (self.posx, self.posy),
                   radius=5, color =(255,255,255), thickness=-1)
        if direction == "up":
            self.posy -= 2
        elif direction == "down":
            self.posy += 2
        elif direction == "left":
            self.posx -= 2
        elif direction == "right":
            self.posx += 2
        # new coordinate and overwrite all the pin-holes coords
        self.holes[self.selected_hole_name] = (self.posx, self.posy)
        self.coords = list(self.holes.values())
        self.render_img(self.img_array)

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
        self.label = ttk.Label(self.master, text='This is the move frame')
        self.label.place(x = 700, y = 10)

        # button
        self.delete_button = ttk.Button(self.container, text='Eliminar')
        self.delete_button.place(x = 700, y = 140)
        self.delete_button.configure(command=self.delete_selected)

        # button
        self.return_button = ttk.Button(self.container, text='Volver')
        self.return_button.place(x = 700, y = 200)
        self.return_button.configure(command=self.return_main)

    def select(self, event):
        # get pin hole
        self.selected_hole_name = self.listbox.curselection()
        self.posx, self.posy = self.holes[self.selected_hole_name]
        self.show_green_holes()
        self.colour_selected(self.posx, self.posy, (255,0,255))

    def delete_selected(self):
        self.colour_selected(self.posx, self.posy, (255,255,255))
        self.holes.pop(self.selected_hole_name)
        self.coords = list(self.holes.values())
        self.create_listbox()

    def create_listbox(self):
        self.holes = { (i,):coord for i, coord in enumerate(self.coords)}
        self.langs_var = tk.StringVar(value=[f"Barreno {i}" for i in range(len(self.holes.keys()))])
        self.listbox = tk.Listbox(
            self.container,
            listvariable=self.langs_var,
            height=6)
        self.listbox.place(x = 700, y = 90)
        self.listbox.bind('<<ListboxSelect>>', self.select)
        self.create_widgets()

    def return_main(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, self.coords)
        frame.tkraise()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("900x700")
        self.title('BARRENADORA AUTOMATIZADA')
        self.resizable(False, False)

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class BetterLabeling():
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.csv_row = self.get_next_line()

    def get_next_line(self):
        with open(self.csv_file) as f:
            reader = csv.reader(f)
            for row in reader:
                yield row

if __name__ == "__main__":
    coords = [(100,100), (320,300)]
    app = App()
    ControlFrame(app)
    app.mainloop()