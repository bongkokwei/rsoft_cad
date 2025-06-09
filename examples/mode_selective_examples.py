"""
Mode Selective Photonic Lantern Simulation using SINGLE_MODE_FIBERS Database

This script demonstrates how to create and simulate a mode selective photonic lantern
using the built-in SINGLE_MODE_FIBERS database.

The script:
1. Selects fiber types from the SINGLE_MODE_FIBERS database
2. Creates a mode selective lantern configuration
3. Runs finite element simulation and visualizes results

Dependencies:
    - pandas: For data manipulation
    - rsoft_cad: Custom RSoft CAD interface library
    - matplotlib: For visualization (used by visualise_modes)

Output:
    - Simulation data files in the specified output directory
    - Mode field distribution plots
"""

import pandas as pd
from rsoft_cad.simulations import build_and_simulate_lantern
from rsoft_cad.constants import SINGLE_MODE_FIBERS
from rsoft_cad.utils import (
    get_next_run_folder,
    get_fiber_type_list_by_indices,
    visualise_modes,
)


def show_smf_database_summary():
    """
    Display summary of the SINGLE_MODE_FIBERS database
    """
    smf_df = pd.DataFrame(SINGLE_MODE_FIBERS)
    return smf_df


def create_mode_selective_lantern_smf():
    """
    Create and simulate a mode selective lantern using SINGLE_MODE_FIBERS database
    """

    # Set up output directories
    data_dir = "output"
    expt_dir = get_next_run_folder("output", "mspl_smf_run_")

    # Show SMF database summary
    smf_df = show_smf_database_summary()

    # Fiber selection strategy for mode selective lanterns
    # Strategy from original example: largest to smallest core diameter approach
    # Index mapping to fiber types:
    #   1: LEAF (9.6 μm core)
    #   2: OS2 (8.5 μm core)
    #   9: Allwave (8.4 μm core)
    #   8: SMF-28e+ (8.3 μm core)
    #   0: SMF-28 (8.2 μm core)
    #   6: G.657.A2 (8.0 μm core)

    fiber_indices = [1, 2, 2, 9, 9, 8, 0, 0]  # Strategic selection for LP modes

    # Get fiber type names
    fiber_types = get_fiber_type_list_by_indices(smf_df, fiber_indices)
    unique_types = list(set(fiber_types))

    # Run the simulation
    try:
        result = build_and_simulate_lantern(
            fiber_indices=fiber_indices,
            lantern_type="mode_selective",
            run_name="mspl_smf_example",
            expt_dir=expt_dir,
            data_dir=data_dir,
            save_folder="rsoft_data_files",
            highest_mode="LP31",  # Target the LP31 mode
            launch_mode="LP01",  # Launch from fundamental mode
            taper_length=50000,  # 50mm taper length
            sim_type="femsim",  # Finite element method
            num_grid=200,  # Grid resolution
            final_capillary_id=25,  # Final capillary diameter
            femnev=int(2 * len(fiber_indices)),  # Number of eigenmodes to find
            manual_mode=True,  # Skip overlap calculation
            domain_min=50000,  # Start analysis at taper end
            hide_sim=False,  # Show simulation GUI
        )

        # Visualize the mode field distributions
        output_file = visualise_modes(
            folder_name=expt_dir,
            file_prefix="mspl_smf_example",
            num_modes=40,  # Show multiple modes
            nrow=5,
            ncol=8,
            figsize=(12, 16),
            show_plot=True,
            cleanup_files=True,
        )

        return expt_dir, fiber_types, unique_types

    except Exception as e:
        print(e)
        return expt_dir, fiber_types, unique_types


if __name__ == "__main__":
    """
    Main execution
    """
    # Run the simulation
    expt_dir, fiber_types, unique_types = create_mode_selective_lantern_smf()
