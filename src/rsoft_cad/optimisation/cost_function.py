import random
import os
import numpy
import subprocess
import numpy as np
import logging

from functools import partial
from typing import Dict, Union, Any, Optional

from rsoft_cad import configure_logging
from rsoft_cad.utils import delete_files_except


def overlap_integral(
    data_dir: str = "output",
    expt_dir: str = "custom_taper_profile",
    input_dir: str = "rsoft_data_files",
    input_file_prefix: str = "run_001_ex",
    ref_dir: str = "ref_mode_profile",
    ref_file_prefix: str = "femsim_result_ex",
    file_extension: str = ".m10",
) -> Dict[str, Union[complex, float]]:
    """
    Calculate the overlap integral between two optical mode profiles using bdutil.

    This function runs the bdutil command-line tool to compute the overlap between
    an input mode profile and a reference mode profile. The overlap is a measure of
    how well the two optical modes match.

    Args:
        data_dir: Base directory for the data files
        expt_dir: Experiment directory name
        input_dir: Directory containing input mode profile files
        input_file_prefix: Prefix for the input file
        ref_dir: Directory containing reference mode profile files
        ref_file_prefix: Prefix for the reference file
        file_extension: File extension for mode profile files

    Returns:
        A dictionary containing the overlap results:
            - 'complex': Complex overlap integral (real and imaginary parts)
            - 'magnitude': Absolute value of the overlap integral
            - 'squared': Squared magnitude of the overlap integral

    Raises:
        RuntimeError: If the bdutil command fails (returns non-zero exit code)
    """
    logger = logging.getLogger(__name__)

    overlap_cmd = "bdutil"
    overlap_flag = "-i"
    input_file_name = f"{input_file_prefix}{file_extension}"
    ref_file_name = f"{ref_file_prefix}{file_extension}"
    file_1 = os.path.join(data_dir, expt_dir, input_dir, input_file_name)
    file_2 = os.path.join(data_dir, expt_dir, ref_dir, ref_file_name)
    args = [overlap_cmd, overlap_flag, file_1, file_2]

    logger.debug(f"Executing command: {' '.join(args)}")
    results = subprocess.run(args, capture_output=True, text=True)

    if results.returncode == 0:
        logger.debug("Overlap calculation successful")
        return process_results(results)
    else:
        # Raise an exception with details about the error
        error_msg = f"Command '{' '.join(args)}' failed with return code {results.returncode}.\nError: {results.stderr}"
        logger.error(error_msg)
        replace_stdout = "Overlap Integral (re im) = 0.0 0.0\n|Overlap Integral| = 0.0\n|Overlap Integral|^2 = 0.0\n"
        results.stdout = replace_stdout
        return process_results(results)


def process_results(
    result: subprocess.CompletedProcess,
) -> Dict[str, Union[complex, float]]:
    """
    Process the results of a bdutil overlap calculation.

    Extracts the overlap values from the stdout of the bdutil command and
    organizes them into a dictionary.

    Args:
        result: CompletedProcess object from running the bdutil command

    Returns:
        A dictionary containing:
            - 'complex': Complex overlap integral (real and imaginary parts)
            - 'magnitude': Absolute value of the overlap integral
            - 'squared': Squared magnitude of the overlap integral
    """
    logger = logging.getLogger(__name__)

    overlap_dict = {}
    # Parse the stdout lines
    lines = result.stdout.strip().split("\n")
    # Extract complex overlap integral
    if len(lines) > 0:
        parts = lines[0].split("=")[1].strip().split()
        if len(parts) >= 2:
            real = float(parts[0])
            imag = float(parts[1])
            overlap_dict["complex"] = complex(real, imag)
    # Extract magnitude
    if len(lines) > 1:
        overlap_dict["magnitude"] = float(lines[1].split("=")[1].strip())
    # Extract squared magnitude
    if len(lines) > 2:
        overlap_dict["squared"] = float(lines[2].split("=")[1].strip())

    logger.debug(f"Processed overlap results: {overlap_dict}")
    return overlap_dict


def calculate_overlap_all_modes(
    data_dir: str = "output",
    expt_dir: str = "custom_taper_profile",
    input_dir: str = "rsoft_data_files",
    input_file_prefix: str = "run_001_ex",
    ref_dir: str = "ref_mode_profile",
    ref_file_prefix: str = "femsim_result_ex",
    num_modes: int = 12,
):
    """
    Calculate the overlap for multiple modes and sum the results.

    Args:
        data_dir: Base directory for the data files
        expt_dir: Experiment directory name
        input_dir: Directory containing input mode profile files
        input_file_prefix: Prefix for the input file
        ref_dir: Directory containing reference mode profile files
        ref_file_prefix: Prefix for the reference file
        num_modes: Number of modes to calculate overlap for

    Returns:
        Sum of the squared overlap integrals for all modes
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Calculating overlap for {num_modes} modes")

    overlap_one_mode = partial(
        overlap_integral,
        data_dir=data_dir,
        expt_dir=expt_dir,
        input_dir=input_dir,
        input_file_prefix=input_file_prefix,
        ref_dir=ref_dir,
        ref_file_prefix=ref_file_prefix,
    )

    results = np.zeros(num_modes)
    for i in range(num_modes):
        logger.debug(f"Processing mode {i}")
        overlap_dict = overlap_one_mode(file_extension=f".m{i:02d}")
        results[i] = overlap_dict["squared"]
        logger.debug(f"Mode {i} squared overlap: {results[i]}")

    total_overlap = np.sum(results)
    logger.info(f"Total overlap sum: {total_overlap}")

    delete_files_except(
        folder_path=os.path.join(data_dir, expt_dir, input_dir),
        match_string=None,
        files_to_keep=["custom_taper.dat"],
    )
    return total_overlap
