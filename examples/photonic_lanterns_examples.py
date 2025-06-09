"""
Photonic Lantern Simulation using SINGLE_MODE_FIBERS Database

This script demonstrates how to create and simulate a photonic lantern
using the built-in SINGLE_MODE_FIBERS database with concentric circle arrangement.

The script:
1. Selects fiber types from the SINGLE_MODE_FIBERS database
2. Creates a photonic lantern with concentric circles configuration
3. Runs beam propagation simulation and visualizes results

Dependencies:
    - pandas: For data manipulation
    - rsoft_cad: Custom RSoft CAD interface library
    - matplotlib: For visualization (used by visualise_modes)

Output:
    - Simulation data files in the specified output directory
    - Field distribution plots
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


def create_photonic_lantern_smf():
    """
    Create and simulate a photonic lantern using SINGLE_MODE_FIBERS database
    """

    # Set up output directories
    data_dir = "output"
    expt_dir = get_next_run_folder("output", "pl_smf_run_")

    # Show SMF database summary
    smf_df = show_smf_database_summary()

    # Define photonic lantern configuration
    # Concentric circles: center + 2 rings
    layer_config = [
        (1, 0.0),  # Center core
        (6, 1.0),  # First ring: 6 cores
        (12, 1.8),  # Second ring: 12 cores
    ]

    total_cores = sum(layer[0] for layer in layer_config)

    # Fiber selection strategy for photonic lanterns
    # Strategy: Use uniform or near-uniform fibers for consistency

    # Option 1: All same fiber type (uniform)
    uniform_fiber_idx = 0  # SMF-28 (most common)
    fiber_indices_uniform = [uniform_fiber_idx] * total_cores

    # Option 2: Ring-based selection (different fiber per ring)
    center_fiber = 1  # LEAF (larger core for center)
    ring1_fiber = 0  # SMF-28 (standard)
    ring2_fiber = 6  # G.657.A2 (smaller core for outer ring)

    fiber_indices_rings = (
        [center_fiber]  # Center core
        + [ring1_fiber] * 6  # First ring
        + [ring2_fiber] * 12  # Second ring
    )

    # Choose strategy (you can change this)
    selected_strategy = "rings"  # Options: "uniform", "rings", "mixed"

    if selected_strategy == "uniform":
        fiber_indices = fiber_indices_uniform
        strategy_desc = f"All fibers: {smf_df.iloc[uniform_fiber_idx]['Fiber_Type']}"
    elif selected_strategy == "rings":
        fiber_indices = fiber_indices_rings
        strategy_desc = "Ring-based: LEAF center, SMF-28 ring1, G.657.A2 ring2"

    # Get fiber type names
    fiber_types = get_fiber_type_list_by_indices(smf_df, fiber_indices)
    unique_types = list(set(fiber_types))

    # Run the simulation
    try:
        result = build_and_simulate_lantern(
            fiber_indices=fiber_indices,
            lantern_type="photonic",
            run_name="pl_smf_example",
            expt_dir=expt_dir,
            data_dir=data_dir,
            save_folder="rsoft_data_files",
            launch_mode="0",  # Launch from center core
            taper_length=50000,  # 80mm taper length
            sim_type="femsim",  # FEMSIM method
            num_grid=200,  # Grid resolution
            final_capillary_id=25,  # Final capillary diameter
            femnev=int(2 * len(fiber_indices)),
            manual_mode=True,  # Skip overlap calculation
            domain_min=50000,  # Start analysis at taper end
            hide_sim=False,  # Hide simulation GUI
            # Photonic lantern configuration
            layer_config=layer_config,
        )

        # Visualize the field distributions
        output_file = visualise_modes(
            folder_name=expt_dir,
            file_prefix="pl_smf_example",
            num_modes=40,  # Show all cores
            nrow=5,
            ncol=8,
            figsize=(12, 16),
            show_plot=True,
            cleanup_files=True,
        )

        return expt_dir, fiber_types, unique_types, selected_strategy

    except Exception as e:
        print(e)
        return expt_dir, fiber_types, unique_types, selected_strategy


if __name__ == "__main__":
    """
    Main execution
    """
    # Run the simulation
    expt_dir, fiber_types, unique_types, strategy = create_photonic_lantern_smf()
