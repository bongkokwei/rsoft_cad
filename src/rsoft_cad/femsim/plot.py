"""
NEF File Plotter - Entry point

This script serves as the entry point for the NEF file plotter tool,
parsing command-line arguments and orchestrating the plotting workflow.
"""

import os
import argparse
import matplotlib.pyplot as plt
from typing import Optional, Callable


# Import from other modules
from .visualisation import plot_combined_nef_files
from .curve_fitting import polynomial, sigmoid_decay, double_exp_decay


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate plots from NEF files in a specified folder."
    )

    # Required argument for the folder path
    parser.add_argument(
        "--folder-path",
        type=str,
        default="femsim_run_001",
        help="Path to the folder containing NEF files",
    )

    # New argument to specify a list of indices to plot
    parser.add_argument(
        "--plot-indices",
        type=int,
        nargs="+",  # Allows one or more integer arguments
        help="Specific mode indices to plot (if provided, only these indices will be plotted)",
    )

    # Optional arguments
    parser.add_argument(
        "--plot-type",
        type=str,
        choices=["real", "imag", "both"],
        default="real",
        help="Type of plot to generate: 'real', 'imag', or 'both' (default: real)",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the plot to a file instead of displaying it",
    )

    parser.add_argument(
        "--output-path",
        type=str,
        help="Custom path to save the output file (used with --save)",
    )

    parser.add_argument(
        "--max-indices",
        type=int,
        default=12,
        help="Maximum number of indices to plot (default: 12)",
    )

    parser.add_argument(
        "--use-filename-x",
        action="store_true",
        help="Use filename as x-axis instead of numerical index",
    )

    parser.add_argument(
        "--no-filename-x",
        action="store_false",
        dest="use_filename_x",
        help="Use numerical index as x-axis instead of filename",
    )

    parser.add_argument(
        "--include-subfolders",
        action="store_true",
        help="Include NEF files in subfolders",
    )

    # Outlier removal arguments
    parser.add_argument(
        "--remove-outliers",
        action="store_true",
        help="Remove outliers using z-score method",
    )

    parser.add_argument(
        "--window-size",
        type=float,
        default=5000,
        help="Window size for outlier detection (in x-axis units)",
    )

    parser.add_argument(
        "--z-threshold",
        type=float,
        default=3.0,
        help="Z-score threshold for outlier detection (default: 3.0)",
    )

    parser.add_argument(
        "--colormap",
        type=str,
        default="managua",
        help="Colormap for plot (default: managua)",
    )

    # Curve fitting arguments
    parser.add_argument(
        "--fit-data",
        action="store_true",
        help="Apply curve fitting to the data points",
    )

    parser.add_argument(
        "--fit-function",
        type=str,
        choices=["polynomial", "sigmoid", "double_exp"],
        default="polynomial",
        help="Function to use for curve fitting (default: polynomial)",
    )

    return parser.parse_args()


def nef_plot() -> None:
    """Main function to run the NEF file plotting tool."""
    # Parse command line arguments
    args = parse_arguments()

    # Construct the full path to the data files
    data_folder = os.path.join("output", args.folder_path, "rsoft_data_files")

    # Determine fitting function if requested
    fit_function = None
    if args.fit_data:
        if args.fit_function == "polynomial":
            fit_function = polynomial
        elif args.fit_function == "sigmoid":
            fit_function = sigmoid_decay
        elif args.fit_function == "double_exp":
            fit_function = double_exp_decay

    # Create combined plot with the specified parameters
    fig = plot_combined_nef_files(
        folder_path=data_folder,
        include_subfolders=args.include_subfolders,
        plot_type=args.plot_type,
        save_plot=args.save,
        output_path=args.output_path,
        max_indices=args.max_indices,
        use_filename_as_x=args.use_filename_x,
        remove_outliers=args.remove_outliers,
        window_size=args.window_size,
        z_threshold=args.z_threshold,
        colormap=args.colormap,
        plot_indices=args.plot_indices,
        fit_data=args.fit_data,
        fit_function=fit_function,
    )

    # Show the plot (unless save_plot is True)
    if fig and not args.save:
        plt.show()


if __name__ == "__main__":
    nef_plot()
