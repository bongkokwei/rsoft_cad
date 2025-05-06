# lantern/visualization.py
"""
Visualisation module for RSoft CAD utilities
"""

import numpy as np
import matplotlib.pyplot as plt

from rsoft_cad.utils.fiber_layout.circular import lantern_layout
from rsoft_cad.utils.fiber_layout.hexagonal import (
    hexagonal_fiber_layout,
    calculate_capillary_diameter,
)


def visualise_lantern(n, cladding_dia=125, show_scale_factor_plot=True):
    """
    Visualize a lantern layout with n cladding circles.

    Parameters:
    -----------
    n : int
        Number of cladding circles
    cladding_dia : float
        Diameter of the cladding circles in microns (default: 125)
    show_scale_factor_plot : bool
        If True, shows the scale factor vs radius plot (default: True)

    Returns:
    --------
    tuple
        (fig, ax) for the main lantern layout plot
        (fig1, ax1) for the scale factor plot (if show_scale_factor_plot=True)
    """

    # Calculate lantern layout
    R, centres_x, centres_y = lantern_layout(cladding_dia, n)

    # Print information
    print(f"Radius of lantern modes: {R:.2f} micron")
    print(f"Radius of center core: {R - (cladding_dia / 2):.2f} micron")
    print(f"Radius of capillary: {R + (cladding_dia / 2):.2f} micron")

    # Create main plot
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-R - cladding_dia, R + cladding_dia)
    ax.set_ylim(-R - cladding_dia, R + cladding_dia)
    ax.set_aspect("equal")

    # Draw larger reference circle
    lantern = plt.Circle(
        (0, 0),
        R,
        color="blue",
        fill=False,
        linestyle="dashed",
    )
    center_core = plt.Circle(
        (0, 0),
        R - (cladding_dia / 2),
        color="green",
        fill=False,
        linestyle="dashed",
    )
    capillary = plt.Circle(
        (0, 0),
        R + (cladding_dia / 2),
        color="orange",
        fill=False,
        linestyle="solid",
    )
    ax.add_patch(capillary)
    ax.add_patch(center_core)
    ax.add_patch(lantern)

    # Draw smaller cladding circles
    for x, y in zip(centres_x, centres_y):
        cladding = plt.Circle((x, y), cladding_dia / 2, color="red", fill=False)
        ax.add_patch(cladding)

    # Plot centre points
    ax.scatter(centres_x, centres_y, color="black", label="Centres of cladding circles")
    ax.scatter(0, 0, color="blue", marker="x", label="Centre of reference circle")

    # Labels and legend
    ax.set_title(f"{n} Cladding Circles in a Lantern Layout")
    ax.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    return (fig, ax)


def plot_hexagonal_fibers(fiber_dia, num_rings=3, spacing_factor=1.0):
    """
    Plots the fibers in a hexagonal pattern.

    Parameters:
        fiber_dia (float): Diameter of the fibers.
        num_rings (int): Number of hexagonal rings around the central fiber.
        spacing_factor (float): Factor to adjust spacing between fibers (1.0 = touching).
    """
    centers_x, centers_y = hexagonal_fiber_layout(fiber_dia, num_rings, spacing_factor)
    cap_dia = calculate_capillary_diameter(fiber_dia, num_rings, spacing_factor)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")

    # Plot each fiber as a circle
    for x, y in zip(centers_x, centers_y):
        circle = plt.Circle((x, y), fiber_dia / 2, fill=False, edgecolor="blue")
        ax.add_patch(circle)

    circle = plt.Circle((0, 0), cap_dia / 2, fill=False, edgecolor="green")
    ax.add_patch(circle)

    # Set limits with some padding
    max_extent = max(
        max(abs(centers_x) + fiber_dia / 2), max(abs(centers_y) + fiber_dia / 2)
    )
    ax.set_xlim(-max_extent * 1.1, max_extent * 1.1)
    ax.set_ylim(-max_extent * 1.1, max_extent * 1.1)

    # Add grid and labels
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.set_title(f"Hexagonal Fiber Layout - {len(centers_x)} fibers")
    ax.set_xlabel("X position")
    ax.set_ylabel("Y position")

    # Show fiber count and parameters
    info_text = (
        f"Diameter: {fiber_dia}\nSpacing factor: {spacing_factor}\nRings: {num_rings}"
    )
    ax.text(
        0.02,
        0.98,
        info_text,
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()
    return fig, ax


def visualise_lp_lantern(lp_modes_dict, cladding_dia=125):
    """
    Visualize a lantern layout with LP modes positioned according to the provided dictionary.

    Parameters:
    -----------
    lp_modes_dict : dict
        Dictionary containing LP mode names as keys and coordinate tuples as values
        Example: {'LP01': (x1, y1), 'LP11a': (x2, y2), ...}
    cladding_dia : float
        Diameter of the cladding circles in microns (default: 125)

    Returns:
    --------
    tuple
        (fig, ax) for the main lantern layout plot
    """
    # Create main plot
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")

    # Draw cladding circles for each LP mode
    for mode_name, coords in lp_modes_dict.items():
        x, y = coords
        # Convert numpy float64 to regular float if needed
        if hasattr(x, "item"):
            x = x.item()
        if hasattr(y, "item"):
            y = y.item()

        # Draw the cladding circle
        cladding = plt.Circle((x, y), cladding_dia / 2, color="red", fill=False)
        ax.add_patch(cladding)

        # Annotate with the LP mode name
        ax.annotate(mode_name, (x, y), ha="center", va="center", fontsize=8)

    # Set axis limits based on the data
    all_x = [coords[0] for coords in lp_modes_dict.values()]
    all_y = [coords[1] for coords in lp_modes_dict.values()]

    # Calculate appropriate limits with some padding
    max_abs_x = max(abs(np.array(all_x).max()), abs(np.array(all_x).min()))
    max_abs_y = max(abs(np.array(all_y).max()), abs(np.array(all_y).min()))
    max_radius = max(max_abs_x, max_abs_y) + cladding_dia

    ax.set_xlim(-max_radius, max_radius)
    ax.set_ylim(-max_radius, max_radius)

    # Labels and grid
    ax.set_title("LP Modes in a Lantern Layout")
    ax.set_xlabel("x-axis (micron)")
    ax.set_ylabel("y-axis (micron)")
    plt.grid(True, linestyle="--", alpha=0.5)

    return (fig, ax)
