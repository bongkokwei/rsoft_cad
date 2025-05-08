import re
import os
import subprocess
import logging
from typing import Optional, Union, List, Dict, Any
from subprocess import CompletedProcess


def run_simulation(
    design_filepath: str,
    design_filename: str,
    sim_package: str,
    prefix_name: str,
    save_folder: str = "launch_files",
    hide_sim: bool = True,
) -> CompletedProcess:
    """
    Run simulation for the specified design file and launch mode.

    This function executes a simulation for a given photonic lantern design file using the specified
    simulation package. It creates a target directory for simulation results if it doesn't exist,
    changes to that directory to run the simulation, and then returns to the original directory.

    Args:
        design_filepath (str): Path to the directory containing the design file
        design_filename (str): Name of the design file to simulate
        sim_package (str): Simulation package to use (e.g., 'femsim' or 'bsimw32')
        prefix_name (str): Prefix to use for output files
        save_folder (str): Folder name to save simulation results (default: "launch_files")
        hide_sim (bool): Whether to hide the simulation window (default: True)

    Returns:
        CompletedProcess: Result of the simulation process, containing stdout, stderr, and return code

    Raises:
        OSError: If there are issues creating directories or changing working directory
        subprocess.SubprocessError: If the simulation process fails to execute
    """
    # Set up logger
    logger = logging.getLogger(__name__)

    logger.info(f"Starting simulation for design: {design_filename}")
    logger.debug(
        f"Simulation parameters: package={sim_package}, prefix={prefix_name}, hide={hide_sim}"
    )

    # Save simulation results to this directory
    target_dir = os.path.join(design_filepath, save_folder)
    logger.debug(f"Target directory for simulation results: {target_dir}")

    # Create the folder if it doesn't exist
    if not os.path.exists(target_dir):
        logger.debug(f"Creating folder: {target_dir}")
        os.makedirs(target_dir)

    # Store original directory to return to later
    original_dir = os.getcwd()
    logger.debug(f"Current working directory: {original_dir}")

    # Construct command arguments based on hide_sim
    command_args = [sim_package]
    if hide_sim:
        command_args.append("-hide")
    command_args.extend([os.path.join("..", design_filename), f"prefix={prefix_name}"])

    logger.debug(f"Command to execute: {' '.join(command_args)}")

    # Change to the target directory
    logger.debug(f"Changing directory to: {target_dir}")
    os.chdir(target_dir)

    # Run the simulation
    logger.info(f"Executing simulation with prefix: {prefix_name}")
    result = subprocess.run(
        command_args,
        capture_output=True,
        text=True,
    )

    # Log the result status
    if result.returncode == 0:
        logger.info(f"Simulation completed successfully")
    else:
        logger.error(f"Simulation failed with return code: {result.returncode}")
        logger.debug(f"Error output: {result.stderr}")

    # Change back to the original directory
    logger.debug(f"Changing back to original directory: {original_dir}")
    os.chdir(original_dir)

    return result


def rename_component_files(directory, file_prefix="femsim", dry_run=False):
    """
    Renames files by moving component indicators (ex, ey, ez, etc.) from the end to the beginning.

    Args:
        directory (str): The directory containing files to rename
        file_prefix (str): The prefix of files to process (default: "femsim")
        dry_run (bool): If True, only show what would be renamed without actually renaming

    Returns:
        list: List of tuples containing (old_filename, new_filename) for renamed files
    """
    # Make sure directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"Directory not found: {directory}")

    # Pattern to match files with component indicators
    pattern = re.compile(rf"{file_prefix}_(.+?)_(ex|ey|ez|hx|hy|hz|sz)(\..*)?$")

    renamed_files = []

    # List all files in the directory
    files = os.listdir(directory)

    # Process each file
    for filename in files:
        # Check if the file matches our pattern
        match = pattern.search(filename)
        if match:
            base_name = match.group(1)  # LP01, LP02, etc.
            component = match.group(2)  # ex, ey, ez, hx, hy, hz, sz
            extension = (
                match.group(3) if match.group(3) else ""
            )  # File extension including the dot

            # Create the new filename with component at the beginning
            new_filename = f"{component}_{file_prefix}_{base_name}{extension}"

            # Full paths for old and new filenames
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)

            # Add to list of renamed files
            renamed_files.append((filename, new_filename))

            # Rename the file
            print(f"Renaming: {filename} -> {new_filename}")
            if not dry_run:
                os.rename(old_path, new_path)

    if not renamed_files:
        print(
            f"No files matching pattern '{file_prefix}_*_(ex|ey|ez|hx|hy|hz|sz)' found in {directory}"
        )
    elif dry_run:
        print(f"Dry run complete! {len(renamed_files)} files would be renamed.")
    else:
        print(f"Renaming complete! {len(renamed_files)} files were renamed.")

    return renamed_files


import shutil


def copy_component_files(
    directory,
    file_prefix="femsim",
    output_directory=None,
    dry_run=False,
):
    """
    Copies files and moves component indicators (ex, ey, ez, etc.) from the end to the beginning.
    Original files are preserved.

    Args:
        directory (str): The directory containing files to process
        file_prefix (str): The prefix of files to process (default: "femsim")
        output_directory (str): Directory to save new files (default: same as source directory)
        dry_run (bool): If True, only show what would be copied without actually copying

    Returns:
        list: List of tuples containing (old_filename, new_filename) for copied files
    """
    # Make sure directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"Directory not found: {directory}")

    # If output directory not specified, use the same directory
    if output_directory is None:
        output_directory = directory

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory) and not dry_run:
        os.makedirs(output_directory)

    # Pattern to match files with component indicators
    pattern = re.compile(rf"{file_prefix}_(.+?)_(ex|ey|ez|hx|hy|hz|sz)(\..*)?$")

    copied_files = []

    # List all files in the directory
    files = os.listdir(directory)

    # Process each file
    for filename in files:
        # Check if the file matches our pattern
        match = pattern.search(filename)
        if match:
            base_name = match.group(1)  # LP01, LP02, etc.
            component = match.group(2)  # ex, ey, ez, hx, hy, hz, sz
            extension = (
                match.group(3) if match.group(3) else ""
            )  # File extension including the dot

            # Create the new filename with component at the beginning
            new_filename = f"{component}_{file_prefix}_{base_name}{extension}"

            # Full paths for old and new filenames
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(output_directory, new_filename)

            # Add to list of copied files
            copied_files.append((filename, new_filename))

            # Copy the file
            print(f"Copying: {filename} -> {new_filename}")
            if not dry_run:
                shutil.copy2(old_path, new_path)  # copy2 preserves metadata

    if not copied_files:
        print(
            f"No files matching pattern '{file_prefix}_*_(ex|ey|ez|hx|hy|hz|sz)' found in {directory}"
        )
    elif dry_run:
        print(f"Dry run complete! {len(copied_files)} files would be copied.")
    else:
        print(
            f"Copying complete! {len(copied_files)} files were copied to {output_directory}"
        )

    return copied_files
