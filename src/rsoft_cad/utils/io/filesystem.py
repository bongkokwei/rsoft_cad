# io/filesystem.py
"""
Filesystem module for RSoft CAD utilities
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import glob
import numpy as np
import shutil


def copy_files_to_destination(file_list, destination_folder):
    """
    Copy a list of files to a destination folder.

    Parameters:
    file_list (list): List of file paths to copy
    destination_folder (str): Path to the folder where files will be copied

    Returns:
    list: List of paths of copied files
    """
    # Create destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    copied_files = []

    for file_path in file_list:
        if os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(destination_folder, file_name)

            # Copy the file
            shutil.copy2(file_path, destination_path)
            copied_files.append(destination_path)

    return copied_files


def get_next_run_folder(folder_path, prefix):
    """
    Find all folders with the given prefix in the specified path,
    identify the maximum run number, and return the next run folder name.

    Args:
        folder_path (str): Path to the directory to search in
        prefix (str): Prefix of the folders to search for

    Returns:
        str: Next run folder name in the format 'run_XXX' where XXX is the next number
    """
    max_run = 0

    # Check if the folder path exists
    if not os.path.exists(folder_path):
        raise ValueError(f"The folder path '{folder_path}' does not exist")

    # Get all directories in the folder path
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # Check if it's a directory and starts with the prefix
        if os.path.isdir(item_path) and item.startswith(prefix):
            # Try to extract the run number
            try:
                # Extract the part after the prefix
                run_part = item[len(prefix) :]
                # Convert to integer
                run_number = int(run_part)
                # Update max_run if this is larger
                max_run = max(max_run, run_number)
            except (ValueError, IndexError):
                # If we can't convert to an integer, skip this directory
                continue

    # Return the next run number formatted as 'run_XXX'
    return f"{prefix}{max_run + 1:03d}"



