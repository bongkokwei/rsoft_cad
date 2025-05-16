# io/readers.py
"""
Readers module for RSoft CAD utilities
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import glob
import numpy as np
import shutil


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


def read_nef_file(file_path):
    """
    Read and parse a .nef file containing effective refractive index data.

    Parameters:
    file_path (str): Path to the .nef file

    Returns:
    dict: Dictionary containing parsed data with the following keys:
        - 'indices': Array of index values (first column)
        - 'n_eff_real': Array of real parts of effective refractive index (second column)
        - 'n_eff_imag': Array of imaginary parts of effective refractive index (third column)
        - 'n_eff_complex': Array of complex numbers (real + j*imag)
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist")

    # Check if file has the correct extension
    if not file_path.lower().endswith(".nef"):
        raise ValueError(f"The file '{file_path}' does not have the .nef extension")

    # Initialize lists to store data
    indices = []
    n_eff_real = []
    n_eff_imag = []

    # Read the file
    with open(file_path, "r") as file:
        for line in file:
            # Skip empty lines
            if not line.strip():
                continue

            # Split the line by whitespace
            parts = line.strip().split()

            # Check if the line has the expected format (3 columns)
            if len(parts) != 3:
                print(f"Warning: Skipping line with unexpected format: {line.strip()}")
                continue

            try:
                # Parse the values
                index = int(parts[0])
                real_part = float(parts[1])
                imag_part = float(parts[2])

                # Append to lists
                indices.append(index)
                n_eff_real.append(real_part)
                n_eff_imag.append(imag_part)

            except ValueError as e:
                print(f"Warning: Could not parse line '{line.strip()}': {e}")
                continue

    # Convert lists to numpy arrays for easier manipulation
    indices = np.array(indices)
    n_eff_real = np.array(n_eff_real)
    n_eff_imag = np.array(n_eff_imag)

    # Create complex array combining real and imaginary parts
    n_eff_complex = n_eff_real + 1j * n_eff_imag

    # Return data as dictionary
    return {
        "indices": indices,
        "n_eff_real": n_eff_real,
        "n_eff_imag": n_eff_imag,
        "n_eff_complex": n_eff_complex,
    }


def read_field_data(filename):
    """
    Read complex data from a 2D uniform grid file format and return as a dictionary.

    The file format follows this syntax:
    /rn,a,b/nx0
    /rn,qa,qb
    Nx X0 Xn Zpos Output_Type Optional_Data
    Ny Y0 Yn
    Data(X0,Y0)      ...      Data(X0,Yn)
    ...              ...      ...
    Data(Xn,Y0)      ...      Data(Xn,Yn)

    Returns a dictionary with parsed data and metadata.
    """
    with open(filename, "r") as f:
        lines = f.readlines()

    # Verify that the file follows the expected format
    if not lines[0].startswith("/rn"):
        raise ValueError(
            f"File {filename} does not follow the expected 2D uniform grid format"
        )

    # Extract header information
    # First two lines are format indicators
    format_line_1 = lines[0].strip()  # /rn,a,b/nx0
    format_line_2 = lines[1].strip()  # /rn,qa,qb

    # Parse X grid data (third line)
    x_line = lines[2].strip().split()
    nx = int(x_line[0])  # Number of X grid points
    x0 = float(x_line[1])  # X min
    xn = float(x_line[2])  # X max
    z_pos = float(x_line[3])  # Z position
    output_type = x_line[4]  # Output type

    # Handle optional data if present
    optional_data = None
    if len(x_line) > 5:
        # Check for wavelength in the optional data
        for item in x_line[5:]:
            if "=" in item and item.split("=")[0].lower() == "wavelength":
                wavelength = float(item.split("=")[1])
                optional_data = {"wavelength": wavelength}
            # Add more optional parameters as needed

    # Parse Y grid data (fourth line)
    y_line = lines[3].strip().split()
    ny = int(y_line[0])  # Number of Y grid points
    y0 = float(y_line[1])  # Y min
    yn = float(y_line[2])  # Y max

    print(
        f"Header info: Grid points: ({nx}, {ny}), X-Range: [{x0}, {xn}], Y-Range: [{y0}, {yn}], "
        f"Z-position: {z_pos}, Output type: {output_type}"
    )

    # Initialize a 2D matrix to store the complex data
    data_matrix = np.zeros((nx, ny), dtype=complex)

    # Parse the data section (starting from line 4)
    # The data is organized as a 2D grid
    data_lines = lines[4:]

    # Check if there are enough data lines
    if len(data_lines) < nx:
        raise ValueError(
            f"Not enough data rows in file {filename}. Expected {nx}, got {len(data_lines)}"
        )

    # Process each row of data
    for i in range(nx):
        row_data = data_lines[i].strip().split()
        # Check if there are enough columns
        if (
            len(row_data) < ny * 2
        ):  # Each complex number takes 2 values (real and imaginary)
            raise ValueError(
                f"Not enough values in row {i+1}. Expected {ny*2}, got {len(row_data)}"
            )

        # Convert to complex numbers
        for j in range(ny):
            idx = j * 2  # Each complex number consists of two consecutive values
            if idx + 1 < len(row_data):
                real = float(row_data[idx])
                imag = float(row_data[idx + 1])
                data_matrix[i, j] = complex(real, imag)

    # Create result dictionary
    result = {
        "complex_data": data_matrix,
        "data_format": {"format_line_1": format_line_1, "format_line_2": format_line_2},
        "xmin": x0,
        "xmax": xn,
        "ymin": y0,
        "ymax": yn,
        "z_pos": z_pos,
        "output_type": output_type,
        "nx": nx,
        "ny": ny,
    }

    # Add optional data if available
    if optional_data:
        result.update(optional_data)

    return result
