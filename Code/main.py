# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 12:01:33 2025

@author: Beryl
"""
import tkinter as tk
import numpy as np
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import brainwave_decoder 
import art_generator

def get_art(normalized_powers, mentals=(.2, .2, .2, .2, .2)):    
    combined_powers = (normalized_powers[:, 2] + normalized_powers[:, 3]) / 2
    scaled_powers = combined_powers**1.5

    if(mentals[0] + mentals[1] > mentals[2] + mentals[3] and mentals[0] + mentals[1] > mentals[4]):
        colormap = plt.cm.viridis
    elif(mentals[2] + mentals[3] > mentals[4]):
        colormap = plt.cm.plasma
    else:
        colormap = plt.cm.inferno

    vmin = np.min(scaled_powers)
    vmax = np.max(scaled_powers)
    scaled_powers = (scaled_powers - vmin) / (vmax - vmin)

    colors = []
    for i, power in enumerate(scaled_powers):
        color = colormap(power)
        colors.append(color)

    avg_scaled_power = normalized_powers.mean()
    
    wave_intensity = mentals[2] * .05 + mentals[3] + mentals[4] * 1.5
    
    num_lines = int(150 + 100 * avg_scaled_power)
    line_width, line_alpha = art_generator.stabilize_line_parameters(num_lines)

    fig = art_generator.generate_brain_art(
        num_lines=num_lines,
        color_palette=colors,
        line_alpha=line_alpha,
        line_width=line_width,
        wave_intensity=wave_intensity
        )
    return fig

def get_new_art(arousal, valence):
    colours = []
    for i in range(len(arousal)):
        if arousal[i] > 0.5:
            if valence[i] > 0:
                color = plt.cm.viridis(arousal[i] + .2)
                colours.append(color)
            else:
                color = plt.cm.inferno(arousal[i] + valence[i])
                colours.append(color)

        else:
            color = plt.cm.viridis(valence[i]*2)
            colours.append(color)
            
    smoothness=(np.mean(valence)*50)**4

    if smoothness > 500:
        smoothness = 500

    fig = art_generator.generate_brain_art(
        smoothness=smoothness,
        wave_intensity=np.mean(arousal),
        num_nodes=round(np.mean(arousal) * 100),
        color_palette = colours,
        num_lines=300,
        line_tightness=0.05, 
        line_alpha=1,
        line_width=2
    )
    return fig

def create_gui():
    def open_file_and_generate_art():
        file_path = filedialog.askopenfilename(title="Select EEG File", filetypes=[("MAT files", "*.mat")])
        if file_path:
            # Clear previous plot
            for widget in plot_frame.winfo_children():
                widget.destroy()

            #raw_clean, sfreq = load_and_preprocess_data(file_path)
            #normalized_powers = compute_band_powers(raw_clean, sfreq)
            #mental_state_description, percentages = describe_mental_state(normalized_powers)
            #fig = get_art(normalized_powers, percentages)
            
            raw_clean, sfreq = brainwave_decoder.extract_only_rel_channels(file_path)
            tenths = brainwave_decoder.split_data(raw_clean, sfreq)
            ar, va = brainwave_decoder.return_averages(tenths, sfreq)
            
            print(ar, va)
            
            fig = get_new_art(ar, va)

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    root = tk.Tk()
    root.title("EEG Art Generator")
    root.geometry("500x350")

    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    button = tk.Button(control_frame, text="Select EEG File and Generate Art", command=open_file_and_generate_art)
    button.pack(pady=10)

    description_label = tk.Label(control_frame, text="", justify=tk.LEFT)
    description_label.pack(pady=10)

    plot_frame = tk.Frame(root)
    plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
