# Import required libraries
import os
import numpy as np
import json
import logging
import matplotlib.pyplot as plt
from functools import partial
from typing import Union, List, Dict, Tuple, Any, Optional

# Import custom modules
from rsoft_cad.lantern import ModeSelectiveLantern, PhotonicLantern
from rsoft_cad.rsoft_simulations import run_simulation
from rsoft_cad.utils import interpolate_taper_value
from rsoft_cad.geometry import calculate_taper_properties
from rsoft_cad import LaunchType, MonitorType, TaperType


def make_parameterised_lantern(
    lantern_type: str = "mode_selective",
    # Mode Selective Lantern parameters
    highest_mode: str = "LP02",
    # Photonic Lantern parameters
    layer_config: Optional[List[Tuple[int, float]]] = None,
    # Common parameters
    launch_mode: Union[str, List[str]] = "LP01",
    opt_name: str = "run_000",
    taper_factor: float = 21,
    taper_length: float = 80000,
    sim_type: str = "breamprop",
    femnev: int = 1,
    save_neff: bool = True,
    step_x: Optional[float] = None,
    step_y: Optional[float] = None,
    domain_min: float = 0,
    data_dir: str = "output",
    expt_dir: str = "pl_property_scan",
    mode_output: str = "OUTPUT_REAL_IMAG",
    core_dia_dict: Optional[Dict[str, float]] = None,
    cladding_dia_dict: Optional[Dict[str, float]] = None,
    bg_index_dict: Optional[Dict[str, float]] = None,
    cladding_index_dict: Optional[Dict[str, float]] = None,
    core_index_dict: Optional[Dict[str, float]] = None,
    monitor_type: MonitorType = MonitorType.FIBER_POWER,
    launch_type: LaunchType = LaunchType.GAUSSIAN,
    taper_config: Union[TaperType, Dict[str, TaperType]] = TaperType.linear(),
    capillary_od: float = 900,
    final_capillary_id: float = 40,
    num_points: int = 100,
    num_grid: int = 200,
    num_pads: int = 50,
    sort_neff: int = 1,  # [0=none, 1=highest, 2=lowest]
) -> Tuple[str, str, Dict[str, Tuple[float, float]]]:
    """
    Create a parameterised photonic lantern configuration with specified properties.

    This function creates either a Mode Selective Photonic Lantern (MSPL) or a standard
    Photonic Lantern with given parameters, configures the simulation environment,
    writes the design file, and saves the configuration parameters for reproducibility.

    Args:
        lantern_type (str): Type of lantern to create. Options: "mode_selective" or "photonic" (default: "mode_selective")
        highest_mode (str): The highest LP mode to support (for mode_selective lantern) (default: "LP02")
        layer_config (List[Tuple[int, float]] | None): List of tuples (num_circles, scale_factor)
                                                      for each layer (for photonic lantern) (default: None)
        launch_mode (str | List[str]): The mode(s) to launch from (default: "LP01")
        opt_name (str): Name identifier for the run (default: "run_000")
        taper_factor (float): The factor by which the fibers are tapered (default: 21)
        taper_length (float): The length of the taper in microns (default: 80000)
        sim_type (str): Simulation type, either "beamprop" or "femsim" (default: "breamprop")
        femnev (int): Number of eigenmodes to find in FEM simulation (default: 1)
        save_neff (bool): Whether to save effective indices (default: True)
        step_x (float | None): Step size in x-direction. If None, calculated from num_grid (default: None)
        step_y (float | None): Step size in y-direction. If None, calculated from num_grid (default: None)
        domain_min (float): Minimum domain boundary in microns (default: 0)
        data_dir (str): Parent directory for outputs (default: "output")
        expt_dir (str): Sub-directory for experiment outputs (default: "pl_property_scan")
        num_grid (int): Number of grid points for simulation (default: 200)
        mode_output (str): Output format for simulation modes (default: "OUTPUT_REAL_IMAG")
        core_dia_dict (Dict[str, float] | None): Dictionary mapping modes to core diameters (default: None)
        cladding_dia_dict (Dict[str, float] | None): Dictionary mapping modes to cladding diameters (default: None)
        bg_index_dict (Dict[str, float] | None): Dictionary mapping modes to background indices (default: None)
        cladding_index_dict (Dict[str, float] | None): Dictionary mapping modes to cladding indices (default: None)
        core_index_dict (Dict[str, float] | None): Dictionary mapping modes to core indices (default: None)
        monitor_type: Type of monitor to add to each pathway. Defaults to FIBER_POWER.
        taper_config: Taper profile to use if tapering is applied. Defaults to LINEAR.
        launch_type: Type of field distribution to launch. Defaults to GAUSSIAN.
        capillary_od (float): Outer diameter of the capillary in microns (default: 900)
        final_capillary_id (float): Final inner diameter of the capillary after tapering in microns (default: 40)
        num_points (int): Number of points along z-axis for model discretization (default: 100)
        num_pads (int): Number of padding grid points (default: 50)
        sort_neff (int): Eigenmode sorting option [0=none, 1=highest, 2=lowest] (default: 1)

    Returns:
        Tuple[str, str, Dict[str, Tuple[float, float]]]: A tuple containing:
            - filepath (str): Path to the directory containing the generated design file
            - file_name (str): Name of the generated design file
            - core_map (Dict[str, Tuple[float, float]]): Mapping of modes to their spatial coordinates

    Raises:
        ValueError: If an invalid simulation type or lantern type is provided
        ValueError: If required parameters for the selected lantern type are missing
    """

    # Set up logger
    logger = logging.getLogger(__name__)

    logger.info(f"Creating parameterised {lantern_type} lantern with name: {opt_name}")

    # Validate simulation type
    if sim_type == "beamprop":
        sim_string = "ST_BEAMPROP"
    elif sim_type == "femsim":
        sim_string = "ST_FEMSIM"
    else:
        logger.error(
            f"Invalid simulation type: {sim_type}. Expected 'femsim' or 'beamprop'."
        )
        raise ValueError(
            f"Invalid simulation type: {sim_type}. Expected 'femsim' or 'beamprop'."
        )

    # Validate lantern type and create appropriate instance
    if lantern_type.lower() == "mode_selective":
        lantern = ModeSelectiveLantern()
        logger.debug("Created ModeSelectiveLantern instance")

        # Create lantern without writing to design file
        logger.debug(
            f"Creating mode selective lantern with highest_mode={highest_mode}, launch_mode={launch_mode}"
        )
        core_map = lantern.create_lantern(
            highest_mode=highest_mode,
            launch_mode=launch_mode,
            opt_name=opt_name,
            savefile=False,  # Hold off on saving design file
            taper_factor=taper_factor,
            taper_length=taper_length,
            core_dia_dict=core_dia_dict,
            cladding_dia_dict=cladding_dia_dict,
            bg_index_dict=bg_index_dict,
            cladding_index_dict=cladding_index_dict,
            core_index_dict=core_index_dict,
            monitor_type=monitor_type,
            launch_type=launch_type,
            taper_config=taper_config,
            capillary_od=capillary_od,
            final_capillary_id=final_capillary_id,
            num_points=num_points,
        )

    elif lantern_type.lower() == "photonic":
        if layer_config is None:
            logger.error("layer_config is required for photonic lantern type")
            raise ValueError("layer_config is required for photonic lantern type")

        lantern = PhotonicLantern()
        logger.debug("Created PhotonicLantern instance")

        # For photonic lantern, launch_mode default should be "0" if it's still "LP01"
        if launch_mode == "LP01":
            launch_mode = "0"
            logger.debug("Changed launch_mode from 'LP01' to '0' for photonic lantern")

        # Create lantern without writing to design file
        logger.debug(
            f"Creating photonic lantern with layer_config={layer_config}, launch_mode={launch_mode}"
        )
        core_map = lantern.create_lantern(
            layer_config=layer_config,
            launch_mode=launch_mode,
            opt_name=opt_name,
            savefile=False,  # Hold off on saving design file
            taper_factor=taper_factor,
            taper_length=taper_length,
            core_diameters=core_dia_dict,  # Note: different parameter name for photonic lantern
            core_dia_dict=core_dia_dict,
            cladding_dia_dict=cladding_dia_dict,
            bg_index_dict=bg_index_dict,
            cladding_index_dict=cladding_index_dict,
            core_index_dict=core_index_dict,
            monitor_type=monitor_type,
            launch_type=launch_type,
            taper_config=taper_config,
            capillary_od=capillary_od,
            final_capillary_id=final_capillary_id,
            num_points=num_points,
        )

    else:
        logger.error(
            f"Invalid lantern type: {lantern_type}. Expected 'mode_selective' or 'photonic'."
        )
        raise ValueError(
            f"Invalid lantern type: {lantern_type}. Expected 'mode_selective' or 'photonic'."
        )

    logger.debug(f"Lantern created with {len(core_map)} cores")

    # Calculate simulation boundaries based on capillary diameter
    if taper_factor > 1:  # backwards compatibility
        (dia_at_pos, _, taper_factor, _) = calculate_taper_properties(
            position=domain_min,
            start_dia=lantern.cap_dia,
            end_dia=None,
            taper_factor=taper_factor,
            taper_length=taper_length,
        )
    else:
        dia_at_pos = interpolate_taper_value(
            lantern.model,
            "capillary_inner_diameter",
            z_pos=domain_min,
        )
    core_pos_x = 0
    core_pos_y = 0

    # To prevent super fine features
    boundary_max = np.ceil(core_pos_x + (dia_at_pos / 2))
    boundary_min = np.floor(core_pos_x - (dia_at_pos / 2))
    boundary_max_y = np.ceil(core_pos_y + (dia_at_pos / 2))
    boundary_min_y = np.floor(core_pos_y - (dia_at_pos / 2))

    grid_size_x = step_x if step_x is not None else (2 * boundary_max) / num_grid
    grid_size_y = step_y if step_y is not None else (2 * boundary_max_y) / num_grid

    logger.debug(f"Grid sizes calculated: x={grid_size_x}, y={grid_size_y}")

    # some glitch in the software, lantern is not centered, have to pad it to prevent clipping
    boundary_min_y -= int(num_pads * 1.5) * grid_size_y
    boundary_max_y += num_pads * grid_size_y
    boundary_min -= num_pads * grid_size_x
    boundary_max += num_pads * grid_size_x

    # Simulation parameters
    sim_params = {
        "boundary_max": boundary_max,
        "boundary_min": boundary_min,
        "boundary_max_y": boundary_max_y,
        "boundary_min_y": boundary_min_y,
        "domain_min": domain_min,
        "grid_size": grid_size_x,
        "grid_size_y": grid_size_y,
        "grid_align_x": 1,
        "grid_align_y": 1,
        "sim_tool": sim_string,
        "fem_nev": femnev,  # Find more eigenmodes
        "fem_neff_seeding": int(save_neff),
        "mode_output_format": mode_output,
        "slice_display_mode": "DISPLAY_CONTOURMAPXY",
        "field_output_format": "OUTPUT_REAL_IMAG",
        "mode_launch_type": 2,
        "cad_aspectratio_x": 50,
        "cad_aspectratio_y ": 50,
        "fem_outh": 0,
        "fem_outs": 0,
        "fem_plot_mesh": 0,
        "fem_save_meshfile": 0,
        "fem_leaky": 1,
        "fem_float": 0,
        "fem_sortev": sort_neff,
    }

    # Update global simulation parameters
    lantern.update_global_params(**sim_params)

    # Generate filename
    file_name = f"{sim_type}_{lantern.design_filename}"
    filepath = os.path.join(data_dir, expt_dir)
    design_filename = os.path.join(filepath, file_name)

    # Create directory if it doesn't exist
    os.makedirs(filepath, exist_ok=True)

    # Write design file
    logger.info(f"Writing design file to {design_filename}")
    lantern.write(design_filename)

    # Save the input parameters to a file
    params = {
        "lantern_type": lantern_type,
        "boundary_max": boundary_max,
        "boundary_min": boundary_min,
        "boundary_max_y": boundary_max_y,
        "boundary_min_y": boundary_min_y,
        "domain_min": domain_min,
        "grid_size": grid_size_x,
        "grid_size_y": grid_size_y,
        "launch_mode": launch_mode,
        "opt_name": opt_name,
        "taper_factor": taper_factor,
        "taper_length": taper_length,
        "sim_type": sim_type,
        "femnev": femnev,
        "save_neff": save_neff,
        "step_x": step_x,
        "step_y": step_y,
        "domain_min": domain_min,
        "data_dir": data_dir,
        "expt_dir": expt_dir,
        "num_grid": num_grid,
    }

    # Add lantern-specific parameters
    if lantern_type.lower() == "mode_selective":
        params["highest_mode"] = highest_mode
    elif lantern_type.lower() == "photonic":
        params["layer_config"] = layer_config

    # Generate params filename
    params_filename = os.path.join(data_dir, expt_dir, f"params_{opt_name}.json")

    # Write parameters to file
    logger.info(f"Saving parameters to {params_filename}")
    with open(params_filename, "w") as f:
        json.dump(params, f, indent=4)

    logger.info(f"Lantern creation complete: {file_name}")

    return filepath, file_name, core_map


if __name__ == "__main__":

    # Example 1: Mode Selective Lantern
    mode_selective_lantern = partial(
        make_parameterised_lantern,
        lantern_type="mode_selective",
        highest_mode="LP02",
        launch_mode="LP01",
        taper_factor=1,  # final diameter of 19 micron
        sim_type="femsim",
        femnev=6,
        taper_length=50000,
        expt_dir="mode_selective_test",
        taper_config={
            "core": TaperType.exponential(),
            "cladding": TaperType.exponential(),
            "cap": TaperType.exponential(),
        },
    )

    mode_selective_lantern(domain_min=25000, opt_name="mspl_test_run")

    # Example 2: Photonic Lantern
    photonic_lantern = partial(
        make_parameterised_lantern,
        lantern_type="photonic",
        layer_config=[
            (1, 1.0),  # Center layer: 1 circle at center
            (6, 1.0),  # First ring: 6 circles
            (12, 1.0),  # Second ring: 12 circles
        ],
        launch_mode="0",  # Note: different default for photonic lantern
        taper_factor=1,
        sim_type="femsim",
        femnev=6,
        taper_length=50000,
        expt_dir="photonic_test",
        taper_config={
            "core": TaperType.exponential(),
            "cladding": TaperType.exponential(),
            "cap": TaperType.exponential(),
        },
    )

    photonic_lantern(domain_min=25000, opt_name="pl_test_run")
