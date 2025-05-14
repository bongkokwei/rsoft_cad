import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import textwrap
import logging
import os
import random

from typing import Dict, List, Any, Tuple, Optional
from functools import partial

from rsoft_cad.simulations import make_parameterised_lantern
from rsoft_cad.layout import create_core_map
from rsoft_cad.rsoft_simulations import run_simulation
from rsoft_cad.utils import visualise_lp_lantern
from rsoft_cad.constants import lp_mode_cutoffs_freq
from rsoft_cad.constants import SINGLE_MODE_FIBERS
from rsoft_cad import configure_logging
from rsoft_cad.geometry import sigmoid_taper_ratio, create_custom_taper_profile
from rsoft_cad import LaunchType, TaperType


def get_fiber_type_list_by_indices(
    smf_df: pd.DataFrame, indices: List[int]
) -> List[str]:
    """
    Return a list of fiber types based on DataFrame row indices.

    Args:
        smf_df: DataFrame containing fiber specifications
        indices: List of row indices in the DataFrame

    Returns:
        List of fiber type strings corresponding to the indices
    """
    fiber_types = []

    for idx in indices:
        if 0 <= idx < len(smf_df):
            fiber_types.append(smf_df.iloc[idx]["Fiber_Type"])
        else:
            raise ValueError(
                f"Index {idx} is out of bounds for DataFrame with {len(smf_df)} rows"
            )

    return fiber_types


def print_dict(
    dict_obj: Dict[str, Any],
    width: int = 80,
    indent: int = 4,
) -> None:
    """
    Print a dictionary with indented values.

    Args:
        dict_obj: Dictionary to print
        width: Width of the separator line
        indent: Number of spaces to use for indentation
    """
    for key, value in dict_obj.items():
        print(f"{key}: ")
        print(textwrap.indent(str(value), " " * indent))
    print("=" * width)


def fiber_assignment(
    core_map: Dict[str, Any],
    fiber_type_list: List[str],
    smf_df: pd.DataFrame,
    columns_to_include: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Assign fiber properties to each core in the core map for all or selected columns.

    Args:
        core_map: Dictionary mapping LP modes to their properties
        fiber_type_list: List of fiber types to assign to cores
        smf_df: DataFrame containing fiber specifications
        columns_to_include: If provided, only process these columns. If None, process all columns.

    Returns:
        Dictionary where:
        - Keys are column names from the DataFrame
        - Values are dictionaries mapping LP modes to their respective property values
    """
    # Create a dictionary to hold all property dictionaries
    property_dicts: Dict[str, Dict[str, Any]] = {}

    # Determine which columns to process
    cols_to_process = columns_to_include if columns_to_include else smf_df.columns

    # Initialize a dictionary for each column
    for column in cols_to_process:
        if column in smf_df.columns:  # Ensure column exists
            property_dicts[column] = {}

    for i, (key, _) in enumerate(core_map.items()):
        if i < len(fiber_type_list):
            # Get the fiber type for this core
            fiber_type = fiber_type_list[i]
            # Find the row with this fiber type
            fiber_data = smf_df[smf_df["Fiber_Type"] == fiber_type]

            if not fiber_data.empty:
                # For each column, add the value to the corresponding property dictionary
                for column in cols_to_process:
                    if column in fiber_data.columns:
                        property_dicts[column][key] = fiber_data[column].values[0]

    return property_dicts


def build_parameterised_lantern(
    fiber_indices: List[int],
    taper_file_name: Optional[str] = None,
    run_name: str = "test_run",
    expt_dir: str = "optimising_expt",
    data_dir: str = "output",
    highest_mode: str = "LP02",
    launch_mode: str = "LP01",
    taper_factor: float = 1,
    taper_length: float = 50000,
    sigmoid_params: Optional[Dict[str, Any]] = None,
    **additional_params: Any,
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Create a photonic lantern with the specified parameters.

    Args:
        fiber_indices: List of integer indices to select fiber types
        run_name: Name for this lantern run
        highest_mode: Mode order to simulate (default: "LP02")
        launch_mode: Input mode (default: "LP01")
        taper_factor: Tapering factor for the lantern (default: 18.75)
        taper_length: Length of taper in microns (default: 40000)
        sigmoid_params: Dictionary containing parameters for taper profile generation and sigmoid function
                     These parameters will be passed to create_custom_taper_profile and sigmoid_taper_ratio
        **additional_params: Additional parameters to pass to make_parameterised_lantern

    Returns:
        Tuple containing:
        - filepath: Path to the created lantern file
        - file_name: Name of the created lantern file
        - core_map: Dictionary mapping LP modes to their properties
    """
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating lantern with run name: {run_name}")

    # Initialize sigmoid_params if None
    if sigmoid_params is None:
        sigmoid_params = {}

    if taper_file_name is None:
        taper_config_dict = {
            "core": TaperType.linear(),
            "cladding": TaperType.linear(),
            "cap": TaperType.linear(),
        }
    else:
        # Check if the taper_file_name exists in the expected locations
        taper_config_dict = {
            "core": TaperType.user(1, taper_file_name),
            "cladding": TaperType.user(1, taper_file_name),
            "cap": TaperType.user(1, taper_file_name),
        }

        taper_file_path = os.path.join(
            data_dir,
            expt_dir,
            taper_file_name,
        )
        taper_file_path_rsoft = os.path.join(
            data_dir,
            expt_dir,
            "rsoft_data_files",
            taper_file_name,
        )

        files_exist = os.path.exists(
            taper_file_path,
        ) or os.path.exists(
            taper_file_path_rsoft,
        )

        if not files_exist:
            logger.warning(
                f"Taper file '{taper_file_name}' does not exist at either "
                f"{taper_file_path} or {taper_file_path_rsoft}. "
                f"It will be created now."
            )

            # Create the custom taper profile
            z, ratios = create_custom_taper_profile(
                data_dir=data_dir,
                expt_dir=expt_dir,
                rsoft_data_dir="rsoft_data_files",
                taper_func=None,
                file_name=taper_file_name,
                **sigmoid_params,  # Pass the sigmoid parameters
            )

    # Create a dictionary with default parameters
    default_params: Dict[str, Any] = {
        "highest_mode": highest_mode,
        "launch_mode": launch_mode,
        "opt_name": run_name,
        "taper_factor": 1,
        "taper_length": taper_length,
        "sim_type": "femsim",
        "femnev": 12,
        "save_neff": True,
        "step_x": None,
        "step_y": None,
        "domain_min": 0,
        "data_dir": data_dir,
        "expt_dir": expt_dir,
        "num_grid": 200,
        "mode_output": "OUTPUT_NONE",
        "taper_config": taper_config_dict,
    }

    # Update with any additional parameters
    default_params.update(additional_params)
    logger.debug(f"Lantern parameters: {default_params}")

    # Create partial function with updated parameters
    lantern_func = partial(make_parameterised_lantern, **default_params)

    # Create core map
    core_map, _ = create_core_map(highest_mode, 125)
    logger.debug(f"Core map created for {highest_mode}")

    # Read fiber data and get fiber types
    smf_df = pd.DataFrame(SINGLE_MODE_FIBERS)
    fiber_types = get_fiber_type_list_by_indices(smf_df, fiber_indices)
    logger.info(f"Selected fiber types: {fiber_types}")

    # Assign fiber properties
    fiber_properties = fiber_assignment(core_map, fiber_types, smf_df)
    logger.debug(f"Fiber properties assigned: {list(fiber_properties.keys())}")

    # Create lantern object
    filepath, file_name, core_map = lantern_func(
        opt_name=run_name,
        core_dia_dict=fiber_properties["Core_Diameter_micron"],
        cladding_dia_dict=fiber_properties["Cladding_Diameter_micron"],
        cladding_index_dict=fiber_properties["Cladding_Index"],
        core_index_dict=fiber_properties["Core_Index"],
    )

    logger.info(f"Lantern created at {os.path.join(filepath,file_name)}")

    return filepath, file_name, core_map


def build_and_simulate_lantern(
    fiber_indices: List[int],
    taper_file_name: Optional[str] = None,
    run_name: str = "test_run",
    highest_mode: str = "LP02",
    launch_mode: str = "LP01",
    taper_factor: float = 18.75,
    taper_length: float = 40000,
    sim_type: str = "femsim",
    expt_dir: str = "optimising_expt",
    data_dir: str = "output",
    save_folder: str = "rsoft_data_files",
    hide_sim: bool = True,
    **additional_params: Any,
) -> float:
    """
    Create a photonic lantern and run a simulation with the specified parameters.

    Args:
        fiber_indices: List of integer indices to select fiber types
        run_name: Name for this lantern run
        highest_mode: Mode order to simulate (default: "LP02")
        launch_mode: Input mode (default: "LP01")
        taper_factor: Tapering factor for the lantern (default: 18.75)
        taper_length: Length of taper in microns (default: 40000)
        sim_type: Simulation type (default: "femsim")
        save_folder: Folder to save simulation results (default: "rsoft_data_files")
        hide_sim: Whether to hide simulation GUI (default: True)
        **additional_params: Additional parameters to pass to make_parameterised_lantern

    Returns:
        Float: Overlap integral value
    """
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating and simulating lantern with run name: {run_name}")

    # Create lantern
    filepath, file_name, core_map = build_parameterised_lantern(
        fiber_indices=fiber_indices,
        taper_file_name=taper_file_name,
        run_name=run_name,
        expt_dir=expt_dir,
        data_dir=data_dir,
        highest_mode=highest_mode,
        launch_mode=launch_mode,
        taper_factor=taper_factor,
        taper_length=taper_length,
        sim_type=sim_type,
        **additional_params,
    )

    # Run simulation
    results = run_simulation(
        filepath,
        file_name,
        sim_type,
        prefix_name=run_name,
        save_folder=save_folder,
        hide_sim=hide_sim,
    )

    # Calculate and return the overlap error
    logger.info(f"Calculating overlap integral")
    overlap_val = calculate_overlap(file_name)
    logger.info(f"Overlap integral: {overlap_val:.4f}")

    return overlap_val


def calculate_overlap(filename):
    # Placeholder for your overlap calculation
    # Assume this function takes the simulation filename and returns a normalized overlap value (0 to 1)
    # For demonstration, let's return a random value
    return random.random()
