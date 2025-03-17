from SignalGen import SignalGen
from Signal import Sine
import soundfile as sf
import matplotlib.pyplot as plt
from DelayandSumBeamformer import Beamformer



def beamform(azimuth,steer_dir,spacing,duration,samplerate):
    n_channels=len(spacing)
    sig_gen=SignalGen(n_channels,spacing)
    sin=Sine(frequency=1000,amplitude=1,sample_rate=48000)
    data=sin.generate_wave(duration)
    sig_gen.update_delays(azimuth,elevation)
    angled_data=sig_gen.delay_and_gain(data)

    beam=Beamformer(n_channels=n_channels,coord=spacing)
    
    beam.update_delays(steer_dir,elevation)
    outdata=1/n_channels*beam.beamform(angled_data)
    score=np.mean(outdata**2)
    
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    
    # Create some example waves with different characteristics
    wave_arr=np.zeros((len(angled_data.T)+1,len(angled_data)))
    wave_arr[0:len(wave_arr)-1]=angled_data.T
    wave_arr[-1]=outdata
    return wave_arr,score


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Ensure SignalGen, Sine, and Beamformer are properly imported or defined

def plot_stacked_waves(ax, waves, sample_rate=48000, spacing=2.5, time_range=None, title="Stacked Audio Waves"):
    """Update plot with stacked waves."""
    ax.clear()
    n_waves = len(waves)
    wave_length = len(waves[0])
    time = np.arange(wave_length) / sample_rate

    if time_range:
        start_idx = int(time_range[0] * sample_rate)
        end_idx = int(time_range[1] * sample_rate)
        start_idx = max(0, min(start_idx, wave_length-1))
        end_idx = max(0, min(end_idx, wave_length-1))
        time = time[start_idx:end_idx]
    else:
        start_idx = 0
        end_idx = wave_length

    for i, wave in enumerate(waves):
        plotted_wave = wave[start_idx:end_idx] + (i * spacing)
        ax.plot(time, plotted_wave, linewidth=1.0, label=f"Wave {i+1}")

    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Amplitude (stacked)')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.set_yticks([i * spacing for i in range(n_waves)])
    ax.set_yticklabels([f"Wave {i+1}" for i in range(n_waves)])
    if n_waves <= 10:
        ax.legend(loc='upper right')
    ax.set_title(f"{title} (Sample Rate: {sample_rate}Hz)")
    plt.draw()

def update(val):
    """Update plot when steer_dir changes."""
    steer_dir = slider.val
    wave_arr,score = beamform(azimuth, steer_dir, spacing, duration, samplerate)
    # print(wave_arr.shape)
    print("Score:"+str(score))
    plot_stacked_waves(ax, wave_arr, sample_rate=samplerate)
    fig.canvas.draw_idle()

# Define parameters
duration = 0.25
spacing = np.array([[-0.4, 0, 0], [-0.3, 0, 0], [-0.2, 0, 0], [-0.1, 0, 0], 
                    [0.0, 0, 0], [0.1, 0, 0], [0.2, 0, 0], [0.3, 0, 0]])
azimuth = 30
elevation = 0
steer_dir = 30
samplerate = 48000

# Initial wave array
wave_arr,score = beamform(azimuth, steer_dir, spacing, duration, samplerate)

# Create plot
fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(bottom=0.2)  # Adjust space for the slider
plot_stacked_waves(ax, wave_arr, sample_rate=samplerate)

# Add slider for steer_dir
ax_slider = plt.axes([0.2, 0.05, 0.65, 0.03])
slider = Slider(ax_slider, 'Steer Dir', -90, 90, valinit=steer_dir)
slider.on_changed(update)

plt.show()