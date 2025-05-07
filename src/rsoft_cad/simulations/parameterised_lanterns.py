# Import required libraries
import os
import numpy as np
import json
import matplotlib.pyplot as plt
from functools import partial

# Import custom modules
from rsoft_cad.lantern import ModeSelectiveLantern

# from rsoft_cad.rsoft_mspl import ModeSelectiveLantern
from rsoft_cad.rsoft_simulations import run_simulation
from rsoft_cad.utils import visualise_lantern
from rsoft_cad.geometry import calculate_taper_properties


def make_parameterised_lantern(
    highest_mode="LP02",
    launch_mode="LP01",
    opt_name="run_000",
    taper_factor=21,
    taper_length=80000,
    sim_type="breamprop",
    femnev=1,
    save_neff=True,
    step_x=None,
    step_y=None,
    domain_min=0,
    data_dir="output",
    expt_dir="pl_property_scan",
    num_grid=400,
    mode_output="OUTPUT_REAL_IMAG",
    core_dict=None,
    cladding_dia_dict=None,
    bg_index_dict=None,
    cladding_index_dict=None,
    core_index_dict=None,
):
    """
    Create a parameterised photonic lantern configuration
    """

    if sim_type == "beamprop":
        sim_string = "ST_BEAMPROP"
    elif sim_type == "femsim":
        sim_string = "ST_FEMSIM"
    else:
        raise ValueError(
            f"Invalid simulation type: {sim_type}. Expected 'femsim' or 'beamprop'."
        )

    # Create Mode Selective Photonic Lantern instance
    mspl = ModeSelectiveLantern()

    # Create lantern without writing to design file
    core_map = mspl.create_lantern(
        highest_mode=highest_mode,
        launch_mode=launch_mode,
        opt_name=opt_name,
        savefile=False,  # Hold off on saving design file
        taper_factor=taper_factor,
        taper_length=taper_length,
    )

    if core_dict is not None:
        mspl.fiber_config.set_core_dia(core_dict)

    if cladding_dia_dict is not None:
        mspl.fiber_config.set_cladding_dia(cladding_dia_dict)

    if bg_index_dict is not None:
        mspl.fiber_config.set_bg_index(bg_index_dict)

    if cladding_index_dict is not None:
        mspl.fiber_config.set_cladding_index(cladding_index_dict)

    if core_index_dict is not None:
        mspl.fiber_config.set_core_index(core_index_dict)

    # Calculate simulation boundaries based on capillary diameter
    # Calculate simulation boundary

    (
        dia_at_pos,
        taper_rate,
        taper_factor,
        end_dia,
    ) = calculate_taper_properties(
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
    # params_filename = os.path.join(data_dir, expt_dir, f"{opt_name}_params.json")
    params_filename = os.path.join(data_dir, expt_dir, f"params.json")

    # Write parameters to file
    with open(params_filename, "w") as f:
        json.dump(params, f, indent=4)

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
