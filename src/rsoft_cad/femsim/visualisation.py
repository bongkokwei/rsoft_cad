import os
from typing import Dict, List, Tuple, Optional, Union, Any, Callable

import numpy as np
import matplotlib.pyplot as plt

# Import from other modules
from .data_processing import process_nef_files, create_axis_values
from .outlier_detection import apply_outlier_removal
from .curve_fitting import plot_fit_results, fit_index_data
from .utils import filter_indices


def setup_figure(
    plot_type: str,
) -> Tuple[plt.Figure, Union[plt.Axes, Tuple[plt.Axes, plt.Axes]]]:
    """
    Set up the figure and axes for plotting.

    Args:
        plot_type (str): Type of plot ('real', 'imag', or 'both')

    Returns:
        Tuple containing:
            - Figure object
            - Axes object(s)
    """
    if plot_type == "both":
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle("Effective index across taper", fontsize=16)
        return fig, (ax1, ax2)
    else:
        fig, ax1 = plt.subplots(figsize=(12, 6))
        fig.suptitle("Effective index across taper", fontsize=16)
        return fig, ax1


def plot_component(
    ax: plt.Axes,
    x_values: List[float],
    x_labels: List[str],
    unique_indices: List[int],
    index_data: Dict[int, List[float]],
    total_files: int,
    cmap: plt.cm.ScalarMappable,
    component_type: str,
    use_filename_as_x: bool,
) -> None:
    """
    Plot a component (real or imaginary) of the effective index.

    Args:
        ax (plt.Axes): Matplotlib axes to plot on
        x_values (List[float]): X-axis values
        x_labels (List[str]): X-axis labels
        unique_indices (List[int]): List of unique mode indices
        index_data (Dict[int, List[float]]): Dictionary of data by mode index
        total_files (int): Total number of files (for padding)
        cmap (plt.cm.ScalarMappable): Color map for different indices
        component_type (str): Component type ('real' or 'imag')
        use_filename_as_x (bool): If True, use filenames as x-axis
    """
    for i, idx in enumerate(unique_indices):
        if idx in index_data:
            values = index_data[idx]
            # Pad with NaN if missing values for some files
            if len(values) < total_files:
                values = values + [np.nan] * (total_files - len(values))

            ax.plot(
                x_values,
                values,
                marker="o",
                markerfacecolor="none",  # Makes circles unfilled
                markeredgecolor=cmap(i / len(unique_indices)),  # Color for the outline
                linestyle="none",  # This prevents connecting lines
                label=f"Index {idx}",
                markersize=3,
            )
    # Set labels and grid
    x_axis_label = "Filename" if use_filename_as_x else "Taper length (micron)"
    y_axis_label = "Real(n_eff)" if component_type == "real" else "Im(n_eff)"

    ax.set_xlabel(x_axis_label)
    ax.set_ylabel(y_axis_label)
    ax.grid(True)

    # Configure x-ticks if using filenames
    if use_filename_as_x:
        ax.set_xticks(x_values)
        ax.set_xticklabels(x_labels, rotation=45, ha="right")


def plot_components(
    plot_type: str,
    ax1: plt.Axes,
    ax2: Optional[plt.Axes],
    x_values: List[float],
    x_labels: List[str],
    unique_indices: List[int],
    index_data_real: Dict[int, List[float]],
    index_data_imag: Dict[int, List[float]],
    total_files: int,
    cmap: Any,
    use_filename_as_x: bool,
) -> None:
    """
    Plot the specified components (real and/or imaginary) based on plot_type.

    Args:
        plot_type (str): Type of plot ('real', 'imag', or 'both')
        ax1 (plt.Axes): Primary axes object
        ax2 (Optional[plt.Axes]): Secondary axes object (for 'both' type)
        x_values (List[float]): X-axis values
        x_labels (List[str]): X-axis labels
        unique_indices (List[int]): List of unique mode indices
        index_data_real (Dict[int, List[float]]): Real component data by mode index
        index_data_imag (Dict[int, List[float]]): Imaginary component data by mode index
        total_files (int): Total number of files
        cmap (Any): Color map for different indices
        use_filename_as_x (bool): If True, use filenames as x-axis
    """
    # Plot real part if needed
    if plot_type in ["real", "both"]:
        plot_component(
            ax1,
            x_values,
            x_labels,
            unique_indices,
            index_data_real,
            total_files,
            cmap,
            "real",
            use_filename_as_x,
        )

    # Plot imaginary part if needed
    if plot_type in ["imag", "both"]:
        ax = ax2 if plot_type == "both" else ax1
        plot_component(
            ax,
            x_values,
            x_labels,
            unique_indices,
            index_data_imag,
            total_files,
            cmap,
            "imag",
            use_filename_as_x,
        )


def add_legend(
    fig: plt.Figure,
    ax1: plt.Axes,
    plot_type: str,
) -> None:
    """
    Add a legend to the figure.

    Args:
        fig (plt.Figure): Figure object
        ax1 (plt.Axes): Primary axes object
        plot_type (str): Type of plot ('real', 'imag', or 'both')
    """
    if plot_type == "both":
        handles, labels = ax1.get_legend_handles_labels()
        fig.legend(handles, labels, loc="center right", bbox_to_anchor=(1.15, 0.5))
    else:
        ax1.legend(loc="center left", bbox_to_anchor=(1.05, 0.5))


def save_figure(
    fig: plt.Figure, folder_path: str, output_path: Optional[str], plot_type: str
) -> None:
    """
    Save the figure to a file.

    Args:
        fig (plt.Figure): Figure to save
        folder_path (str): Default folder path for saving
        output_path (Optional[str]): Custom output path
        plot_type (str): Type of plot ('real', 'imag', or 'both')
    """
    if output_path is None:
        output_path = os.path.join(
            folder_path,
            f"combined_nef_plot_{plot_type}.png",
        )

    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved plot to {output_path}")


def plot_combined_nef_files(
    folder_path: str,
    include_subfolders: bool = False,
    save_plot: bool = False,
    output_path: Optional[str] = None,
    plot_type: str = "real",
    max_indices: Optional[int] = None,
    use_filename_as_x: bool = True,
    remove_outliers: bool = False,
    window_size: float = 5000,
    z_threshold: float = 3,
    colormap: str = "viridis",
    plot_indices: Optional[List[int]] = None,
    fit_data: bool = False,
    fit_function: Optional[Callable] = None,
) -> Optional[plt.Figure]:
    """
    Plot multiple .nef files with each index as a separate line.

    Args:
        folder_path (str): Path to the folder containing .nef files
        include_subfolders (bool): If True, search for files in subfolders as well
        save_plot (bool): If True, save the plot as PNG file
        output_path (Optional[str]): Path to save the plot (if None, generates a default name)
        plot_type (str): 'real', 'imag', or 'both' to specify which part to plot
        max_indices (Optional[int]): Maximum number of indices to plot (None for all)
        use_filename_as_x (bool): If True, use filenames as x-axis; otherwise use file index
        remove_outliers (bool): If True, apply outlier removal using z-score method
        window_size (float): Window size for outlier detection (in x-axis units)
        z_threshold (float): Z-score threshold for outlier detection
        colormap (str): Colormap for plot (default: viridis)
        plot_indices (Optional[List[int]]): Specific mode indices to plot
        fit_data (bool): If True, apply curve fitting to the data points
        fit_function (Optional[Callable]): Function to use for fitting (default: polynomial)

    Returns:
        Optional[plt.Figure]: The figure object or None if no files found
    """
    # Process NEF files
    index_data_real, index_data_imag, file_names, nef_files = process_nef_files(
        folder_path, include_subfolders
    )

    if not nef_files:
        return None

    # Get unique indices across all files
    unique_indices = sorted(index_data_real.keys())

    # Filter indices based on provided criteria
    unique_indices = filter_indices(unique_indices, max_indices, plot_indices)

    if not unique_indices:
        return None

    # Create x-axis values
    x_values, x_labels = create_axis_values(
        folder_path, nef_files, file_names, use_filename_as_x
    )

    # Set up figure and axes
    if plot_type == "both":
        fig, (ax1, ax2) = setup_figure(plot_type)
    else:
        fig, ax1 = setup_figure(plot_type)
        ax2 = None

    # Color map for different indices
    cmap = plt.get_cmap(colormap, len(unique_indices))

    # Apply outlier removal if requested
    if remove_outliers:
        print("Cleaning data...")
        # Process real part data if needed
        if plot_type in ["real", "both"]:
            index_data_real = apply_outlier_removal(
                index_data_real, unique_indices, x_values, window_size, z_threshold
            )

        # Process imaginary part data if needed
        if plot_type in ["imag", "both"]:
            index_data_imag = apply_outlier_removal(
                index_data_imag, unique_indices, x_values, window_size, z_threshold
            )

    # Plot components based on plot_type
    plot_components(
        plot_type,
        ax1,
        ax2,
        x_values,
        x_labels,
        unique_indices,
        index_data_real,
        index_data_imag,
        len(nef_files),
        cmap,
        use_filename_as_x,
    )

    # Apply curve fitting if requested
    if fit_data:
        print("Fitting curves to data...")
        fit_results = fit_index_data(
            index_data_real, index_data_imag, x_values, fit_function
        )

        # Plot fit results
        if plot_type in ["real", "both"]:
            plot_fit_results(ax1, x_values, unique_indices, fit_results, cmap, "real")

        if plot_type in ["imag", "both"]:
            ax = ax2 if plot_type == "both" else ax1
            plot_fit_results(ax, x_values, unique_indices, fit_results, cmap, "imag")

    # Add legend and adjust layout
    add_legend(fig, ax1, plot_type)
    plt.tight_layout()

    # Save plot if requested
    if save_plot:
        save_figure(fig, folder_path, output_path, plot_type)

    return fig
