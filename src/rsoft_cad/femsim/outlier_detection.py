import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List

from .data_processing import create_dataframe_from_nef_data


def remove_outliers_by_zscore(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    window_size: float = 5000,
    z_threshold: float = 3,
) -> pd.DataFrame:
    """
    Remove outliers from data using local z-scores within moving windows.

    Args:
        df (pd.DataFrame): DataFrame containing the data
        x_column (str): Name of the column to use as x-axis (e.g., 'taper_length')
        y_column (str): Name of the column to check for outliers (e.g., 'real_n_eff')
        window_size (float): Size of windows to calculate local z-scores
        z_threshold (float): Z-score threshold to identify outliers

    Returns:
        pd.DataFrame: DataFrame with outliers removed
    """
    # Guard against empty DataFrames
    if df.empty:
        return df

    # Sort data by x-axis value
    df_sorted = df.sort_values(x_column).copy()

    # Create bins for local z-score calculation
    x_min = df_sorted[x_column].min()
    x_max = df_sorted[x_column].max()

    # Create appropriate number of bins
    bins = np.arange(x_min, x_max + window_size, window_size)

    # Handle edge case of too few data points
    if len(bins) <= 1:
        bins = [x_min, x_max]

    df_sorted["bin"] = pd.cut(df_sorted[x_column], bins=bins)

    # Calculate z-scores within each bin
    df_sorted["zscore"] = df_sorted.groupby("bin")[y_column].transform(
        lambda x: stats.zscore(x, nan_policy="omit") if len(x) > 1 else 0,
    )

    # Filter out points with high z-scores
    df_cleaned = df_sorted[abs(df_sorted["zscore"]) < z_threshold]

    # Remove temporary columns before returning
    df_cleaned = df_cleaned.drop(["bin", "zscore"], axis=1)

    return df_cleaned


def apply_outlier_removal(
    index_data: Dict[int, List[float]],
    unique_indices: List[int],
    x_values: List[float],
    window_size: float,
    z_threshold: float,
) -> Dict[int, List[float]]:
    """
    Apply outlier removal to a set of index data.

    Args:
        index_data (Dict[int, List[float]]): Dictionary of data by mode index
        unique_indices (List[int]): List of unique mode indices to process
        x_values (List[float]): X-axis values
        window_size (float): Window size for outlier detection
        z_threshold (float): Z-score threshold for outlier detection

    Returns:
        Dict[int, List[float]]: Updated index data with outliers removed
    """
    processed_data = index_data.copy()

    for idx in unique_indices:
        if idx in processed_data:
            # Create DataFrame for this index
            df = create_dataframe_from_nef_data(processed_data, x_values, idx)
            if not df.empty:
                # Remove outliers
                df_cleaned = remove_outliers_by_zscore(
                    df,
                    "taper_length",
                    "n_eff",
                    window_size,
                    z_threshold,
                )
                # Update the values
                processed_data[idx] = df_cleaned["n_eff"].tolist()

    return processed_data
