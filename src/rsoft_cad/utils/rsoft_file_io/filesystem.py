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
import logging

from .finders import find_files_by_extension


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


def copy_files_by_extension(expt_dir, extension, include_subfolders=True):
    """
    Finds files with a specific extension in a source folder and copies them to a destination folder.

    Args:
        expt_dir (str): Experiment directory name
        extension (str): File extension to search for (e.g. ".nef")
        include_subfolders (bool, optional): Whether to search subfolders. Defaults to True.

    Returns:
        list: List of copied file paths
    """
    # Set up the source and destination folders
    source_folder = os.path.join(
        "output",
        expt_dir,
        "rsoft_data_files",
    )

    destination_folder = os.path.join(
        "output",
        expt_dir,
        "rsoft_data_files",
        "nef_folder",
    )

    # Step 1: Find the files
    files_to_copy = find_files_by_extension(
        source_folder, extension, include_subfolders=include_subfolders
    )

    # Step 2: Copy the files
    copied_files = copy_files_to_destination(files_to_copy, destination_folder)

    # Step 3: Print summary
    print(f"Copied {len(copied_files)} files to {destination_folder}")
    for file in copied_files:
        print(f"  - {file}")

    return copied_files


def delete_files_except(
    folder_path,
    match_string=None,
    files_to_keep=None,
):
    """
    Delete all files in a folder except those that contain a specific string
    or are in the list of files to keep.

    Args:
        folder_path (str): Path to the folder containing files
        match_string (str, optional): Files containing this string will be kept
        files_to_keep (list, optional): List of specific filenames to keep
    """
    logger = logging.getLogger(__name__)

    if files_to_keep is None:
        files_to_keep = []

    # Ensure folder path exists
    if not os.path.exists(folder_path):
        logger.error(f"Folder '{folder_path}' does not exist.")
        return

    # Get list of all files in the folder
    files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    # Counter for deleted files
    deleted_count = 0

    logger.info(f"Cleaning directory: {folder_path}")
    logger.debug(f"Keeping files with pattern: {match_string}")
    logger.debug(f"Keeping specific files: {files_to_keep}")

    # Process each file
    for file in files:
        # Check if file should be kept
        keep_file = False

        # Check if file contains the match string
        if match_string and match_string in file:
            keep_file = True

        # Check if file is in the list of files to keep
        if file in files_to_keep:
            keep_file = True

        # Delete file if it doesn't meet the criteria to keep
        if not keep_file:
            file_path = os.path.join(folder_path, file)
            try:
                os.remove(file_path)
                logger.debug(f"Deleted: {file}")
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting {file}: {e}")

    logger.info(f"Total files deleted: {deleted_count}")
