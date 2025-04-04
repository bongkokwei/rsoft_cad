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


def plot_hexagonal_fibers(fiber_dia, num_rings=3, spacing_factor=1.0):
    """
    Plots the fibers in a hexagonal pattern.

    Parameters:
        fiber_dia (float): Diameter of the fibers.
        num_rings (int): Number of hexagonal rings around the central fiber.
        spacing_factor (float): Factor to adjust spacing between fibers (1.0 = touching).
    """
    centers_x, centers_y = hexagonal_fiber_layout(fiber_dia, num_rings, spacing_factor)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")

    # Plot each fiber as a circle
    for x, y in zip(centers_x, centers_y):
        circle = plt.Circle((x, y), fiber_dia / 2, fill=False, edgecolor="blue")
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


# Example usage
if __name__ == "__main__":
    # Example: 125 µm diameter fibers with 3 rings
    fiber_diameter = 125
    fig, ax = plot_hexagonal_fibers(fiber_diameter, num_rings=1, spacing_factor=1.05)
    plt.show()

    # Calculate theoretical packing efficiency
    centers_x, centers_y = hexagonal_fiber_layout(
        fiber_diameter, num_rings=3, spacing_factor=1.05
    )
    num_fibers = len(centers_x)
    print(f"Generated {num_fibers} fibers in hexagonal arrangement")
