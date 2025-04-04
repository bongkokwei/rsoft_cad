from rsoft_cad.utils.lantern_layout import lantern_layout
import matplotlib.pyplot as plt


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


# Example usage:
if __name__ == "__main__":
    # Visualize a 5-fiber lantern with default cladding diameter (125 microns)
    fig, ax = visualise_lantern(n=5)
    plt.show()
