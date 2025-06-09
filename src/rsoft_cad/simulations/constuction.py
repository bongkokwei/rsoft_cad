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
from rsoft_cad.constants import lp_mode_cutoffs_freq
from rsoft_cad.constants import SINGLE_MODE_FIBERS
from rsoft_cad import configure_logging
from rsoft_cad.geometry import create_custom_taper_profile
from rsoft_cad import LaunchType, TaperType
from rsoft_cad.utils import get_fiber_type_list_by_indices, fiber_assignment


def build_parameterised_lantern(
    fiber_indices: List[int],
    lantern_type: str = "mode_selective",  # New parameter with default
    taper_file_name: Optional[str] = None,
    run_name: str = "test_run",
    expt_dir: str = "optimising_expt",
    data_dir: str = "output",
    save_folder: str = "rsoft_data_file",
    highest_mode: str = "LP02",
    launch_mode: str = "LP01",
    taper_factor: float = 1,
    taper_length: float = 50000,
    sigmoid_params: Optional[Dict[str, Any]] = None,
    femnev: int = 12,
    num_grid: int = 200,
    **additional_params: Any,
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Create a photonic lantern with the specified parameters.

    Args:
        fiber_indices: List of integer indices to select fiber types
        lantern_type: Type of lantern to create (default: "mode_selective")
        run_name: Name for this lantern run
        highest_mode: Mode order to simulate (default: "LP02")
        launch_mode: Input mode (default: "LP01")
        taper_factor: Tapering factor for the lantern (default: 1)
        taper_length: Length of taper in microns (default: 50000)
        sigmoid_params: Dictionary containing parameters for taper profile generation and sigmoid function
                     These parameters will be passed to create_custom_taper_profile and sigmoid_taper_ratio
        femnev: Number of effictive indices to look for (default: 12)
        num_grid: Number of grids per axis (default: 200)
        **additional_params: Additional parameters to pass to make_parameterised_lantern

    Returns:
        Tuple containing:
        - filepath: Path to the created lantern file
        - file_name: Name of the created lantern file
        - core_map: Dictionary mapping LP modes to their properties
    """
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating {lantern_type} lantern with run name: {run_name}")

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
            save_folder,
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
                rsoft_data_dir=save_folder,
                taper_func=None,
                file_name=taper_file_name,
                **sigmoid_params,  # Pass the sigmoid parameters
            )

    # Create a dictionary with default parameters
    default_params: Dict[str, Any] = {
        "launch_mode": launch_mode,
        "opt_name": run_name,
        "taper_factor": 1,
        "taper_length": taper_length,
        "sim_type": "femsim",
        "femnev": femnev,
        "save_neff": True,
        "step_x": None,
        "step_y": None,
        "domain_min": 0,
        "data_dir": data_dir,
        "expt_dir": expt_dir,
        "num_grid": num_grid,
        "mode_output": "OUTPUT_REAL_IMAG",
        "taper_config": taper_config_dict,
    }

    # Update with any additional parameters
    default_params.update(additional_params)
    logger.debug(f"Lantern parameters: {default_params}")

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

    # Call the updated make_parameterised_lantern with lantern_type parameter
    filepath, file_name, core_map = make_parameterised_lantern(
        lantern_type=lantern_type,
        highest_mode=highest_mode,  # This goes to lantern_specific_kwargs for mode_selective
        core_dia_dict=fiber_properties["Core_Diameter_micron"],
        cladding_dia_dict=fiber_properties["Cladding_Diameter_micron"],
        cladding_index_dict=fiber_properties["Cladding_Index"],
        core_index_dict=fiber_properties["Core_Index"],
        **default_params,
    )

    logger.info(f"Lantern created at {os.path.join(filepath,file_name)}")

    return filepath, file_name, core_map


def build_and_simulate_lantern(
    fiber_indices: List[int],
    lantern_type: str = "mode_selective",  # New parameter with default
    taper_file_name: Optional[str] = None,
    run_name: str = "test_run",
    highest_mode: str = "LP02",
    launch_mode: str = "LP01",
    taper_factor: float = 1,
    taper_length: float = 50000,
    sim_type: str = "femsim",
    expt_dir: str = "optimising_expt",
    data_dir: str = "output",
    save_folder: str = "rsoft_data_files",
    hide_sim: bool = True,
    final_capillary_id: float = 25,
    num_grid: int = 200,
    ref_folder_name: str = "ideal_modes",
    ref_prefix: str = "ref_LP",
    manual_mode: bool = False,
    **additional_params: Any,
) -> float:
    """
    Create a photonic lantern and run a simulation with the specified parameters.

    Args:
        fiber_indices: List of integer indices to select fiber types
        lantern_type: Type of lantern to create (default: "mode_selective")
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
    logger.info(
        f"Creating and simulating {lantern_type} lantern with run name: {run_name}"
    )

    # Create lantern
    filepath, file_name, core_map = build_parameterised_lantern(
        fiber_indices=fiber_indices,
        lantern_type=lantern_type,
        taper_file_name=taper_file_name,
        run_name=run_name,
        expt_dir=expt_dir,
        data_dir=data_dir,
        save_folder=save_folder,
        highest_mode=highest_mode,
        launch_mode=launch_mode,
        taper_factor=taper_factor,
        taper_length=taper_length,
        sim_type=sim_type,
        final_capillary_id=final_capillary_id,
        num_grid=num_grid,
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
    if not manual_mode:
        from rsoft_cad.optimisation.cost_function import calculate_overlap_all_modes

        # Calculate and return the overlap error
        logger.info(f"Calculating overlap integral")
        overlap_val = calculate_overlap_all_modes(
            data_dir=data_dir,
            expt_dir=expt_dir,
            input_dir=save_folder,
            input_file_prefix=f"{run_name}_ex",
            ref_dir=ref_folder_name,
            ref_file_prefix=ref_prefix,
            num_modes=12,
        )
        logger.info(f"Overlap integral: {overlap_val:.4f}")
    else:
        overlap_val = 0

    return overlap_val
