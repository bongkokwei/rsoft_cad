# visualization/field_plots.py
"""
Field_plots module for RSoft CAD utilities
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_field_data(data_dict, plot_type="magnitude", figsize=(10, 8), cmap="viridis"):
    """
    Plot the complex field data from a dictionary returned by read_femsim_field_data.

    Parameters:
    -----------
    data_dict : dict
        Dictionary containing the complex data and metadata from read_femsim_field_data
    plot_type : str, optional
        Type of plot to generate: 'magnitude', 'phase', 'real', 'imaginary', or 'all'
        Default is 'magnitude'
    figsize : tuple, optional
        Size of the figure in inches. Default is (10, 8)
    cmap : str, optional
        Colormap to use for the plots. Default is 'viridis'

    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object containing the plot(s)
    """

    # Extract data and metadata from the dictionary
    complex_data = data_dict["complex_data"]
    xmin, xmax = data_dict["xmin"], data_dict["xmax"]
    ymin, ymax = data_dict["ymin"], data_dict["ymax"]
    nx, ny = data_dict["nx"], data_dict["ny"]

    # Create coordinate grids
    x = np.linspace(xmin, xmax, nx)
    y = np.linspace(ymin, ymax, ny)
    X, Y = np.meshgrid(x, y)

    # Handle different plot types
    if plot_type == "all":
        # Create a figure with 4 subplots for all visualizations
        fig, axes = plt.subplots(2, 2, figsize=figsize)

        # Magnitude plot
        im0 = axes[0, 0].pcolormesh(
            X, Y, np.abs(complex_data).T, cmap=cmap, shading="auto"
        )
        axes[0, 0].set_title("Magnitude")
        axes[0, 0].set_xlabel("X")
        axes[0, 0].set_ylabel("Y")
        fig.colorbar(im0, ax=axes[0, 0], label="Magnitude")

        # Phase plot
        im1 = axes[0, 1].pcolormesh(
            X, Y, np.angle(complex_data, deg=True).T, cmap=cmap, shading="auto"
        )
        axes[0, 1].set_title("Phase (degrees)")
        axes[0, 1].set_xlabel("X")
        axes[0, 1].set_ylabel("Y")
        fig.colorbar(im1, ax=axes[0, 1], label="Phase (degrees)")

        # Real part plot
        im2 = axes[1, 0].pcolormesh(
            X, Y, np.real(complex_data).T, cmap=cmap, shading="auto"
        )
        axes[1, 0].set_title("Real Part")
        axes[1, 0].set_xlabel("X")
        axes[1, 0].set_ylabel("Y")
        fig.colorbar(im2, ax=axes[1, 0], label="Real Part")

        # Imaginary part plot
        im3 = axes[1, 1].pcolormesh(
            X, Y, np.imag(complex_data).T, cmap=cmap, shading="auto"
        )
        axes[1, 1].set_title("Imaginary Part")
        axes[1, 1].set_xlabel("X")
        axes[1, 1].set_ylabel("Y")
        fig.colorbar(im3, ax=axes[1, 1], label="Imaginary Part")
    else:
        # Single plot based on plot_type
        fig, ax = plt.subplots(figsize=figsize)

        if plot_type == "magnitude":
            plot_data = np.abs(complex_data)
            title = "Field Magnitude"
            cbar_label = "Magnitude"
        elif plot_type == "phase":
            plot_data = np.angle(complex_data, deg=True)
            title = "Field Phase (degrees)"
            cbar_label = "Phase (degrees)"
        elif plot_type == "real":
            plot_data = np.real(complex_data)
            title = "Real Part of Field"
            cbar_label = "Real Part"
        elif plot_type == "imaginary":
            plot_data = np.imag(complex_data)
            title = "Imaginary Part of Field"
            cbar_label = "Imaginary Part"
        else:
            raise ValueError(
                f"Invalid plot_type: {plot_type}. Must be one of 'magnitude', 'phase', 'real', 'imaginary', or 'all'"
            )

        im = ax.pcolormesh(X, Y, plot_data.T, cmap=cmap, shading="auto")
        ax.set_title(title)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        fig.colorbar(im, ax=ax, label=cbar_label)

    # Add metadata to the plot
    z_pos = data_dict.get("z_pos", "unknown")
    output_type = data_dict.get("output_type", "")
    wavelength = data_dict.get("wavelength", "unknown")

    metadata_str = f"Z-position: {z_pos}, Output type: {output_type}"
    if "wavelength" in data_dict:
        metadata_str += f", Wavelength: {wavelength}"

    plt.figtext(0.5, 0.01, metadata_str, ha="center", fontsize=9)
    plt.tight_layout(
        rect=[0, 0.03, 1, 0.97]
    )  # Adjust layout to make room for metadata text

    return fig
