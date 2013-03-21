#
# Computes the linear least squares fit for a set of experimental data to
# illustrate several different methods of solving the linear least squares
# problem.
#
# Note: In practice, an optimized algorithm (such as the one employed by
# np.linalg.lstsq) should always be preferred to a the below naive
# implementations.
#

import numpy as np
from matplotlib import pyplot as plt

def lstsq_normal_eqns(A, b):
    return np.linalg.solve(np.dot(A.T, A), np.dot(A.T, b))

def lstsq_qr(A, b):
    Q, R = np.linalg.qr(A)
    return np.linalg.solve(R, np.dot(Q.T, b))

def lstsq_svd(A, b):
    U, s, VT = np.linalg.svd(A)
    r = sum(s > 1e-10 * s[0])
    return np.dot((VT.T)[:r, :], np.dot(U[:, :r].T, b) / s[:r])

def lstsq_cheating(A, b):
    return np.linalg.lstsq(A, b)[0]

if __name__ == '__main__':
    currents = np.array([1.00, 2.02, 3.01, 4.01, 5.00, 5.99, 7.00, 8.01, 9.01, 9.97])
    hall_voltages = np.array([2.75, 5.5, 8.4, 11.0, 14.3, 17.0, 20.0, 23.0, 26.5, 29.5])

    A = np.array([currents, np.ones(currents.size)]).T

    def dump(s):
        print s
        plt.plot(currents, s[0] * currents + s[1])

    dump(lstsq_normal_eqns(A, hall_voltages))
    dump(lstsq_qr(A, hall_voltages))
    dump(lstsq_svd(A, hall_voltages))
    dump(lstsq_cheating(A, hall_voltages))

    plt.scatter(currents, hall_voltages)
    plt.show()
