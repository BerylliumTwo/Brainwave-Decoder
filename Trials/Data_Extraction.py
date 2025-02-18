# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 12:14:39 2025

@author: Beryl
"""

import mne
import os
import numpy as np
import scipy.io
import matplotlib.pyplot as plt

#mat_data = scipy.io.loadmat("GAMEEMO\(S01)\Raw EEG Data\.mat format\S01G1AllRawChannels.mat")
mat_data = scipy.io.loadmat("Data_Original_P01\Data_Original_P01.mat")

print(mat_data.keys())

eeg_data = mat_data["EEG_DATA"][0][0]
sfreq = 64
eeg_data = eeg_data.transpose()
print(eeg_data.shape)
print(type(eeg_data))

n_channels, n_samples = eeg_data.shape
channel_names = [f"EEG{i+1}" for i in range(n_channels)]
channel_types = ["eeg"] * n_channels

info = mne.create_info(channel_names, sfreq, channel_types)

raw = mne.io.RawArray(eeg_data, info)

print(raw.info)

times = np.arange(eeg_data.shape[1]) / sfreq

plt.figure(figsize=(12, 6))
for i in range(2, 19):
    plt.plot(times, eeg_data[i, :] + i * 100, label=channel_names[i])  # Offset for visibility

plt.xlabel("Time (s)")
plt.ylabel("Amplitude (µV)")
plt.title("EEG Signals")
plt.legend(loc="upper right")
plt.grid(True)

plt.show()

#raw.plot(scalings="auto", title="Raw EEG Data", show=True)

