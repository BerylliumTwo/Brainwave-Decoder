# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 14:21:15 2025

@author: Beryl
"""
import numpy as np
import mne
import scipy.io
from scipy import signal
from sklearn.preprocessing import MinMaxScaler
import warnings
import logging

mne.set_log_level("WARNING")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

def load_and_preprocess_data(file_path):
    mat_data = scipy.io.loadmat(file_path)
    channel_names = ['AF3', 'AF4', 'F3', 'F4', 'F7', 'F8', 'FC5', 'FC6', 'O1', 'O2', 'P7', 'P8', 'T7', 'T8']
    channel_data = []
    for channel in channel_names:
        if channel in mat_data:
            channel_data.append(mat_data[channel].flatten())
    eeg_data = np.array(channel_data)
    sfreq = 128
    n_channels, n_samples = eeg_data.shape
    channel_types = ["eeg"] * n_channels
    info = mne.create_info(channel_names, sfreq, channel_types)
    raw = mne.io.RawArray(eeg_data, info)
    raw.filter(0.5, 50., fir_design='firwin')
    ica = mne.preprocessing.ICA(n_components=14, random_state=97, max_iter=1000)
    ica.fit(raw)
    raw_clean = ica.apply(raw)
    return raw_clean, sfreq

def band_power(psd, freqs, band):
    band_freqs = np.logical_and(freqs >= band[0], freqs <= band[1])
    band_psd = psd[:, band_freqs]
    return np.trapz(band_psd, x=freqs[band_freqs], axis=1)

def compute_band_powers(raw_clean, sfreq):
    events = mne.make_fixed_length_events(raw_clean, duration=1.0)
    epochs = mne.Epochs(raw_clean, events, tmin=0, tmax=1.0, baseline=None)
    epochs_data = epochs.get_data()
    psds, freqs = mne.time_frequency.psd_array_multitaper(
        epochs_data, sfreq=sfreq, fmin=0.5, fmax=50., bandwidth=2.0, n_jobs=1
    )
    psds_avg = psds.mean(axis=1)
    eeg_bands = {'Delta': (0.5, 4), 'Theta': (4, 8), 'Alpha': (8, 12), 'Beta': (12, 30), 'Gamma': (30, 50)}
    band_powers = {band: band_power(psds_avg, freqs, eeg_bands[band]) for band in eeg_bands}
    scaler = MinMaxScaler()
    normalized_powers = scaler.fit_transform(np.array(list(band_powers.values())).T)
    return normalized_powers

def describe_mental_state(normalized_powers):
    mental_states = [
        {"state": "relaxed", "range": (0.0, 0.2)},
        {"state": "calm", "range": (0.2, 0.4)},
        {"state": "focused", "range": (0.4, 0.6)},
        {"state": "alert", "range": (0.6, 0.8)},
        {"state": "excited", "range": (0.8, 1.0)}
    ]
    
    avg_scaled_power = normalized_powers.mean()
    
    breakdown = []
    total_weight = 0
    for state in mental_states:
        lower, upper = state["range"]
        center = (lower + upper) / 2
        sigma = (upper - lower) / 2
        weight = np.exp(-((avg_scaled_power - center) ** 2 / (2 * sigma ** 2)))
        breakdown.append({"state": state["state"], "weight": weight})
        total_weight += weight
    
    mental_state_breakdown = []
    percentages = []
    for item in breakdown:
        percentage = (item["weight"] / total_weight) * 100
        percentages.append(percentage)
        if percentage > 5:
            mental_state_breakdown.append(f"{percentage:.0f}% {item['state']}")
    
    return "\n".join(mental_state_breakdown), percentages


######


def extract_only_rel_channels(file_path):
    mat_data = scipy.io.loadmat(file_path)
    channel_names = ['AF3', 'AF4', 'F3', 'F4', 'P7', 'P8', 'T7', 'T8']
    channel_data = [mat_data[channel].flatten() for channel in channel_names if channel in mat_data]
    eeg_data = np.array(channel_data)

    sfreq = 128
    info = mne.create_info(channel_names, sfreq, ["eeg"]*len(channel_names))
    raw = mne.io.RawArray(eeg_data, info)
    raw.filter(0.5, 50., fir_design='firwin')
    ica = mne.preprocessing.ICA(n_components=8, random_state=97, max_iter=800)
    ica.fit(raw)
    ica.exclude = [1, 2]
    raw_clean = ica.apply(raw)
    return raw_clean, sfreq

def split_data(raw_clean, sfreq):
    events = mne.make_fixed_length_events(raw_clean, duration=1.0)
    epochs = mne.Epochs(raw_clean, events, tmin=0, tmax=1.0, baseline=None)
    epoch_data = epochs.get_data()
    # Divide data into 10
    n_epochs = len(epoch_data)
    tenth_length = n_epochs // 10
    tenths = [
        epoch_data[i*tenth_length : (i+1)*tenth_length] 
        for i in range(10)
    ]

    if n_epochs % 10 != 0:
        tenths[-1] = np.concatenate([tenths[-1], epoch_data[10*tenth_length:]])
    return tenths

def normalize_arousal(raw_value):
    AROUSAL_RANGE = (0.5, 8.0)
    """Normalize arousal to 0-1 scale with soft clipping"""
    normalized = (raw_value - AROUSAL_RANGE[0]) / (AROUSAL_RANGE[1] - AROUSAL_RANGE[0])
    return 1 / (1 + np.exp(-(normalized - 0.5) * 10))

def normalize_valence(raw_value):
    VALENCE_RANGE = (-2.0, 2.0)
    """Normalize valence to -1 to 1 scale with soft clipping"""
    normalized = (raw_value - VALENCE_RANGE[0]) / (VALENCE_RANGE[1] - VALENCE_RANGE[0]) * 2 - 1
    return np.tanh(normalized * 3)

def calculate_arousal(epoch_data, sfreq):
    freqs, psd = signal.welch(epoch_data, sfreq, nperseg=sfreq)
    beta_idx = np.logical_and(freqs >= 12, freqs <= 30)
    beta_power = np.mean(psd[:, beta_idx], axis=1)
    
    gamma_idx = np.logical_and(freqs >= 30, freqs <= 50)
    gamma_power = np.mean(psd[:, gamma_idx], axis=1)
    
    frontal_asymmetry = epoch_data[1,:] - epoch_data[0,:]  # AF4 - AF3
    
    raw_arousal = 0.5*np.mean(beta_power) + 0.2*np.mean(gamma_power) + 0.3*np.std(frontal_asymmetry)
    
    return normalize_arousal(raw_arousal)

def calculate_valence(epoch_data, sfreq):
    freqs, psd = signal.welch(epoch_data, sfreq, nperseg=sfreq)
    alpha_idx = np.logical_and(freqs >= 8, freqs <= 13)
    alpha_power = np.mean(psd[:, alpha_idx], axis=1)
    
    theta_idx = np.logical_and(freqs >= 4, freqs <= 8)
    theta_power = np.mean(psd[:, theta_idx], axis=1)
    
    frontal_asymmetry = epoch_data[1,:] - epoch_data[0,:]
    
    raw_valence = 0.5*np.mean(alpha_power) - 0.2*np.mean(theta_power) - 0.3*np.mean(frontal_asymmetry)
    
    return normalize_valence(raw_valence)

def predict_emotion(arousal, valence):
    if arousal > 0.5:
        return "Excited/Happy" if valence > 0 else "Stressed/Angry"
    else:
        return "Content/Relaxed" if valence > 0 else "Sad/Bored"

def return_averages(tenths, sfreq):
    ar = []
    va = []
    for i, tenth in enumerate(tenths):
        tenth_arousals = [calculate_arousal(epoch, sfreq) for epoch in tenth]
        tenth_valences = [calculate_valence(epoch, sfreq) for epoch in tenth]
        
        avg_arousal = np.mean(tenth_arousals)
        avg_valence = np.mean(tenth_valences)
    
        ar.append(avg_arousal)
        va.append(avg_valence)
    return ar, va
    
if __name__ == "__main__":
    raw_clean, sfreq = extract_only_rel_channels("S01G1AllRawChannels.mat")
    tenths = split_data(raw_clean, sfreq)
    ar, va = return_averages(tenths, sfreq)
    
    for i in range(len(ar)):
        emotion = predict_emotion(ar[i], va[i])
        
        print(f"\nTime Period {i+1}:")
        print(f"Normalized Arousal: {ar[i]:.3f} (0-1 scale)")
        print(f"Normalized Valence: {va[i]:.3f} (-1 to 1 scale)")
        print(f"Dominant Emotional State: {emotion}\n")