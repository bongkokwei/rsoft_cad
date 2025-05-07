# visualization/field_plots.py
"""
Field_plots module for RSoft CAD utilities
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_field_data(field_data):
    """Create visualizations for the complex field data and return dictionary of (fig, ax) pairs"""
    # Extract values from the field_data dictionary
    complex_data = field_data["complex_data"]
    xmin = field_data["xmin"]
    xmax = field_data["xmax"]
    ymin = field_data["ymin"]
    ymax = field_data["ymax"]
    wavelength = field_data["wavelength"]
    taper_length = field_data["taper_length"]
    nx = field_data["nx"]
    ny = field_data["ny"]

    # Calculate magnitudes
    magnitudes = np.array([abs(c) for c in complex_data])
    phases = np.array([np.angle(c) for c in complex_data])

    # Use actual grid dimensions from the data
    print(f"Grid dimensions: {nx}x{ny}")

    # Create coordinate arrays
    x = np.linspace(xmin, xmax, nx)
    y = np.linspace(ymin, ymax, ny)
    X, Y = np.meshgrid(x, y)

    # Reshape data to 2D grid using actual dimensions
    Z_mag = np.zeros((ny, nx))
    Z_phase = np.zeros((ny, nx))

    for i in range(min(nx * ny, len(magnitudes))):
        row = i // nx
        col = i % nx
        if row < ny and col < nx:
            Z_mag[row, col] = magnitudes[i]
            Z_phase[row, col] = phases[i]

    # Create individual figures and store in dictionary
    result = {}

    # Plot 1: Magnitude as 2D colormap
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    im1 = ax1.pcolormesh(X, Y, Z_mag, shading="auto", cmap="viridis")
    plt.colorbar(im1, ax=ax1, label="Magnitude")
    ax1.set_title(
        f"Field Magnitude (Wavelength={wavelength}, Length={taper_length}microns)"
    )
    ax1.set_xlabel("X position")
    ax1.set_ylabel("Y position")
    result["magnitude_2d"] = (fig1, ax1)

    # Plot 2: 3D surface of magnitude
    fig2, ax2 = plt.subplots(figsize=(8, 6), subplot_kw={"projection": "3d"})
    surf = ax2.plot_surface(X, Y, Z_mag, cmap="plasma", linewidth=0, antialiased=False)
    plt.colorbar(surf, ax=ax2, shrink=0.5, aspect=5, label="Magnitude")
    ax2.set_title("3D Surface Plot of Magnitude")
    ax2.set_xlabel("X position")
    ax2.set_ylabel("Y position")
    ax2.set_zlabel("Magnitude")
    result["magnitude_3d"] = (fig2, ax2)

    # Plot 3: Phase as 2D colormap
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    im3 = ax3.pcolormesh(X, Y, Z_phase, shading="auto", cmap="hsv")
    plt.colorbar(im3, ax=ax3, label="Phase (radians)")
    ax3.set_title("Field Phase")
    ax3.set_xlabel("X position")
    ax3.set_ylabel("Y position")
    result["phase_2d"] = (fig3, ax3)

    # Plot 4: Contour plot of magnitude
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    contour = ax4.contour(X, Y, Z_mag, 15, colors="black")
    im4 = ax4.contourf(X, Y, Z_mag, 15, cmap="RdYlBu_r")
    plt.colorbar(im4, ax=ax4, label="Magnitude")
    ax4.clabel(contour, inline=True, fontsize=8)
    ax4.set_title("Contour Plot of Magnitude")
    ax4.set_xlabel("X position")
    ax4.set_ylabel("Y position")
    result["magnitude_contour"] = (fig4, ax4)

    return result


