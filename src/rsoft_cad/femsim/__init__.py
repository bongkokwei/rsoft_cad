"""
NEF File Plotter - A tool for analyzing and visualizing multiple .nef files.

This package provides functionality to process, analyze, and visualize data from
.nef files typically used in optical waveguide simulations.
"""

from .data_processing import (
    process_nef_files,
    extract_run_names,
    get_z_positions_from_runs,
    create_dataframe_from_nef_data,
    create_axis_values,
)

from .outlier_detection import (
    remove_outliers_by_zscore,
    apply_outlier_removal,
)

from .curve_fitting import (
    sigmoid_decay,
    double_exp_decay,
    polynomial,
    fit_index_data,
    plot_fit_results,
)

from .visualisation import (
    setup_figure,
    plot_component,
    plot_components,
    add_legend,
    save_figure,
    plot_combined_nef_files,
)

from .utils import filter_indices

from .plot import nef_plot

from .param_scan import femsim_tapered_lantern, femsimulation

__all__ = [
    # Data processing
    "process_nef_files",
    "extract_run_names",
    "get_z_positions_from_runs",
    "create_dataframe_from_nef_data",
    "create_axis_values",
    # Outlier detection
    "remove_outliers_by_zscore",
    "apply_outlier_removal",
    # Curve fitting
    "sigmoid_decay",
    "double_exp_decay",
    "polynomial",
    "fit_index_data",
    "plot_fit_results",
    # Visualization
    "setup_figure",
    "plot_component",
    "plot_components",
    "add_legend",
    "save_figure",
    "plot_combined_nef_files",
    # Utils
    "filter_indices",
]
