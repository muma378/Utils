import matplotlib.pyplot as plt
import numpy as np

t = np.arange(256)
sp = np.fft.fft(np.sin(t))
freq = np.fft.fftfreq(t.shape[-1])
import pdb;pdb.set_trace()
plt.plot(freq, sp.real, freq, sp.imag)
plt.show()