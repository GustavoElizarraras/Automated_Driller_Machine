
class BinarizingFrame(ttk.Frame):
    def __init__(self, container, img_name):
        super().__init__(container)
        self.container = container
        self.img_name = img_name
        # Hardcoded path, to remove later
        #self.img_path = os.getcwd() + "/dataset/useful_handpicked_rot/12300111_temp_2.jpg"
        self.img_path = "/home/pi/Documents/pcb_images/" + self.img_name

        # gray image of the pcb that takes the camera
        self.gray_img = cv2.imread(self.img_path, 0)
        image_center = tuple(np.array(self.gray_img.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, -3.4, 1.0)
        self.gray_img = cv2.warpAffine(self.gray_img, rot_mat, self.gray_img.shape[1::-1], flags=cv2.INTER_LINEAR)
        self.gray_img = self.gray_img[515:1465, 600:1550]
        self.gray_img = cv2.resize(self.gray_img, (640, 640), interpolation= cv2.INTER_LINEAR)
        self.render_img(self.gray_img)
        self.create_widgets()

    def render_img(self, img_array):
        self.render = ImageTk.PhotoImage(Image.fromarray(img_array))
        self.img_label = ttk.Label(self.container, image=self.render, cursor="cross")
        self.img_label.place(x = 0, y = 0)

    def create_widgets(self):

        self.slider1 = tk.Scale(self.container, from_=0, to=255, orient="horizontal")
        self.slider1.bind("<ButtonRelease-1>", self.binarize)
        self.slider1.place(x=700, y=50)

        self.slider1_2 = tk.Scale(self.container, from_=0, to=255, orient="horizontal")
        self.slider1_2.bind("<ButtonRelease-1>", self.binarize)
        self.slider1_2.place(x=700, y=100)

        self.slider2 = tk.Scale(self.container, from_=0, to=5, orient="horizontal")
        self.slider2.bind("<ButtonRelease-1>", self.dilate)
        self.slider2.place(x=700, y=150)

        self.slider3 = tk.Scale(self.container, from_=0, to=5, orient="horizontal")
        self.slider3.bind("<ButtonRelease-1>", self.erode)
        self.slider3.place(x=700, y=200)

        # button
        self.continue_button = ttk.Button(self.container, text='Detectar barrenos')
        self.continue_button.place(x = 700, y = 10)
        self.continue_button.configure(command=self.display_control_panel)

    def binarize(self, event):
        threshold_low = self.slider1.get()
        threshold_high = self.slider1_2.get()
        _, new_image = cv2.threshold(self.gray_img, threshold_low , threshold_high, cv2.THRESH_BINARY)
        self.render_img(new_image)

    def dilate(self, event):
        k = self.slider2.get()
        kernel = np.ones((k,k), np.uint8)
        new_image = cv2.dilate(self.gray_img, kernel, iterations = 1)
        self.render_img(new_image)

    def erode(self, event):
        k = self.slider3.get()
        kernel = np.ones((k,k), np.uint8)
        new_image = cv2.erode(self.gray_img, kernel, iterations = 1)
        self.render_img(new_image)

    def display_control_panel(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = ControlFrame(self.container, [])
        frame.tkraise()