import tkinter as tk
from tkinter import ttk
from functools import partial
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import csv

class ImageInitializer(ttk.Frame):
    def __init__(self, container, coords):
        super().__init__(container)
        self.container = container

        # TODO: Get the last image name from a folder

        self.img_path = os.getcwd() + "/dataset/useful_handpicked_rot/90100076_temp_3.jpg"
        # PCB Image

        self.img = Image.open(self.img_path)
        # image for opencv
        self.img_array = cv2.merge([np.asarray(self.img), np.asarray(self.img), np.asarray(self.img)])
        #self.img_array = np.asarray(self.img)
        # List of coordinates (dummy for now)
        self.coords = coords
        # pin-holes identifiers
        self.holes = { (i,):coord for i, coord in enumerate(coords)}
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
            color = (0,255,0)
            if radius == 2:
                color = (0,0,255)
            cv2.circle(self.img_array, center, radius, color, 4)
        self.draw_hole_number()
        self.render_img(self.img_array)

    def colour_selected(self, center, color, radius=5):
        cv2.circle(img=self.img_array, center=center,
                   radius=radius, color=color, thickness=4)
        self.render_img(self.img_array)

    def draw_hole_number(self):
        for num, coord in self.holes.items():
            cv2.putText(self.img_array, f"B{num[0]}", (coord[0][0]-10, coord[0][1]-11), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,135,160), 2)


class ControlFrame(ImageInitializer):
    def __init__(self, container, coords):
        super().__init__(container, coords)
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

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def press_add(self):
        self.clear_frame()
        frame = AddPCBHole(self.container, self.coords)
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
        locations = [self.img_path[85:]]
        for c in self.coords:
            a, b = c[0]
            r = c[1]
            x1, x2 = str(a - r), str(a + r)
            y1, y2 = str(b + r), str(b - r)
            locations.append(x1)
            locations.append(y1)
            locations.append(x2)
            locations.append(y2)
        with open("dataset/processed_locations/hand_picked_better.csv", "a") as file:
            coords_writer = csv.writer(file)
            coords_writer.writerow(locations)


class AddPCBHole(ImageInitializer):
    def __init__(self, container, coords):
        super().__init__(container, coords)
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
            self.coords.append(((event.x, event.y), 9))
            self.render_img(self.img_array, self.draw_cross)

    def return_main(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, self.coords)
        frame.tkraise()

class MovePCBHole(ImageInitializer):
    def __init__(self, container, coords):
        super().__init__(container, coords)
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
        self.posx, self.posy = self.holes[self.selected_hole_name][0]
        self.radius = self.holes[self.selected_hole_name][1]
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
                   radius=1, color =(255,27,51), thickness=-1)
        if direction == "up":
            self.posy -= 1
        elif direction == "down":
            self.posy += 1
        elif direction == "left":
            self.posx -= 1
        elif direction == "right":
            self.posx += 1
        # new coordinate and overwrite all the pin-holes coords
        self.holes[self.selected_hole_name] = ((self.posx, self.posy), self.radius)
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
        self.label = ttk.Label(self.master, text='This is the delete frame')
        self.label.place(x = 700, y = 10)

        # button
        self.delete_button = ttk.Button(self.container, text='Eliminar')
        self.delete_button.place(x = 700, y = 300)
        self.delete_button.configure(command=self.delete_selected)

        # button
        self.return_button = ttk.Button(self.container, text='Volver')
        self.return_button.place(x = 700, y = 350)
        self.return_button.configure(command=self.return_main)

    def select(self, event):
        # get pin hole
        self.selected_hole_name = self.listbox.curselection()
        self.center = self.holes[self.selected_hole_name][0]
        self.radius = self.holes[self.selected_hole_name][1]
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
        self.listbox.place(x = 700, y = 90)
        self.listbox.bind('<<ListboxSelect>>', self.select)
        self.create_widgets()

    def return_main(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, self.coords)
        frame.tkraise()

class ParseCoords():
    def __init__(self, coords):
        self.coords = coords
        self.coords_processed = []
        self.get_img_coords()

    def get_img_coords(self):
        for i in range(0, len(self.coords), 4):
            x1, y1 = int(self.coords[i]), int(self.coords[i+1])
            x2, y2 = int(self.coords[i+2]), int(self.coords[i+3])
            half_x = (x2-x1) // 2
            half_y = (y1-y2) // 2
            self.coords_processed.append(((x1 + half_x, y1 - half_y), abs(int((y1-y2)/2))))

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

if __name__ == "__main__":
    coords = ParseCoords([35,605,17,623,66,583,48,601,153,604,135,621,53,552,35,570,53,512,35,530,145,536,127,554,157,505,139,524,64,451,46,469,35,427,17,445,71,191,53,209,96,168,78,186,145,102,127,120,478,237,460,255,423,581,405,599])
    app = App()
    ControlFrame(app, coords.coords_processed)
    app.mainloop()