import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.animation import FuncAnimation
from SignalGen import SignalGen
from Signal import Sine
from DelayandSumBeamformer import Beamformer
import soundfile as sf
step=0
def iter(last_steer_dir, rms_power, angled_waves):
    return np.random.randint(-90,90)

def beamform(azimuth, steer_dir, spacing, duration, samplerate):
    n_channels = len(spacing)
    sig_gen = SignalGen(n_channels, spacing)
    sin = Sine(frequency=1000, amplitude=1, sample_rate=48000)
    data = sin.generate_wave(duration)
    sig_gen.update_delays(azimuth, elevation)
    angled_data = sig_gen.delay_and_gain(data)
    
    beam = Beamformer(n_channels=n_channels, coord=spacing)
    beam.update_delays(steer_dir, elevation)
    outdata = 1 / n_channels * beam.beamform(angled_data)
    score = np.mean(outdata**2)
    
    wave_arr = np.vstack([angled_data.T, outdata])
    return wave_arr, score, angled_data

def plot_stacked_waves(ax, waves, sample_rate=48000, spacing=2.5, title="Stacked Audio Waves"):
    ax.clear()
    n_waves = len(waves)
    wave_length = len(waves[0])
    time = np.arange(wave_length) / sample_rate
    
    for i, wave in enumerate(waves):
        ax.plot(time, wave + (i * spacing), linewidth=1.0, label=f"Wave {i+1}")
    
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Amplitude (stacked)')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.set_yticks([i * spacing for i in range(n_waves)])
    ax.set_yticklabels([f"Wave {i+1}" for i in range(n_waves)])
    if n_waves <= 10:
        ax.legend(loc='upper right')

duration = 0.25
spacing = np.array([[-0.4, 0, 0], [-0.3, 0, 0], [-0.2, 0, 0], [-0.1, 0, 0], 
                    [0.0, 0, 0], [0.1, 0, 0], [0.2, 0, 0], [0.3, 0, 0]])
azimuth = np.random.randint(-90,90)
elevation = 0
steer_dir = 0
samplerate = 48000
m_score = -1000
tt = 0

fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(bottom=0.2)

def update(frame):
    global steer_dir, tt, m_score, step
    t1 = time.time()
    wave_arr, rms_power, angled_data = beamform(azimuth, steer_dir, spacing, duration, samplerate)
    steer_dir = iter(steer_dir, rms_power, angled_data)
    tt += time.time() - t1
    score = rms_power - tt * 0.1
    step+=1
    m_score = max(score, m_score)
    print(f"Dirr: {steer_dir} Score: {score}, Max Score: {m_score}")
    plot_stacked_waves(ax, wave_arr, sample_rate=samplerate, title=f"Step: {step} Steer Direction: {steer_dir} Sound Direction:{azimuth}")
    fig.canvas.draw_idle()

ani = FuncAnimation(fig, update, interval=500)
plt.show()
