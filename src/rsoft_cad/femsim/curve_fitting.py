from typing import Dict, List, Tuple, Optional, Union, Any, Callable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from collections import defaultdict
from scipy import stats
from scipy.optimize import curve_fit


def sigmoid_decay(x, a, b, c, d, e):
    """
    Function combining linear decay with sigmoid drop-off
    a + b*x + c/(1 + np.exp(d*(x-e)))

    a, b: linear component parameters
    c, d, e: sigmoid component parameters
    e: position of the sigmoid midpoint
    """
    return a + b * x + c / (1 + np.exp(d * (x - e)))


def double_exp_decay(x, A, B, C, D, E):
    """
    Double exponential decay function.

    Parameters:
    -----------
    x : array-like
        Independent variable (taper length in microns)
    A : float
        Asymptotic value (baseline)
    B : float
        Amplitude of first exponential term
    C : float
        Decay constant for first exponential term
    D : float
        Amplitude of second exponential term
    E : float
        Decay constant for second exponential term

    Returns:
    --------
    y : array-like
        Dependent variable (effective index)
    """
    return A + B * np.exp(-x / C) + D * np.exp(-x / E)


def polynomial(x, a, b, c):
    """
    Simple polynomial function for fitting.

    Parameters:
    -----------
    x : array-like
        Independent variable
    a, b, c : float
        Polynomial coefficients

    Returns:
    --------
    y : array-like
        a*x^2 + b*x + c
    """
    return a * x**2 + b * x + c


def fit_index_data(
    index_data_real: Dict[int, List[float]],
    index_data_imag: Dict[int, List[float]],
    x_values: List[float],
    fit_function: Optional[Callable] = None,
) -> Dict[int, Dict[str, Any]]:
    """
    Fits real and imaginary index data and stores results in a defaultdict.

    Parameters:
    -----------
    index_data_real : Dict[int, List[float]]
        Dictionary mapping indices to lists of real component values
    index_data_imag : Dict[int, List[float]]
        Dictionary mapping indices to lists of imaginary component values
    x_values : List[float]
        X-axis values for fitting (e.g., taper lengths)
    fit_function : callable, optional
        Function to use for fitting. Default is a simple polynomial fit.

    Returns:
    --------
    fit_results : Dict[int, Dict[str, Any]]
        Dictionary containing fitted parameters and functions for each index
    """
    # Default to a polynomial function if none provided
    if fit_function is None:
        fit_function = polynomial

    # Create defaultdict to store results
    fit_results = defaultdict(dict)

    # Process each index
    all_indices = set(index_data_real.keys()) | set(index_data_imag.keys())

    for idx in all_indices:
        # Process real component data
        if idx in index_data_real and len(index_data_real[idx]) > 0:
            y_real = np.array(index_data_real[idx])
            x_real = np.array(
                x_values[: len(y_real)]
            )  # Use actual x-values, not just indices

            # Filter out NaN values
            valid_mask = ~np.isnan(y_real)
            x_real_valid = x_real[valid_mask]
            y_real_valid = y_real[valid_mask]

            # Only try to fit if we have enough valid data points
            if len(y_real_valid) > 3:  # Need at least 4 points for a good fit
                try:
                    # Fit real component
                    popt_real, pcov_real = curve_fit(
                        fit_function, x_real_valid, y_real_valid
                    )

                    # Store results
                    fit_results[idx]["real_params"] = popt_real
                    fit_results[idx]["real_covariance"] = pcov_real

                    # Generate fitted curve (for all x values, including those with NaN y-values)
                    fit_results[idx]["real_fitted"] = [
                        fit_function(x, *popt_real) if not np.isnan(x) else np.nan
                        for x in x_real
                    ]
                    # Store function for later use
                    fit_results[idx]["real_function"] = (
                        lambda x, params=popt_real: fit_function(x, *params)
                    )
                except Exception as e:
                    fit_results[idx]["real_error"] = f"Fitting error: {str(e)}"

        # Process imaginary component data
        if idx in index_data_imag and len(index_data_imag[idx]) > 0:
            y_imag = np.array(index_data_imag[idx])
            x_imag = np.array(x_values[: len(y_imag)])  # Use actual x-values

            # Filter out NaN values
            valid_mask = ~np.isnan(y_imag)
            x_imag_valid = x_imag[valid_mask]
            y_imag_valid = y_imag[valid_mask]

            # Only try to fit if we have enough valid data points
            if len(y_imag_valid) > 3:
                try:
                    # Fit imaginary component
                    popt_imag, pcov_imag = curve_fit(
                        fit_function, x_imag_valid, y_imag_valid
                    )

                    # Store results
                    fit_results[idx]["imag_params"] = popt_imag
                    fit_results[idx]["imag_covariance"] = pcov_imag

                    # Generate fitted curve
                    fit_results[idx]["imag_fitted"] = [
                        fit_function(x, *popt_imag) if not np.isnan(x) else np.nan
                        for x in x_imag
                    ]
                    # Store function for later use
                    fit_results[idx]["imag_function"] = (
                        lambda x, params=popt_imag: fit_function(x, *params)
                    )
                except Exception as e:
                    fit_results[idx]["imag_error"] = f"Fitting error: {str(e)}"

    return fit_results


def plot_fit_results(
    ax: plt.Axes,
    x_values: List[float],
    unique_indices: List[int],
    fit_results: Dict[int, Dict[str, Any]],
    cmap: plt.cm.ScalarMappable,
    component_type: str,
) -> None:
    """
    Plot the fitted curves on the axes.

    Parameters:
    -----------
    ax : plt.Axes
        Matplotlib axes to plot on
    x_values : List[float]
        X-axis values
    unique_indices : List[int]
        List of unique mode indices
    fit_results : Dict[int, Dict[str, Any]]
        Dictionary containing fitted parameters and functions
    cmap : plt.cm.ScalarMappable
        Color map for different indices
    component_type : str
        Component type ('real' or 'imag')
    """
    # Create a dense x-grid for smoother curves
    x_min = min(x_values)
    x_max = max(x_values)
    x_dense = np.linspace(x_min, x_max, 1000)

    for i, idx in enumerate(unique_indices):
        fit_key = f"{component_type}_function"
        if idx in fit_results and fit_key in fit_results[idx]:
            try:
                # Get the fit function
                fit_func = fit_results[idx][fit_key]

                # Generate smooth curve
                y_fit = [fit_func(x) for x in x_dense]

                # Plot the fit
                ax.plot(
                    x_dense,
                    y_fit,
                    "-",
                    color=cmap(i / len(unique_indices)),
                    linewidth=1.5,
                    alpha=0.7,
                    zorder=0,  # Put fit lines behind data points
                )
            except Exception as e:
                print(f"Error plotting fit for index {idx} ({component_type}): {e}")
