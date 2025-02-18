# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 23:10:49 2025

@author: Beryl
"""
import tkinter as tk
import mne
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

image_files = ["image_1.jpg", "image_2.jpg", "image_3.jpg", "image_4.jpg"]

def center_window(window, width=500, height=500):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_frame(frame_func, *args):
    for widget in window.winfo_children():
        widget.destroy()
    frame_func(*args)

def main_menu():
    frame = tk.Frame(window)
    frame.pack(pady=20)

    tk.Label(frame, text="Main Menu", font=("Arial", 32)).pack(pady=10)

    btn_gallery = tk.Button(frame, text="Display Image Gallery", width=20, command=lambda: show_frame(show_gallery))
    btn_gallery.pack(pady=5)

    btn_graph = tk.Button(frame, text="Display Graph", width=20, command=lambda: show_frame(show_graph))
    btn_graph.pack(pady=5)

    btn_option3 = tk.Button(frame, text="Option 3", width=20, command=lambda: show_frame(option_three))
    btn_option3.pack(pady=5)

    btn_quit = tk.Button(frame, text="Quit", width=20, command=window.destroy)
    btn_quit.pack(pady=5)

def show_gallery():
    frame = tk.Frame(window)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Image Gallery", font=("Arial", 20)).pack(pady=10)


    for img_file in image_files:
        img = Image.open(img_file)
        img = img.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)

        btn = tk.Button(frame, image=img_tk, command=lambda f=img_file: show_frame(show_single_image, f))
        btn.image = img_tk 
        btn.pack(pady=5)

    tk.Button(frame, text="Back to Main Menu", command=lambda: show_frame(main_menu)).pack(pady=10)

def show_single_image(image_path):
    frame = tk.Frame(window)
    frame.pack(pady=20)

    tk.Label(frame, text="Image Viewer", font=("Arial", 20)).pack(pady=10)

    img = Image.open(image_path)
    img = img.resize((350, 350))
    img_tk = ImageTk.PhotoImage(img)

    label = tk.Label(frame, image=img_tk)
    label.image = img_tk
    label.pack()

    tk.Button(frame, text="Back to Gallery", command=lambda: show_frame(show_gallery)).pack(pady=10)

def show_graph():
    frame = tk.Frame(window)
    frame.pack(pady=20)

    tk.Label(frame, text="Graph Display", font=("Arial", 14)).pack(pady=10)

    fig, ax = plt.subplots(figsize=(3, 3), dpi=100)
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_title('Sample Graph')

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

    tk.Button(frame, text="Back to Main Menu", command=lambda: show_frame(main_menu)).pack(pady=10)

def option_three():
    frame = tk.Frame(window)
    frame.pack(pady=20)

    tk.Label(frame, text="Option 3 Selected", font=("Arial", 14)).pack(pady=10)

    tk.Button(frame, text="Back to Main Menu", command=lambda: show_frame(main_menu)).pack(pady=10)

window = tk.Tk()
window.title("Image Gallery")
window.geometry("700x500")
center_window(window, 700, 500)

main_menu()

window.mainloop()
