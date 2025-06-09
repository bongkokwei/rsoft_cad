"""
Custom Taper Profile Simulation for Photonic Lanterns
====================================================

This script demonstrates how to create and simulate a photonic lantern with a custom
sigmoid-based taper profile using the rsoft_cad package. It showcases:

1. Creating a custom sigmoid taper profile and saving it to dimension files
2. Setting up a parameterized lantern simulation with the custom taper
3. Running a FEM simulation of the lantern
4. Visualizing the lantern's LP mode structure

The script generates a sigmoid taper ratio along the z-axis and applies it to the core,
cladding, and cap of the photonic lantern. The simulation is configured for LP01 to LP02
mode conversion with Gaussian launch conditions.

TODO: make it more generalised, right now anything more than 6 is kaput.

Dependencies:
- rsoft_cad: Package for RSoft CAD simulations
- numpy: For numerical operations
- matplotlib: For visualization
- os: For file path handling
"""

import os
import matplotlib.pyplot as plt
import numpy as np


from rsoft_cad.rsoft_simulations import run_simulation
from rsoft_cad.simulations import make_parameterised_lantern
from rsoft_cad.utils import visualise_lp_lantern
from rsoft_cad.geometry import sigmoid_taper_ratio
from rsoft_cad import LaunchType, TaperType
from rsoft_cad.geometry import create_custom_taper_profile


if __name__ == "__main__":

    data_dir = "output"
    expt_dir = "custom_taper_profile"
    save_to = os.path.join(data_dir, expt_dir)
    file_name_dim = "custom_profile_dim.txt"

    # Create custom taper profile with the sigmoid parameters
    z, ratios = create_custom_taper_profile(
        data_dir=data_dir,
        expt_dir=expt_dir,
        rsoft_data_dir="rsoft_data_files",
        file_name=file_name_dim,
    )

    filepath, file_name, mspl_core_map = make_parameterised_lantern(
        lantern_type="mode_selective",
        highest_mode="LP02",
        launch_mode="LP01",
        sim_type="femsim",
        femnev=12,
        opt_name="LP01",
        taper_length=50000,
        taper_factor=1,  # set to one to use custom taper
        domain_min=50000,
        data_dir=data_dir,
        expt_dir=expt_dir,
        launch_type=LaunchType.GAUSSIAN,
        taper_config={
            "core": TaperType.user(1, file_name_dim),
            "cladding": TaperType.user(1, file_name_dim),
            "cap": TaperType.user(1, file_name_dim),
        },
        final_capillary_id=25,
        num_grid=200,
        num_pads=50,
        sort_neff=1,
    )

    results = run_simulation(
        filepath,
        file_name,
        "femsim",
        prefix_name="inner_diam_scan",
        save_folder="rsoft_data_files",
        hide_sim=False,
    )

    fig = visualise_lp_lantern(mspl_core_map)
    plt.show()
