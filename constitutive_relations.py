import numpy as np
from scipy.constants import e, mu_0 as mu0, epsilon_0 as eps0, m_e


def plasma_frequency(plasma_density):

    return e * np.sqrt(plasma_density / (m_e * eps0))


def skin_depth(plasma_density):

    return np.sqrt(m_e / (plasma_density * mu0)) / e
