"""
Photonic Lantern Simulation Script

This script performs a photonic lantern simulation using RSoft CAD software.
A photonic lantern is a device that couples light between a multimode fiber
and multiple single-mode fibers through an adiabatic taper transition.

The simulation builds and analyses a lantern configuration with specified
single-mode fibers, simulates mode propagation, and visualizes the results.


Dependencies:
    - pandas: For data manipulation and analysis
    - rsoft_cad: Custom RSoft CAD interface library
    - matplotlib: For visualization (used by visualise_modes)


Output:
    - Simulation data files in the specified output directory
    - Mode visualization plots
    - Console output showing selected fiber types
"""

import pandas as pd

from rsoft_cad.simulations import build_and_simulate_lantern
from rsoft_cad.constants import SINGLE_MODE_FIBERS
from rsoft_cad.utils import (
    get_next_run_folder,
    get_fiber_type_list_by_indices,
    visualise_modes,
)

data_dir = "output"
expt_dir = get_next_run_folder("output", "best_config_run_")

"""
Fiber selection strategy (largest to smallest core diameter):
Index mapping to fiber types:
    1: LEAF (9.6 μm core)
    2: OS2 (8.5 μm core) 
    9: Allwave (8.4 μm core)
    8: SMF-28e+ (8.3 μm core)
    0: SMF-28 (8.2 μm core)
    6: G.657.A2 (8.0 μm core)
    5: G.655 (7.8 μm core)
    3: TrueWave RS (7.5 μm core)
"""
fiber_indices = [1, 2, 2, 9, 9, 8, 0, 0]

build_and_simulate_lantern(
    fiber_indices=fiber_indices,
    taper_file_name="custom_taper.dat",
    run_name="manual_config",
    expt_dir=expt_dir,
    data_dir=data_dir,
    save_folder="rsoft_data_files",
    highest_mode="LP31",
    launch_mode="LP01",
    taper_length=50000,
    femnev=int(2 * len(fiber_indices)),
    num_grid=200,
    final_capillary_id=12,
    manual_mode=True,
    domain_min=50000,
)

# Sort the original list by core diameter
smf_df = pd.DataFrame(SINGLE_MODE_FIBERS)
fiber_types = get_fiber_type_list_by_indices(smf_df, fiber_indices)
print(f"Selected fiber types: {fiber_types}")

output_file = visualise_modes(
    folder_name=expt_dir,
    num_modes=16,
    nrow=4,
    ncol=4,
    figsize=(10, 10),
    show_plot=True,
    cleanup_files=True,
)
