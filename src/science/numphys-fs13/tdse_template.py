# Extended template for sheet 14, ex 2 (David Nadlinger).

from numpy import arange, conj, dot, exp, imag, pi, real, sqrt, zeros
from numpy.fft import fft, ifft, fftshift
from numpy.linalg import norm
import matplotlib.pyplot as plt

#
# Simulation parameters
#

# Arbitrary parameter epsilon - would be the reduced Planck constant in
# case of a quantum-mechanical particle trapped in a potential well.
eps = 10.0**(-2)
ieps = 1.0 / eps

scale = pi

# Time until which to run the simuation.
tend = 10.0 * sqrt(ieps)

# Number of time steps.
nl = 1
n = int(tend * 10**nl)

# Space discretization: N is the number of points distributed across
# the x-axis interval [-scale, scale].
l = 12
N = 2**l

# Potential, scaled with 1 / epsilon.
x = scale * arange(-1, 1, 2.0 / N)
V = 0.5 * ieps * (x**2)         # Harmonic
#V = 8 * ieps * (1 - exp(-(x + 1)/4))**2 # Morse

# Initial value for the wave function u.
u0 = (ieps/pi)**(0.25) * exp(-(0.5*ieps)*(x+0.5)**2) * exp(-1j*x*ieps)
#u0 = COMPLETE HERE

# If True, copies of the plots for all the steps are saved as sequentially
# numbered PNG files (for producing animations, slow!).
save_figs = False


#
# Set up solution operators and norm/energy helpers.
#

# Laplacian.
#
# The Schroedinger equation as phrased on the exercise sheet (TDSE) describes a
# particle of mass 1 (if epsilon is h_bar, the reduced planck constant) in a
# potential field. The kinetic energy of this system is given (correspondence
# principle) by what is the first summand in the right hand side of the
# equation, i.e. a constant factor times the Laplacian of u, or in one
# dimension rather the second derivative of u.
#
# However, to avoid having to compute the discrete Laplacian, we can use c, the
# Fourier coefficients of u, instead. If we want A * c (as used in
# compute_norms below) to be equivalent to 0.5 * eps**2 * d2u/dx^2, what is A?
# (see the formulas on the exercise sheet)
A = # COMPLETE HERE

# Exponentials Phi_A, Phi_B used to solve the differential equation.
timestep = tend / n
ea = # COMPLETE HERE (see equations on the ex. sheet, you will probably use A)
eb = exp(-0.5j * timestep * V)

# Set up arrays for tracking wave function norm and system energies
# over time. norm_names is used for labeling the associated plot lines.
norms = zeros((n, 4))
norm_names = ["$\|u\|_{L2}$", "$E_{kin}$", "$E_{pot}$", "$E_{tot}$"]

def compute_norms(u):
    """
    Given a vector u with wave function values at points x, returns
    norm, kinetic, potential and total energies.
    """
    # We use Parseval's equation to compute (an approimation for) the L_2 norms
    # here.
    c = fft(u)
    l2norm = sqrt(2 * pi) * norm(c) / N
    cE = eps * abs(dot(conj(c), A * c) / N**2) * (2 * pi)
    pE = eps * abs(dot(conj(c), fft(V * u) / N**2)) * (2 * pi)
    return l2norm, cE, pE, (cE + pE)

# Print summary of the initial state.
norms[0] = compute_norms(u0)
print 'eps:', eps
print zip(norm_names, norms[0, :])


#
# Set up the plot window consisting of two subplots, the wave function u
# in the top half, and the evolution of norm/energies in the bottom half.
#
# We feed both plots with the initial state and keep the objects returned
# around so we can update the data later when update_plots is called.
#

times = arange(0, n + 1) * timestep

fig = plt.figure(figsize = (12, 8))
u_plot = fig.add_subplot(2, 1, 1)
e_plot = fig.add_subplot(2, 1, 2)

# Plot the wave function.
re_line, = u_plot.plot(x, real(u0), label='$Re(u)$')
im_line, = u_plot.plot(x, imag(u0), label='$Im(u)$')
abs_line, = u_plot.plot(x, abs(u0), label='$\\|u\\|$')
u_plot.legend()

# Plot the potential as well for reference (arbitrary units).
u_plot.plot(x, V * eps, 'k--')

# Norm/energies - include a bit of "breathing space" so that all lines are
# clearly visible.
e_plot.set_xlim(0, 100)
e_plot.set_ylim(0, max(norms[0]) * 1.05)
e_lines = map(lambda a, b: e_plot.plot(a, label = b)[0], norms[0], norm_names)
e_plot.legend()

def update_plots(u, time_idx):
    """
    Updates the plots to display the wave function with values given by the
    vector u, and the first time_idx norm/energy values from the norms[] array.
    """

    u_plot.set_title('time t = %s' % times[time_idx])

    # Update wave function.
    re_line.set_ydata(real(u))
    im_line.set_ydata(imag(u))
    abs_line.set_ydata(abs(u))

    # Draw energy history up to the current point in time.
    for line, data in zip(e_lines, norms[0 : time_idx + 1].transpose()):
        line.set_data(times[0 : time_idx + 1], data)

    # Tell matplotlib to refresh the screen.
    plt.draw()

    if save_figs:
        filename = str('tdse%04d' %k) + '.png'
        plt.savefig(filename)

#
# Enable interactive mode and show the plot.
#
# Interactive mode enables us to update the plot while the calculation is still
# running (otherwise, show() would not return until the plot is closed).
# Plot controls, however, are still not working (and the window cannot be
# resized, etc.) because window messages are not handled.
#
plt.ion()
plt.show()


#
# Solve the system until tend is reached after n timesteps, updating the plot in
# each iteration.
#
u = u0.copy()
for k in range(1, n):
    # Compute next time step using Strang splitting.
    u = # COMPLETE HERE
    norms[k] = compute_norms(u)
    update_plots(u, k)
