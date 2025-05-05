# lantern/hexagonal.py
"""
Hexagonal module for RSoft CAD utilities
"""

import numpy as np
import matplotlib.pyplot as plt


def hexagonal_fiber_layout(fiber_dia, num_rings=3, spacing_factor=1.0):
    """
    Computes the positions of fibers arranged in a hexagonal pattern.

    Parameters:
        fiber_dia (float): Diameter of the fibers.
        num_rings (int): Number of hexagonal rings around the central fiber.
        spacing_factor (float): Factor to adjust spacing between fibers (1.0 = touching).

    Returns:
        tuple: (centers_x, centers_y) where:
            centers_x (ndarray): x-coordinates of fiber centers.
            centers_y (ndarray): y-coordinates of fiber centers.
    """
    # Fiber radius
    r = fiber_dia / 2

    # Distance between fiber centers (adjusted by spacing factor)
    d = fiber_dia * spacing_factor

    # Initialize with central fiber
    centers_x = [0]
    centers_y = [0]

    # Create hexagonal grid
    for ring in range(1, num_rings + 1):
        # For each ring
        for i in range(6):
            # Each side of the hexagon
            for j in range(ring):
                # Calculate angle for this side of the hexagon
                angle = np.pi / 3 * i

                # Calculate the position of the current corner
                corner_x = ring * d * np.cos(angle)
                corner_y = ring * d * np.sin(angle)

                # Calculate the position of the next corner
                next_angle = np.pi / 3 * ((i + 1) % 6)
                next_x = ring * d * np.cos(next_angle)
                next_y = ring * d * np.sin(next_angle)

                # Interpolate between corners to place fibers along sides
                if j > 0:  # Skip corners (they're added at j=0)
                    t = j / ring
                    x = corner_x + t * (next_x - corner_x)
                    y = corner_y + t * (next_y - corner_y)
                    centers_x.append(x)
                    centers_y.append(y)
                else:
                    # Add corner position
                    centers_x.append(corner_x)
                    centers_y.append(corner_y)

    return np.array(centers_x), np.array(centers_y)



def calculate_capillary_diameter(fiber_dia, num_rings=3, spacing_factor=1.0):
    """
    Calculate the diameter of the capillary that fits all fibers in a hexagonal packing.

    Parameters:
        fiber_dia (float): Diameter of each fiber
        num_rings (int): Number of rings in the hexagonal packing
        spacing_factor (float): Factor to adjust spacing between fibers (1.0 = touching)

    Returns:
        float: Diameter of the encompassing circle
    """
    # In a hexagonal packing, the most distant fibers are at the corners of the hexagon
    # For spacing_factor=1.0 (touching fibers), the distance from center to corner of nth ring is:
    # distance_to_corner = num_rings * fiber_dia

    # For any spacing factor, this distance becomes:
    distance_to_corner = num_rings * fiber_dia * spacing_factor

    # To get the radius of the encompassing circle, add one fiber radius
    capillary_radius = distance_to_corner + (fiber_dia / 2)

    # Return the diameter
    return 2 * capillary_radius



