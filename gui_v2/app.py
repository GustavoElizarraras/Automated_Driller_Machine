import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import Image, ImageTk

class ControlFrame(ttk.LabelFrame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        # self.container = container
        # PCB Image
        self.img = Image.open("gui/12000001_temp.jpg")
        self.render = ImageTk.PhotoImage(self.img)
        self.img_label = ttk.Label(self.master, image=self.render, compound="right")
        self.img_label.place(x = 10, y = 10)

        self.create_widgets()

    def create_widgets(self):

        # button
        self.add_button = ttk.Button(self.master, text='Añadir barreno')
        self.add_button.place(x = 700, y = 10)
        self.add_button.configure(command=self.press_add)

        # button
        self.del_button = ttk.Button(self.master, text='Eliminar barreno')
        self.del_button.place(x = 700, y = 50)
        # self.convert_button.configure(command=self.convert)

        # button
        self.move_button = ttk.Button(self.master, text='Mover barreno')
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

class AddPCBHole(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self.master, text='This is the add frame')
        self.label.place(x = 700, y = 10)

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


