# io/finders.py
"""
Finders module for RSoft CAD utilities
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import glob
import numpy as np
import shutil


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



def find_files_by_extension(folder_path, extension, include_subfolders=False):
    """
    Find all files with the specified extension in the given folder.

    Parameters:
    folder_path (str): Path to the folder to search in
    extension (str): File extension to search for (e.g., ".nef", ".mon")
                     Can be provided with or without the leading dot
    include_subfolders (bool): If True, search in subfolders as well (recursive search)

    Returns:
    list: List of filenames with the specified extension
    """
    # Ensure extension starts with a dot
    if not extension.startswith("."):
        extension = "." + extension

    if not os.path.isdir(folder_path):
        raise ValueError(f"The path '{folder_path}' is not a valid directory")

    if include_subfolders:
        # Recursive search using os.walk
        matching_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(extension.lower()):
                    matching_files.append(os.path.join(root, file))
    else:
        # Non-recursive search using glob
        matching_files = glob.glob(os.path.join(folder_path, f"*{extension}"))

    return matching_files



