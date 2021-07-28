import json
import math

"""
Defines some useful equations for establishing OSIRIS parameters.
"""

# Constants

# Taken from CODATA

e = 1.602176634e-19  # C, elementary charge
c = 299792458  # m/s, speed of light in vacuo
eps0 = 8.8541878128e-12  # F/m, vacuum electric permittivity
mu0 = 1.25663706212e-6  # N/(A*A). vacuum magnetic permeability
m_e = 9.1093837015e-31  # kg, electron mass

# Calculates the SI values
# They're functionalised so that they can be called whenever

# System


def x_step(laser_wavelength):
    return laser_wavelength / 20


def y_step(density):
    return skin_depth(density) / 4


def z_step(density):
    return skin_depth(density) / 4


def nx(xdims, laser_wavelength):
    return xdims / x_step(laser_wavelength)


def ny(ydims, density):
    return ydims / y_step(density)


def nz(zdims, density):
    return zdims / z_step(density)


def time_step(laser_wavelength, density):
    return 0.99 * (math.sqrt(x_step(laser_wavelength)**2 +
                             y_step(density)**2 + z_step(density)**2) / c)


def timesteps_total(sim_length, laser_wavelength, density):
    return sim_length / time_step(laser_wavelength, density)


def ndump(sim_length, laser_wavelength, density):
    return timesteps_total(sim_length, laser_wavelength, density) / 100

# Plasma


def uniform_length(total_length, ramp_lengths):
    return total_length - sum(ramp_lengths)


def plasma_frequency(density):
    return math.sqrt((density * e * e) / (eps0 * m_e))


def wavelength(density):
    return 2 * math.pi * c / plasma_frequency(density)


def period(density):
    return wavelength(density) / c


def skin_depth(density):
    return c / plasma_frequency(density)

# Laser


def laser_frequency(laser_wavelength):
    return 2 * math.pi * c / laser_wavelength

# Witness Beam


def num_electons(total_charge):
    return total_charge / e
