"""
Lantern module for RSoft CAD package.

This package provides classes and utilities for designing and simulating
photonic lantern structures, particularly mode-selective lanterns used
in spatial mode multiplexing applications.
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

from .femsim_plot import nef_plot

from .femsim_param_scan import femsim_tapered_lantern, femsimulation

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
