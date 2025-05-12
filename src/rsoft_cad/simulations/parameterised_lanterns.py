# Import required libraries
import os
import numpy as np
import json
import logging
import matplotlib.pyplot as plt
from functools import partial

# Import custom modules
from rsoft_cad.lantern import ModeSelectiveLantern

# from rsoft_cad.rsoft_mspl import ModeSelectiveLantern
from rsoft_cad.rsoft_simulations import run_simulation
from rsoft_cad.utils import visualise_lantern
from rsoft_cad.geometry import calculate_taper_properties
from rsoft_cad import LaunchType, MonitorType, TaperType


def make_parameterised_lantern(
    highest_mode: str = "LP02",
    launch_mode: str | list[str] = "LP01",
    opt_name: str = "run_000",
    taper_factor: float = 21,
    taper_length: float = 80000,
    sim_type: str = "breamprop",
    femnev: int = 1,
    save_neff: bool = True,
    step_x: float | None = None,
    step_y: float | None = None,
    domain_min: float = 0,
    data_dir: str = "output",
    expt_dir: str = "pl_property_scan",
    num_grid: int = 400,
    mode_output: str = "OUTPUT_REAL_IMAG",
    core_dia_dict: dict[str, float] | None = None,
    cladding_dia_dict: dict[str, float] | None = None,
    bg_index_dict: dict[str, float] | None = None,
    cladding_index_dict: dict[str, float] | None = None,
    core_index_dict: dict[str, float] | None = None,
    monitor_type: MonitorType = MonitorType.FIBER_POWER,
    launch_type: LaunchType = LaunchType.GAUSSIAN,
    taper_config: TaperType | dict[str, TaperType] = TaperType.linear(),
) -> tuple[str, str, dict[str, tuple[float, float]]]:
    """
    Create a parameterised photonic lantern configuration with specified properties.

    This function creates a Mode Selective Photonic Lantern (MSPL) with given parameters,
    configures the simulation environment, writes the design file, and saves the configuration
    parameters for reproducibility.

    Args:
        highest_mode (str): The highest LP mode to support (default: "LP02")
        launch_mode (str | list[str]): The mode(s) to launch from (default: "LP01")
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
        num_grid (int): Number of grid points for simulation (default: 400)
        mode_output (str): Output format for simulation modes (default: "OUTPUT_REAL_IMAG")
        core_dia_dict (dict[str, float] | None): Dictionary mapping modes to core diameters (default: None)
        cladding_dia_dict (dict[str, float] | None): Dictionary mapping modes to cladding diameters (default: None)
        bg_index_dict (dict[str, float] | None): Dictionary mapping modes to background indices (default: None)
        cladding_index_dict (dict[str, float] | None): Dictionary mapping modes to cladding indices (default: None)
        core_index_dict (dict[str, float] | None): Dictionary mapping modes to core indices (default: None)
        monitor_type: Type of monitor to add to each pathway. Defaults to FIBER_POWER.
        taper_type: Taper profile to use if tapering is applied. Defaults to LINEAR.
        launch_type: Type of field distribution to launch. Defaults to GAUSSIAN.


    Returns:
        tuple[str, str, dict[str, tuple[float, float]]]: A tuple containing:
            - filepath (str): Path to the directory containing the generated design file
            - file_name (str): Name of the generated design file
            - core_map (dict[str, tuple[float, float]]): Mapping of modes to their spatial coordinates

    Raises:
        ValueError: If an invalid simulation type is provided
    """

    # Set up logger
    logger = logging.getLogger(__name__)

    logger.info(f"Creating parameterised lantern with name: {opt_name}")

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

    # Create Mode Selective Photonic Lantern instance
    mspl = ModeSelectiveLantern()
    logger.debug("Created ModeSelectiveLantern instance")

    # Create lantern without writing to design file
    logger.debug(
        f"Creating lantern with highest_mode={highest_mode}, launch_mode={launch_mode}"
    )
    core_map = mspl.create_lantern(
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
    )
    logger.debug(f"Lantern created with {len(core_map)} cores")

    # Calculate simulation boundaries based on capillary diameter
    (dia_at_pos, _, taper_factor, _) = calculate_taper_properties(
        position=domain_min,
        start_dia=mspl.cap_dia,
        end_dia=None,
        taper_factor=taper_factor,
        taper_length=taper_length,
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
    boundary_min_y -= 10 * grid_size_y
    boundary_max_y += 10 * grid_size_y
    boundary_min -= 10 * grid_size_x
    boundary_max += 10 * grid_size_x

    # Simulation parameters
    sim_params = {
        "boundary_max": boundary_max,
        "boundary_min": boundary_min,
        "boundary_max_y": boundary_max_y,
        "boundary_min_y": boundary_min_y,
        "domain_min": domain_min,
        "grid_size": grid_size_x,
        "grid_size_y": grid_size_y,
        "sim_tool": sim_string,
        "fem_nev": femnev,  # Find more eigenmodes
        "fem_neff_seeding": int(save_neff),
        "mode_output_format": mode_output,
        "slice_display_mode": "DISPLAY_CONTOURMAPXY",
        "field_output_format": "OUTPUT_REAL_IMAG",
        "mode_launch_type": 2,
        "cad_aspectratio_x": 500,
        "cad_aspectratio_y ": 500,
        "fem_outh": 0,
        "fem_outs": 0,
        "fem_plot_mesh": 0,
        "fem_save_meshfile": 0,
        "fem_leaky": 1,
        "fem_float": 0,
    }

    # Update global simulation parameters
    mspl.update_global_params(**sim_params)

    # Generate filename
    file_name = f"{sim_type}_{mspl.design_filename}"
    filepath = os.path.join(data_dir, expt_dir)
    design_filename = os.path.join(filepath, file_name)

    # Write design file
    logger.info(f"Writing design file to {design_filename}")
    mspl.write(design_filename)

    # Save the input parameters to a file
    params = {
        "boundary_max": boundary_max,
        "boundary_min": boundary_min,
        "boundary_max_y": boundary_max_y,
        "boundary_min_y": boundary_min_y,
        "domain_min": domain_min,
        "grid_size": grid_size_x,
        "grid_size_y": grid_size_y,
        "highest_mode": highest_mode,
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

    # Generate params filename
    params_filename = os.path.join(data_dir, expt_dir, f"params.json")

    # Write parameters to file
    logger.info(f"Saving parameters to {params_filename}")
    with open(params_filename, "w") as f:
        json.dump(params, f, indent=4)

    logger.info(f"Lantern creation complete: {file_name}")

    return filepath, file_name, core_map


if __name__ == "__main__":

    lantern = partial(
        make_parameterised_lantern,
        highest_mode="LP02",
        launch_mode="LP01",
        taper_factor=13.15,  # final diamter of 19 micron
        sim_type="femsim",
        femnev=6,
        taper_length=49400,
        expt_dir="lantern_test",
    )

    lantern(domain_min=0, opt_name="test_run")
