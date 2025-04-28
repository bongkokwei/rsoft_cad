import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import glob


def find_fld_files(folder_path, include_subfolders=False):
    """
    Find all files with .fld extension in the specified folder.

    Parameters:
    folder_path (str): Path to the folder to search in
    include_subfolders (bool): If True, search in subfolders as well (recursive search)

    Returns:
    list: List of .fld filenames found
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"The path '{folder_path}' is not a valid directory")

    if include_subfolders:
        # Recursive search using os.walk
        fld_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".fld"):
                    fld_files.append(os.path.join(root, file))
    else:
        # Non-recursive search using glob
        fld_files = glob.glob(os.path.join(folder_path, "*.fld"))

    return fld_files


def read_field_data(filename):
    """
    Read complex data from the file format provided and return as a dictionary
    """

    with open(filename, "r") as f:
        lines = f.readlines()

    # Extract header information
    header_line_1 = lines[2].strip().split()
    nx = int(header_line_1[0])  # Grid reference value
    xmin = float(header_line_1[1])
    xmax = float(header_line_1[2])
    wavelength = float(header_line_1[5].split("=")[1])
    taper_length = int(header_line_1[3])
    header_line_2 = lines[3].strip().split()
    ny = int(header_line_2[0])
    ymin = float(header_line_2[1])
    ymax = float(header_line_2[2])

    print(
        f"Header info: Grid reference: {nx}, Range: [{xmin}, {xmax}], Wavelength: {wavelength}"
    )

    # Extract data values (starting from line 4)
    data_str = " ".join(lines[4:]).strip().split()
    data = [float(val) for val in data_str]
    # Convert to complex numbers
    complex_data = []
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            real = data[i]
            imag = data[i + 1]
            complex_data.append(complex(real, imag))

    # Return all values as a dictionary
    return {
        "complex_data": complex_data,
        "xmin": xmin,
        "xmax": xmax,
        "wavelength": wavelength,
        "taper_length": taper_length,
        "ymin": ymin,
        "ymax": ymax,
        "nx": nx,
        "ny": ny,
    }


def find_mon_files(folder_path, include_subfolders=False):
    """
    Find all files with .mon extension in the specified folder.
    Parameters:
    folder_path (str): Path to the folder to search in
    include_subfolders (bool): If True, search in subfolders as well (recursive search)
    Returns:
    list: List of .mon filenames found
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"The path '{folder_path}' is not a valid directory")

    if include_subfolders:
        # Recursive search using os.walk
        mon_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".mon"):
                    mon_files.append(os.path.join(root, file))
    else:
        # Non-recursive search using glob
        mon_files = glob.glob(os.path.join(folder_path, "*.mon"))

    return mon_files


def read_mon_file(file_path):
    """
    Read a .mon file into a pandas DataFrame.

    Parameters:
    file_path (str): Path to the .mon file

    Returns:
    tuple: (header_info, data_df) where:
        - header_info is a dictionary containing monitor metadata
        - data_df is a pandas DataFrame with z-axis as the first column and monitor readings as other columns
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist")

    # Read the file content
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Parse header information (first 5 lines)
    header_info = {}

    # Process header lines
    monitor_numbers = lines[0].split(":")[1].strip().split()
    monitor_paths = lines[1].split(":")[1].strip().split()
    monitor_types = lines[2].split(":")[1].strip().split()
    monitor_tilts = lines[3].split(":")[1].strip().split()
    monitor_modes = lines[4].split(":")[1].strip().split()

    header_info["monitor_numbers"] = [int(num) for num in monitor_numbers]
    header_info["monitor_paths"] = [int(path) for path in monitor_paths]
    header_info["monitor_types"] = monitor_types
    header_info["monitor_tilts"] = [int(tilt) for tilt in monitor_tilts]
    header_info["monitor_modes"] = [int(mode) for mode in monitor_modes]

    # Parse data rows (starting from line 5 onward)
    data_rows = []
    for line in lines[5:]:
        values = [float(val) for val in line.strip().split()]
        data_rows.append(values)

    # Create a pandas DataFrame
    data_array = np.array(data_rows)

    # Create column names: 'z' for first column, then 'monitor_1', 'monitor_2', etc.
    num_columns = data_array.shape[1]
    column_names = ["z"]
    column_names.extend([f"monitor_{i}" for i in range(1, num_columns)])

    # Create the DataFrame
    data_df = pd.DataFrame(data_array, columns=column_names)

    return header_info, data_df
