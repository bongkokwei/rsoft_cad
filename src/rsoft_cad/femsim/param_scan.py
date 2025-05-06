from functools import partial
import numpy as np
import pandas as pd
import os
import time
import argparse

from rsoft_cad.rsoft_simulations import run_simulation
from rsoft_cad.utils import get_next_run_folder
from rsoft_cad.simulations import make_parameterised_lantern


def femsim_tapered_lantern(
    expt_dir="n_eff_scan_run_003",
    taper_factor=11,
    taper_length=50000,
    num_points=400,
    highest_mode="LP02",
    launch_mode="LP01",
    sim_type="femsim",
    femnev=12,
    start_pos=0,
    num_grid=400,
    mode_output="OUTPUT_REAL_IMAG",
):
    """
    Run a series of femsim on a tapered lantern structure to analyse
    effective refractive index at different positions along the taper.

    Parameters:
    -----------
    expt_dir : str
        Directory to store experiment results
    taper_factor : float
        Factor determining the final diameter of the tapered structure
    taper_length : float
        Total length of the taper in microns
    num_points : int
        Number of simulation points along the taper
    highest_mode : str
        Highest mode to include in simulation
    launch_mode : str
        Mode to launch into the structure
    sim_type : str
        Type of simulation to run
    femnev : int
        FEM eigenvalue parameter
    """
    taper_scan_array = np.linspace(
        start_pos,
        taper_length,
        num_points,
        endpoint=True,
    )

    x_value = pd.DataFrame(columns=["filename", "z_pos"])

    n_eff_expt = partial(
        make_parameterised_lantern,
        highest_mode=highest_mode,
        launch_mode=launch_mode,
        taper_factor=taper_factor,  # final diameter of 19 micron
        sim_type=sim_type,
        femnev=femnev,
        taper_length=taper_length,
        expt_dir=expt_dir,
        num_grid=num_grid,
        mode_output=mode_output,
    )

    for i, taper in enumerate(taper_scan_array):
        filepath, filename, core_map = n_eff_expt(
            domain_min=taper,
            opt_name=f"run_{i:03d}",  # design file suffix
        )

        # Run simulation
        simulation_result = run_simulation(
            filepath,
            filename,
            sim_package=sim_type,
            prefix_name=f"run_{i:03d}",
            save_folder="rsoft_data_files",
            hide_sim=True,
        )

        print(f"Error message: {simulation_result.stdout} \n")

        # Add a new row
        x_value.loc[i, "filename"] = f"run_{i:03d}"
        x_value.loc[i, "z_pos"] = taper  # Using the taper value from your array

        # Save progress after each simulation
        x_value.to_csv(
            os.path.join("output", expt_dir, "x_values.csv"),
            index=False,
        )


def femsimulation():
    """Parse command line arguments and run tapered lantern simulations."""
    parser = argparse.ArgumentParser(
        description="Run tapered lantern simulations to analyse effective refractive index."
    )

    parser.add_argument(
        "--taper-factors",
        type=float,
        nargs="+",
        default=[13],
        help="List of taper factors to simulate (default: [13])",
    )
    parser.add_argument(
        "--taper-length",
        type=float,
        default=50000,
        help="Length of the taper in microns (default: 50000)",
    )
    parser.add_argument(
        "--num-points",
        type=int,
        default=400,
        help="Number of simulation points along taper (default: 400)",
    )

    parser.add_argument(
        "--num-grids",
        type=int,
        default=200,
        help="Number of simulation points in one axis (default: 200)",
    )

    parser.add_argument(
        "--highest-mode",
        type=str,
        default="LP02",
        help="Highest mode to include in simulation (default: LP02)",
    )
    parser.add_argument(
        "--launch-mode",
        type=str,
        default="LP01",
        help="Mode to launch into the structure (default: LP01)",
    )
    parser.add_argument(
        "--sim-type",
        type=str,
        default="femsim",
        help="Type of simulation to run (default: femsim)",
    )
    parser.add_argument(
        "--femnev",
        type=int,
        default=12,
        help="FEM eigenvalue parameter (default: 12)",
    )
    parser.add_argument(
        "--output-prefix",
        type=str,
        default="femsim_run_",
        help="Prefix for output directory names (default: femsim_run_)",
    )

    parser.add_argument(
        "--start-pos",
        type=float,
        default=0,
        help="Starting positon of simulation in microns (default: 0.0)",
    )

    parser.add_argument(
        "--mode-output",
        type=str,
        default="OUTPUT_REAL_IMAG",
        help="Mode output format (default=OUTPUT_REAL_IMAG)",
    )

    args = parser.parse_args()

    for i, taper_factor in enumerate(args.taper_factors):
        expt_dir = get_next_run_folder("output", args.output_prefix)
        femsim_tapered_lantern(
            expt_dir=expt_dir,
            taper_factor=taper_factor,
            taper_length=args.taper_length,
            num_points=args.num_points,
            highest_mode=args.highest_mode,
            launch_mode=args.launch_mode,
            sim_type=args.sim_type,
            femnev=args.femnev,
            start_pos=args.start_pos,
            num_grid=args.num_grids,
            mode_output=args.mode_output,
        )


if __name__ == "__main__":
    femsimulation()
