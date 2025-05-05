# lantern/circular.py
"""
Circular module for RSoft CAD utilities
"""

import numpy as np
import matplotlib.pyplot as plt


def lantern_layout(cladding_dia, n, rot=np.pi / 2):
    """
    Computes the positions of 5 circles arranged in a circular fashion
    around a larger reference circle.

    Parameters:
        cladding_dia (float): Diameter of the smaller circles (cladding diameter).

    Returns:
        tuple: (R, centres_x, centres_y) where:
            R (float): Radius of the reference circle.
            centres_x (ndarray): x-coordinates of cladding circle centres.
            centres_y (ndarray): y-coordinates of cladding circle centres.
    """

    # Compute the radius of the larger circle
    if n > 1:
        R = cladding_dia / (2 * np.sin(np.pi / n))
        # Angles for placing the circles
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)

        # Centre positions of small circles
        centres_x = R * np.cos(angles + rot)
        centres_y = R * np.sin(angles + rot)
    else:
        R = cladding_dia / 2
        centres_x = np.array([0])
        centres_y = np.array([0])

    return R, centres_x, centres_y



def find_scale_factor(start_dia, n, start_scale, end_scale, step_scale):
    scale_factor = np.arange(start_scale, end_scale, step_scale)
    R_array = np.zeros(len(scale_factor))

    for i, scale in enumerate(scale_factor):
        R_array[i], _, _ = lantern_layout(start_dia / scale, n=n)

    return scale_factor, R_array



