import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageInitializer(ttk.Frame):
    def __init__(self, container, coords):
        super().__init__(container)
        self.container = container
        # PCB Image
        self.img = Image.open("gui/12000001_temp.jpg")
        # image for opencv
        self.img_array = np.asarray(self.img)
        # List of coordinates (dummy for now)
        self.coords = coords
        self.render_img(self.img_array)
    
    def render_img(self, img_array, binding=None):
        for c in self.coords:
            cv2.circle(img=img_array, center = (c[0], c[1]),
                       radius=5, color =(0,255,0), thickness=-1)
        self.render = ImageTk.PhotoImage(Image.fromarray(img_array))
        self.img_label = ttk.Label(self.container, image=self.render, cursor="cross")
        self.img_label.place(x = 0, y = 0)
        self.img_label.bind("<Button-1>", binding)

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
        # self.convert_button.configure(command=self.convert)

        # button
        self.move_button = ttk.Button(self.container, text='Mover barreno')
        self.move_button.place(x = 700, y = 90)
        self.move_button.configure(command=self.press_move)

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

#     def press_del(self):
#         pass

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
            self.coords.append((event.x, event.y))
            self.render_img(self.img_array, self.draw_cross)

    def return_main(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, self.coords)
        frame.tkraise()

class MovePCBHole(ImageInitializer):
    def __init__(self, container, coords):
        super().__init__(container, coords)
        self.holes = { (i,):coord for i, coord in enumerate(coords)}
        self.langs_var = tk.StringVar(value=[f"Barreno {i}" for i in len(self.holes)])
        self.create_widgets()

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
        self.insert_cursor(self.posx, self.posy)
        self.label = ttk.Label(self.master, text=self.selected_hole_name)
        self.label.place(x = 700, y = 130)

    def insert_cursor(self, px, py):
        # button
        self.up = ttk.Button(self.container, text='up')
        self.up.place(x = 700, y = 200)
        self.up.configure(command=self.move_pin_hole("up", px, py))
        # button
        self.down = ttk.Button(self.container, text='down')
        self.down.place(x = 700, y = 240)
        # self.down.configure(command=self.press_add)
        # button
        self.left = ttk.Button(self.container, text='left')
        self.left.place(x = 700, y = 280)
        # self.left.configure(command=self.press_add)
        # button
        self.right = ttk.Button(self.container, text='right')
        self.right.place(x = 700, y = 320)
        # self.right.configure(command=self.press_add)
    
    def move_pin_hole(self,direction, x, y):
        if direction == "up":
            y += 20
        
        cv2.circle(img=self.img_array, center = (x, y),
                   radius=5, color =(255,255,0), thickness=-1)
        self.render_img(self.img_array)


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

if __name__ == "__main__":
    coords = [(100,100), (320,300)]
    app = App()
    ControlFrame(app, coords)
    app.mainloop()


