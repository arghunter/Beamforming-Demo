import numpy as np

from time import time
from scipy import signal
from DelayApproximation import DelayAproximator


v=340.3 # speed of sound at sea level m/s
    
class Beamformer:
    def __init__(self,n_channels=8,coord=np.array([[-0.08,0.042],[-0.08,0.014],[-0.08,-0.028],[-0.08,-0.042],[0.08,0.042],[0.08,0.014],[0.08,-0.028],[0.08,-0.042]]),sample_rate=48000):
        self.n_channels = n_channels
        self.coord = coord
        self.sample_rate = sample_rate
        self.delays = np.zeros(n_channels) #in microseconds
        self.gains = np.ones(n_channels) # multiplier
        self.sample_dur= 1/sample_rate *10**6 #Duration of a sample in microseconds
        self.delay_approx=DelayAproximator(self.coord)
        self.doa=0
        self.update_delays(0,0)
        self.locked=False
    def beamform(self,samples):
        
        sample_save=samples
        samples,max_sample_shift=self.delay_and_gain(samples)
       
        samples=self.sum_channels(samples)
        if hasattr(self,'last_overlap'):
            for i in range(self.last_overlap.shape[0]):
                samples[i]+=self.last_overlap[i]
        
        self.last_overlap=samples[samples.shape[0]-max_sample_shift:samples.shape[0]]
 
        

        return samples[0:samples.shape[0]-max_sample_shift]

    def sum_channels(self,samples):
        summed=np.zeros(samples.shape[0])
        for j in range(samples.shape[0]):
            summed[j] = samples[j].sum()
        return summed
    def delay_and_gain(self, samples):
        #backwards interpolations solves every prblem
        shifts=self.calculate_channel_shift()

        intshifts=np.floor(shifts)
        max_sample_shift=int(max(intshifts))
        dims = samples.shape
        dims=(int(dims[0]+max_sample_shift),dims[1])
        delayed = np.zeros(dims)
        if hasattr(self,'last_samples'):
            
            for i in range(self.n_channels):
                intermult=1-(shifts[i]%1)
                shiftdiff=max_sample_shift-int(intshifts[i])
                delayed[0+shiftdiff][i]=self.gains[i]*((samples[0][i]-self.last_samples[len(self.last_samples)-1][i])*(intermult)+self.last_samples[len(self.last_samples)-1][i])               
        else:
            for i in range(self.n_channels):
                intermult=1-(shifts[i]%1)
                shiftdiff=max_sample_shift-int(intshifts[i])
                delayed[0+shiftdiff][i]=(self.gains[i]*(samples[0][i]-0)*(intermult))               
        
        for i in range(self.n_channels):
            intermult=1-(shifts[i]%1)
            shiftdiff=max_sample_shift-int(intshifts[i])
            for j in range(1,dims[0]-max_sample_shift):
                delayed[j+shiftdiff][i]=self.gains[i]*((samples[j][i]-samples[j-1][i])*(intermult)+samples[j-1][i])               
            
        
        self.last_samples=samples
       
        return delayed,max_sample_shift
    #calculates number of samples to delay
    def calculate_channel_shift(self):
        channel_shifts=(self.delays/self.sample_dur)
        return channel_shifts

    def update_delays(self,azimuth,elevation): #doa in degrees, assuming plane wave as it is a far-field source
        # self.doa=doa
        self.delays=np.array(self.delay_approx.get_flat_delays(azimuth,elevation))*10**6
        # print(self.delays)
        shift=min(self.delays)
        self.delays+=-shift
        # print("azi ele")
        # print(str(azimuth)+" "+str(elevation))
        # print("channel shift")
        # print(self.calculate_channel_shift())







