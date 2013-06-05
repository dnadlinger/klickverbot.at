import numpy as np
import scipy.integrate

def l2norm_fft(f, lower, upper, N):
    nodes = np.linspace(lower, upper, num = N)
    coeffs = np.fft.fft(f(nodes)) / N
    return np.sum(np.abs(coeffs)**2) * (upper - lower)

eps = 1e-2
q = 0.5

def g(x):
    return (np.pi * eps)**(-0.25) * np.exp(-1./(2. * eps) * (x - q)**2) * np.exp(-1j * x / eps)

a = q - 3 * np.sqrt(eps)
b = q + 3 * np.sqrt(eps)

from matplotlib import pyplot as plt
xs = np.linspace(a, b, 1000)
plt.plot(xs, g(xs))
plt.show()

print scipy.integrate.quad(lambda x: np.abs(g(x))**2, a, b)[0]
print l2norm_fft(g, a, b, 2**10)
