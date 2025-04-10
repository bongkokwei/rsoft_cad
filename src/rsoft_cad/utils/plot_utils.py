import matplotlib.pyplot as plt
import numpy as np


def visualise_lantern(lp_modes_dict, cladding_dia=125):
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
