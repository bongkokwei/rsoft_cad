import numpy as np
import matplotlib.pyplot as plt


def lantern_layout(cladding_dia, n):
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
    # Small circle (cladding) radius
    r = cladding_dia / 2

    # Compute the radius of the larger circle
    R = cladding_dia / (2 * np.sin(np.pi / n))

    # Angles for placing the circles
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)

    # Centre positions of small circles
    centres_x = R * np.cos(angles)
    centres_y = R * np.sin(angles)

    return R, centres_x, centres_y


def find_scale_factor(start_dia, n):
    scale_factor = np.arange(1, 30, 0.1)
    R_array = np.zeros(len(scale_factor))

    for i, scale in enumerate(scale_factor):
        R_array[i], _, _ = lantern_layout(start_dia / scale, n=n)

    return scale_factor, R_array


if __name__ == "__main__":

    # Example usage and plotting
    n = 5
    cladding_dia = 125  # Define the cladding diameter
    R, centres_x, centres_y = lantern_layout(cladding_dia, n)

    print(f"Radius of lantern modes: {R:.2f} micron")
    print(f"Radius of center core: {R - (cladding_dia / 2):.2f} micron")
    print(f"Radius of capillary: {R + (cladding_dia / 2):.2f} micron")

    # Create plot
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

    fig1, ax1 = plt.subplots(figsize=(6, 6))
    scale_factor, radius = find_scale_factor(start_dia=125, n=6)
    ax1.plot(scale_factor, radius, ".")
    ax1.set_ylabel("Cladding diameter (micron)")
    ax1.set_xlabel("Scale factor")
    ax1.grid(True)

    plt.show()
