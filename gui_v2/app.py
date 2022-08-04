import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageInitializer(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        # List of coordinates (dummy for now)
        self.coords = [(100,100), (320,300)]
        # PCB Image
        self.img = Image.open("gui/12000001_temp.jpg")
        # image for opencv
        self.img_array = np.asarray(self.img.copy())
        self.render_img()
    
    def render_img(self):
        self.show_holes_center()
        self.render = ImageTk.PhotoImage(Image.fromarray(self.img_array))
        self.img_label = ttk.Label(self.container, image=self.render, cursor="cross")
        self.img_label.place(x = 0, y = 0)

    def show_holes_center(self):
        for c in self.coords:
            cv2.circle(img=self.img_array, center = (c[0], c[1]),
                       radius=5, color =(0,255,0), thickness=-1)


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
        # self.convert_button.configure(command=self.convert)

        # button
        self.move_button = ttk.Button(self.container, text='Mover barreno')
        self.move_button.place(x = 700, y = 90)
        # self.convert_button.configure(command=self.convert)

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def press_add(self):
        self.clear_frame()
        frame = AddPCBHole(self.container)
        frame.tkraise()

#     def press_del(self):
#         pass

#     def press_move(self):
#         pass

class AddPCBHole(ImageInitializer):
    def __init__(self, container):
        super().__init__(container)
        self.pts = []
        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self.master, text='This is the add frame')
        self.label.place(x = 700, y = 10)
        self.img_label.bind("<Button-1>", self.draw_cross)

    def draw_cross(self, event):
            line_thickness = 2
            cv2.line(self.img_array, (event.x - 15, event.y), (event.x + 15, event.y), (0,0,255), thickness=line_thickness)
            cv2.line(self.img_array, (event.x, event.y - 15), (event.x, event.y + 15), (0,0,255), thickness=line_thickness)
            self.img_label.destroy()
            self.render_img()
            self.coords.append((event.x, event.y))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("900x700")
        self.title('BARRENADORA AUTOMATIZADA')
        self.resizable(False, False)

if __name__ == "__main__":
    app = App()
    ControlFrame(app)
    app.mainloop()


