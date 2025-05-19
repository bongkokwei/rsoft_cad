import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jv


def generate_lp_mode(
    l, p, orientation, mfd, xmin, xmax, ymin, ymax, num_grid_x, num_grid_y
):
    """
    Generate LP mode with specified parameters and orientation
    Parameters:
    l: azimuthal mode index
    p: radial mode index (p-1 gives the number of radial nodes)
    orientation: 'a' (even/cosine), 'b' (odd/sine), or 'both' (combined with arbitrary phase)
    mfd: Mode Field Diameter (μm)
    xmin, xmax: x-axis range (μm)
    ymin, ymax: y-axis range (μm)
    num_grid_x: Number of grid points in x direction
    num_grid_y: Number of grid points in y direction
    """
    # Create coordinate grid with separate x and y ranges
    x = np.linspace(xmin, xmax, num_grid_x)
    y = np.linspace(ymin, ymax, num_grid_y)
    X, Y = np.meshgrid(x, y)
    # Convert to polar coordinates
    R = np.sqrt(X**2 + Y**2)
    Phi = np.arctan2(Y, X)

    # Convert MFD to beam waist (w0)
    w0 = mfd / 2

    # For LP modes in optical fibers:
    from scipy.special import jv

    # For LP02 mode specifically
    if l == 0 and p == 2:
        # Use the correct formula for LP02
        # For LP02, we need one sign change in the radial function
        # The first root of J0 is at ~2.405
        # The second root is at ~5.520

        # Normalized radius
        rho = R / w0

        # LP02 has a zero crossing at a specific radius
        zero_crossing = 5.520 / 2.405  # Ratio of second to first zero of J0

        # Create the LP02 mode directly
        radial_part = (1 - 2 * (rho / zero_crossing) ** 2) * np.exp(-(rho**2) / 2)

        # No angular dependence for l=0
        field = radial_part
    else:
        # For other LP modes, use the standard approach
        # Normalized radius
        rho = R / w0

        # Calculate u parameter (related to V number in fiber)
        if l == 0 and p == 1:
            u = 2.405  # First zero of J0
        elif l == 1 and p == 1:
            u = 3.832  # First zero of J1
        elif l == 2 and p == 1:
            u = 5.136  # First zero of J2
        else:
            # Approximation for other modes
            u = (l + 2 * p - 0.5) * np.pi / 2

        # Calculate the radial part using Bessel functions
        radial_part = jv(l, u * rho / w0) * np.exp(-(rho**2) / 2)

        # Angular component based on orientation
        if l == 0:
            # For l=0 modes (LP0p), there's no orientation distinction
            field = radial_part
        else:
            if orientation == "a":
                # Even mode (a-type) - horizontal orientation for LP11a
                field = radial_part * np.cos(l * Phi)
            elif orientation == "b":
                # Odd mode (b-type) - vertical orientation for LP11b
                field = radial_part * np.sin(l * Phi)
            elif orientation == "both":
                # Generate complex field with both orientations
                phase = 0  # Can be changed to rotate the mode
                field = radial_part * (
                    np.cos(l * Phi) + 1j * np.sin(l * Phi) * np.exp(1j * phase)
                )
            else:
                raise ValueError("Orientation must be 'a', 'b', or 'both'")

    # Normalize field
    field = field / np.max(np.abs(field))

    return X, Y, field


def plot_lp_mode(X, Y, field, l, p, orientation, mfd):
    plt.figure(figsize=(12, 5))

    # Plot intensity
    plt.subplot(1, 2, 1)
    intensity = np.abs(field) ** 2
    plt.pcolormesh(X, Y, intensity, cmap="viridis")
    plt.colorbar(label="Intensity")
    plt.title(f"LP{l}{p}{orientation} Mode Intensity (MFD={mfd}μm)")
    plt.xlabel("x (μm)")
    plt.ylabel("y (μm)")
    plt.axis("equal")

    # Plot field amplitude or phase
    plt.subplot(1, 2, 2)

    # For complex fields ('both' orientation), plot phase
    if np.iscomplexobj(field) and orientation == "both":
        plt.pcolormesh(X, Y, np.angle(field), cmap="hsv", vmin=-np.pi, vmax=np.pi)
        plt.colorbar(label="Phase (rad)")
        plt.title(f"LP{l}{p} Combined Mode Phase")
    else:
        # For real fields ('a' or 'b' orientation), plot field amplitude
        plt.pcolormesh(X, Y, np.real(field), cmap="seismic", vmin=-1, vmax=1)
        plt.colorbar(label="Field Amplitude")
        plt.title(f"LP{l}{p}{orientation} Mode Field Distribution")

    plt.xlabel("x (μm)")
    plt.ylabel("y (μm)")
    plt.axis("equal")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Example usage for LP11a (horizontally oriented lobes)
    l = 0
    p = 2
    orientation = "a"  # 'a' for even/cosine orientation (horizontal for LP11)
    mfd = 10.0
    xmin, xmax = -20.0, 20.0
    ymin, ymax = -20.0, 20.0
    num_grid_x = 256
    num_grid_y = 256

    X, Y, field_a = generate_lp_mode(
        l, p, orientation, mfd, xmin, xmax, ymin, ymax, num_grid_x, num_grid_y
    )
    plot_lp_mode(X, Y, field_a, l, p, orientation, mfd)
