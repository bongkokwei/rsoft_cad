from functools import partial
import numpy as np
import pandas as pd
import os
import time
import argparse
import logging
from tqdm import tqdm

from rsoft_cad.rsoft_simulations import run_simulation
from rsoft_cad.utils import get_next_run_folder
from rsoft_cad.simulations import make_parameterised_lantern
from rsoft_cad.geometry import sigmoid_taper_ratio
from rsoft_cad import (
    LaunchType,
    TaperType,
    configure_logging,
)  # Import the configure_logging function


def femsim_tapered_lantern(
    expt_dir="femsim_run_000",
    data_dir="output",
    taper_factor=1,
    taper_length=50000,
    file_name_dim="custom_taper.txt",
    num_points=200,
    highest_mode="LP02",
    launch_mode="LP01",
    sim_type="femsim",
    femnev=12,
    start_pos=0,
    num_grid=200,
    mode_output="OUTPUT_REAL_IMAG",
    final_capillary_id=25,
    logger=None,
):
    """
    Run a series of femsim on a tapered lantern structure to analyse
    effective refractive index at different positions along the taper.

    Parameters:
    -----------
    expt_dir : str
        Directory to store experiment results
    data_dir : str
        Base directory to store output data
    taper_factor : float
        Factor determining the final diameter of the tapered structure
    taper_length : float
        Total length of the taper in microns
    file_name_dim : str
        Filename for custom taper profile dimensions
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
    start_pos : float
        Starting position for simulation in microns
    num_grid : int
        Number of grid points in each axis for simulation
    mode_output : str
        Format for mode output (e.g., OUTPUT_REAL_IMAG)
    final_capillary_id : int
        Final capillary ID for the structure
    logger : logging.Logger
        Logger instance
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    logger.info(f"Starting tapered lantern simulation in directory: {expt_dir}")
    logger.info(
        f"Configuration: taper_factor={taper_factor}, taper_length={taper_length}, "
        f"num_points={num_points}, highest_mode={highest_mode}, launch_mode={launch_mode}"
    )

    taper_scan_array = np.linspace(
        start_pos,
        taper_length,
        num_points,
        endpoint=True,
    )
    logger.debug(
        f"Generated taper scan array with {num_points} points from {start_pos} to {taper_length}"
    )

    x_value = pd.DataFrame(columns=["filename", "z_pos"])

    n_eff_expt = partial(
        make_parameterised_lantern,
        highest_mode=highest_mode,
        launch_mode=launch_mode,
        sim_type=sim_type,
        femnev=femnev,
        taper_length=taper_length,
        taper_factor=taper_factor,  # set to one to use custom taper
        data_dir=data_dir,
        expt_dir=expt_dir,
        launch_type=LaunchType.GAUSSIAN,
        taper_config={
            "core": TaperType.user(1, file_name_dim),
            "cladding": TaperType.user(1, file_name_dim),
            "cap": TaperType.user(1, file_name_dim),
        },
        num_grid=num_grid,
        mode_output=mode_output,
        final_capillary_id=final_capillary_id,
        num_pads=50,
    )
    logger.debug("Configured parameterized lantern function")

    for i, taper in enumerate(tqdm(taper_scan_array, desc="Running simulations")):
        logger.info(f"Running simulation {i+1}/{num_points} at position {taper}")
        try:
            filepath, filename, core_map = n_eff_expt(
                domain_min=taper,
                opt_name=f"run_{i:03d}",  # design file suffix
            )
            logger.debug(f"Generated design file: {filepath}/{filename}")

            # Run simulation
            simulation_result = run_simulation(
                filepath,
                filename,
                sim_package=sim_type,
                prefix_name=f"run_{i:03d}",
                save_folder="rsoft_data_files",
                hide_sim=True,
            )

            if simulation_result.returncode == 0:
                logger.debug(f"Simulation run_{i:03d} completed successfully")
            else:
                logger.warning(
                    f"Simulation run_{i:03d} returned non-zero exit code: {simulation_result.returncode}"
                )
                if simulation_result.stdout:
                    logger.warning(f"Stdout: {simulation_result.stdout}")
                if simulation_result.stderr:
                    logger.error(f"Stderr: {simulation_result.stderr}")

            # Add a new row
            x_value.loc[i, "filename"] = f"run_{i:03d}"
            x_value.loc[i, "z_pos"] = taper  # Using the taper value from your array

            # Save progress after each simulation
            csv_path = os.path.join(data_dir, expt_dir, "x_values.csv")
            x_value.to_csv(csv_path, index=False)
            logger.debug(f"Updated and saved progress to {csv_path}")

        except Exception as e:
            logger.exception(f"Error in simulation {i} at position {taper}: {str(e)}")

    logger.info(
        f"Completed all {num_points} simulations for capillary inner diameter {final_capillary_id}"
    )


def femsimulation():
    """Parse command line arguments and run lantern simulations."""

    parser = argparse.ArgumentParser(
        description="Run lantern simulations to analyse effective refractive index."
    )

    parser.add_argument(
        "--taper-factor",
        type=float,
        default=1,
        help="Taper factor (default: [1])",
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
        default=200,
        help="Number of simulation points along taper (default: 200)",
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
    # Add new argument for data directory
    parser.add_argument(
        "--data-dir",
        type=str,
        default="output",
        help="Base directory to store output data (default: output)",
    )
    # Add new argument for final capillary ID
    parser.add_argument(
        "--final-capillary-id",
        type=float,
        nargs="+",
        default=[25.0],
        help="List of taper factors to simulate (default: [25.0])",
    )
    # Add new argument for log level
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )

    args = parser.parse_args()

    expt_dir = get_next_run_folder(args.data_dir, args.output_prefix)
    logger.info(f"Created experiment directory: {expt_dir}")

    # Set up logging
    log_path = os.path.join(args.data_dir, expt_dir, "simulation.log")
    logger = configure_logging(log_file=log_path, log_level=logging.INFO)
    logger.info("Starting femsimulation script")

    # Update logging level if specified
    if args.log_level:
        level = getattr(logging, args.log_level)
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
        logger.info(f"Set logging level to {args.log_level}")

    logger.info(f"Parsed arguments: {vars(args)}")

    # Custom taper profile name
    file_name_dim = "custom_profile_dim.txt"
    save_to = os.path.join("output", expt_dir, "rsoft_data_files")
    os.makedirs(save_to, exist_ok=True)
    logger.debug(f"Created directory for rsoft data files: {save_to}")

    z = np.linspace(0, 1, args.num_points)
    taper_ratios = sigmoid_taper_ratio(z, taper_length=1)
    logger.debug(f"Generated sigmoid taper profile with {args.num_points} points")

    # Save to both data folder and expt_dir
    profile_path_1 = os.path.join(save_to, file_name_dim)
    np.savetxt(
        profile_path_1,
        np.column_stack((z, taper_ratios)),
        delimiter="\t",
        header=f"/rn,a,b /nx0 {args.num_points} 0 1 1 OUTPUT_REAL\n ",
        comments="",
    )
    logger.debug(f"Saved taper profile to {profile_path_1}")

    profile_path_2 = os.path.join("output", expt_dir, file_name_dim)
    np.savetxt(
        profile_path_2,
        np.column_stack((z, taper_ratios)),
        delimiter="\t",
        header=f"/rn,a,b /nx0 {args.num_points} 0 1 1 OUTPUT_REAL\n ",
        comments="",
    )
    logger.debug(f"Saved taper profile to {profile_path_2}")

    for i, cap_id in enumerate(args.final_capillary_id):
        logger.info(
            f"Starting simulation for taper factor {cap_id} ({i+1}/{len(args.final_capillary_id)})"
        )
        try:
            femsim_tapered_lantern(
                expt_dir=expt_dir,
                taper_factor=args.taper_factor,
                taper_length=args.taper_length,
                num_points=args.num_points,
                highest_mode=args.highest_mode,
                launch_mode=args.launch_mode,
                sim_type=args.sim_type,
                femnev=args.femnev,
                start_pos=args.start_pos,
                num_grid=args.num_grids,
                mode_output=args.mode_output,
                file_name_dim=file_name_dim,
                data_dir=args.data_dir,
                final_capillary_id=args.final_capillary_id,
                logger=logger,
            )
            logger.info(f"Completed simulation for capillary id {cap_id}")
        except Exception as e:
            logger.exception(
                f"Error during simulation with capillary id {cap_id}: {str(e)}"
            )

    logger.info("All simulations completed")


if __name__ == "__main__":
    femsimulation()
