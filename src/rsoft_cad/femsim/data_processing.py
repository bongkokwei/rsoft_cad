import os
import re

import pandas as pd

from typing import Dict, List, Tuple
from collections import defaultdict
from rsoft_cad.utils import find_files_by_extension, read_nef_file


def extract_run_names(file_paths: List[str]) -> List[str]:
    """
    Extract 'run_XXX' parts from a list of file paths.

    Args:
        file_paths (List[str]): List of file paths containing run_XXX.nef files

    Returns:
        List[str]: List of extracted run names in the format 'run_XXX'
    """
    run_names = []

    for path in file_paths:
        # Extract filename from path
        filename = os.path.basename(path)

        # Extract run_XXX using regex (removing the .nef extension)
        match = re.match(r"(run_\d+)\.nef", filename)
        if match:
            run_names.append(match.group(1))

    return run_names


def get_z_positions_from_runs(
    dataframe: pd.DataFrame, file_paths: List[str]
) -> Tuple[List[float], List[str]]:
    """
    Extract z_pos values from a DataFrame based on run names found in file paths.

    Args:
        dataframe (pd.DataFrame): DataFrame with 'filename' and 'z_pos' columns
        file_paths (List[str]): List of file paths containing run_XXX.nef files

    Returns:
        Tuple[List[float], List[str]]: A tuple containing:
            - List of z_pos values corresponding to the run names
            - List of run names extracted from file paths
    """
    # Extract run names from file paths
    run_names = extract_run_names(file_paths)

    # Filter DataFrame to get only rows with matching filenames
    filtered_df = dataframe[dataframe["filename"].isin(run_names)]

    # Extract z_pos values
    z_positions = filtered_df["z_pos"].tolist()

    return z_positions, run_names


def process_nef_files(
    folder_path: str, include_subfolders: bool = True
) -> Tuple[Dict[int, List[float]], Dict[int, List[float]], List[str], List[str]]:
    """
    Process multiple .nef files and extract relevant data.

    Args:
        folder_path (str): Path to the folder containing .nef files
        include_subfolders (bool): If True, search for files in subfolders as well

    Returns:
        Tuple containing:
            - Dictionary of real index data by mode index
            - Dictionary of imaginary index data by mode index
            - List of file names
            - List of file paths
    """
    # Find all .nef files
    nef_files = find_files_by_extension(folder_path, ".nef", include_subfolders)

    if not nef_files:
        print(f"No .nef files found in {folder_path}")
        return {}, {}, [], []

    print(f"Found {len(nef_files)} .nef files")

    # Dictionary to organize data by index
    index_data_real = defaultdict(list)
    index_data_imag = defaultdict(list)
    file_names = []

    # Process each file
    for file_path in nef_files:
        try:
            # Get filename for display
            filename = os.path.basename(file_path)
            file_names.append(os.path.splitext(filename)[0])  # Remove extension

            # Read the data
            data = read_nef_file(file_path)

            # Store data by index
            for j, idx in enumerate(data["indices"]):
                index_data_real[idx].append(data["n_eff_real"][j])
                index_data_imag[idx].append(data["n_eff_imag"][j])

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    return index_data_real, index_data_imag, file_names, nef_files


def create_dataframe_from_nef_data(
    index_data: Dict[int, List[float]],
    x_values: List[float],
    index_id: int,
) -> pd.DataFrame:
    """
    Create a DataFrame from NEF data for a specific mode index.

    Args:
        index_data (Dict[int, List[float]]): Dictionary of data by mode index
        x_values (List[float]): X-axis values (e.g., taper lengths)
        index_id (int): Mode index to extract

    Returns:
        pd.DataFrame: DataFrame with x and y columns
    """
    if index_id not in index_data or not index_data[index_id]:
        return pd.DataFrame()

    # Get the data for this index
    y_values = index_data[index_id]

    # Create DataFrame
    df = pd.DataFrame(
        {
            "taper_length": x_values[: len(y_values)],  # Ensure lengths match
            "n_eff": y_values,
        }
    )

    return df


def create_axis_values(
    folder_path: str,
    nef_files: List[str],
    file_names: List[str],
    use_filename_as_x: bool,
) -> Tuple[List[float], List[str]]:
    """
    Create x-axis values and labels for plotting.

    Args:
        folder_path (str): Path to the folder containing .nef files
        nef_files (List[str]): List of .nef file paths
        file_names (List[str]): List of file names without extensions
        use_filename_as_x (bool): If True, use filenames as x-axis; otherwise use z positions

    Returns:
        Tuple[List[float], List[str]]: x-values and x-labels for plotting
    """
    # Get parent directory of the data folder
    expt_dir, _ = os.path.split(folder_path)

    try:
        # Read the CSV containing z-position data
        x_values_df = pd.read_csv(os.path.join(expt_dir, "x_values.csv"))

        # Get z-positions from the data frame
        z_positions, _ = get_z_positions_from_runs(x_values_df, nef_files)

        # Set x values and labels
        x_values = z_positions
        x_labels = file_names if use_filename_as_x else [str(x) for x in z_positions]

        return x_values, x_labels

    except Exception as e:
        print(f"Error creating axis values: {e}")
        print("Using default numerical indices for x-axis.")

        # Fallback to using numerical indices
        x_values = list(range(len(file_names)))
        x_labels = file_names if use_filename_as_x else [str(i) for i in x_values]

        return x_values, x_labels
