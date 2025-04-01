# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 13:11:43 2025

@author: Beryl
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy.ndimage import gaussian_filter
import random

def stabilize_line_parameters(num_lines):
    if num_lines <= 50:
        line_width = 30
        line_alpha = 0.3
    elif num_lines <= 100:
        line_width = 15
        line_alpha = 0.5
    else:
        line_width = 2
        line_alpha = 0.8
    return line_width, line_alpha

def generate_brain_art(
    canvas_size=(12, 6), 
    num_lines=100, 
    num_nodes=14, 
    wave_intensity=0.05, 
    line_tightness=0.1, 
    line_alpha=0.5, 
    node_size_range=(0.02, 0.05), 
    color_palette=[(0.1, 0.1, 0.1)], 
    smoothness=20, 
    line_width=0.5,
    background_color=(0.95, 0.95, 0.95)
):
    fig, ax = plt.subplots(figsize=canvas_size)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)
    x = np.linspace(0, 1, 1000)
    y_grid = np.linspace(0, 1, 1000)
    X, Y = np.meshgrid(x, y_grid)
    flow_field = np.zeros_like(X)
    node_positions = []
    
    for _ in range(num_nodes):
        cx, cy = np.random.rand(2)
        node_positions.append((cx, cy))
        size = np.random.uniform(*node_size_range)
        ellipse = Ellipse((cx, cy), size, size, alpha=0)
        ax.add_patch(ellipse)
        distances = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        flow_field += np.exp(-distances / line_tightness) * wave_intensity * np.sign(Y - cy)
        
    flow_field = gaussian_filter(flow_field, sigma=smoothness)
    flow_field = (flow_field - flow_field.min()) / (flow_field.max() - flow_field.min())
    
    for i in range(num_lines):
        base_y = i / num_lines
        y_offsets = flow_field[i * (1000 // num_lines), :]
        y = base_y + (y_offsets - 0.5) * wave_intensity
        color = random.choice(color_palette)
        ax.plot(x, y, color=color, alpha=line_alpha, linewidth=line_width)
        
    return fig