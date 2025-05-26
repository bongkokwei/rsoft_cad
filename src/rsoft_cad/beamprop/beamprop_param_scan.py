from rsoft_cad.simulations import make_parameterised_lantern
from functools import partial
import numpy as np
import pandas as pd
import os
import time
import argparse
import logging

from rsoft_cad.rsoft_simulations import run_simulation
from rsoft_cad.utils import get_next_run_folder
from rsoft_cad.simulations import make_parameterised_lantern
from rsoft_cad.geometry import sigmoid_taper_ratio
from rsoft_cad import (
    LaunchType,
    TaperType,
    configure_logging,
)


def beamprop_tapered_lantern(
    expt_dir="femsim_run_000",
    data_dir="output",
    taper_factor=1,
    taper_length=50000,
    file_name_dim="custom_taper.txt",
    num_points=200,
    highest_mode="LP02",
    launch_mode="LP01",
    sim_type="beamprop",
    femnev=12,
    start_pos=0,
    num_grid=200,
    mode_output="OUTPUT_REAL_IMAG",
    final_capillary_id=25,
    opt_name="beamprop",
    logger=None,
):
    """
    Run beam propagation simulation for a tapered photonic lantern structure.

    This function sets up and executes a beam propagation simulation through a tapered
    photonic lantern using RSoft CAD tools. The simulation analyzes how optical modes
    propagate through the tapered structure and can be used to study coupling efficiency
    and loss characteristics.

    Parameters
    ----------
    expt_dir : str, optional
        Directory name to store experiment results (default: "femsim_run_000")
    data_dir : str, optional
        Base directory path for storing output data (default: "output")
    taper_factor : float, optional
        Scaling factor for the taper profile (default: 1.0)
    taper_length : float, optional
        Total length of the taper in microns (default: 50000)
    file_name_dim : str, optional
        Filename containing custom taper profile dimensions (default: "custom_taper.txt")
    num_points : int, optional
        Number of simulation points along the taper length (default: 200)
    highest_mode : str, optional
        Highest-order mode to include in simulation (default: "LP02")
    launch_mode : str, optional
        Input mode to launch into the structure (default: "LP01")
    sim_type : str, optional
        Type of simulation to run (default: "beamprop")
    femnev : int, optional
        Number of eigenvalues for FEM solver (default: 12)
    start_pos : float, optional
        Starting position for simulation in microns (default: 0)
    num_grid : int, optional
        Number of grid points per axis for simulation mesh (default: 200)
    mode_output : str, optional
        Output format for mode data (default: "OUTPUT_REAL_IMAG")
    final_capillary_id : int, optional
        Final capillary identifier for the lantern structure (default: 25)
    opt_name : str, optional
        Optimization/run name for file identification (default: "beamprop")
    logger : logging.Logger, optional
        Logger instance for output messages (default: None, creates new logger)

    Returns
    -------
    core_map : dict
        Dictionary containing the core mapping information from the simulation

    Raises
    ------
    FileNotFoundError
        If the custom taper profile file cannot be found
    RuntimeError
        If the RSoft simulation fails to execute properly
    """

    # Initialize logging if no logger provided
    if logger is None:
        logger = logging.getLogger(__name__)

    # Log simulation start and key parameters
    logger.info(f"Starting tapered lantern beam propagation simulation")
    logger.info(f"Experiment directory: {expt_dir}")
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Simulation configuration:")
    logger.info(f"  - Taper factor: {taper_factor}")
    logger.info(f"  - Taper length: {taper_length} μm")
    logger.info(f"  - Number of points: {num_points}")
    logger.info(f"  - Highest mode: {highest_mode}")
    logger.info(f"  - Launch mode: {launch_mode}")
    logger.info(f"  - Grid points: {num_grid}")
    logger.info(f"  - Custom taper file: {file_name_dim}")

    try:
        # Create parameterized simulation function using partial application
        # This allows us to fix most parameters while varying specific ones
        logger.debug("Creating parameterized simulation function")
        beamprop_expt = partial(
            make_parameterised_lantern,
            highest_mode=highest_mode,  # Maximum mode order to simulate
            launch_mode=launch_mode,  # Input mode type
            sim_type=sim_type,  # Simulation method (beam propagation)
            femnev=femnev,  # Number of FEM eigenvalues
            taper_length=taper_length,  # Physical taper length
            taper_factor=taper_factor,  # Taper scaling factor
            data_dir=data_dir,  # Output data directory
            expt_dir=expt_dir,  # Experiment subdirectory
            launch_type=LaunchType.GAUSSIAN,  # Gaussian beam launch
            # Configure taper profiles for different structure components
            taper_config={
                "core": TaperType.user(1, file_name_dim),  # Core taper profile
                "cladding": TaperType.user(1, file_name_dim),  # Cladding taper profile
                "cap": TaperType.user(1, file_name_dim),  # Cap taper profile
            },
            num_grid=num_grid,  # Simulation mesh density
            mode_output=mode_output,  # Output data format
            final_capillary_id=final_capillary_id,  # End structure ID
            num_pads=50,  # Padding layers for boundary conditions
        )

        # Generate simulation files and structure mapping
        logger.info("Generating simulation files and structure geometry")
        filepath, filename, core_map = beamprop_expt(
            opt_name=opt_name,
            taper_factor=taper_factor,
        )

        logger.info(f"Generated simulation files:")
        logger.info(f"  - File path: {filepath}")
        logger.info(f"  - File name: {filename}")
        logger.debug(f"Core mapping: {core_map}")

        # Execute the RSoft beam propagation simulation
        logger.info("Starting RSoft beam propagation simulation")
        simulation_start_time = time.time()

        simulation_result = run_simulation(
            filepath,  # Path to simulation input file
            filename,  # Simulation file name
            sim_package="bsimw32",  # RSoft BeamPROP simulator package
            prefix_name=opt_name,  # Output file prefix
            save_folder="rsoft_data_files",  # Results storage folder
            hide_sim=True,  # Run simulation in background
        )

        simulation_end_time = time.time()
        simulation_duration = simulation_end_time - simulation_start_time

        logger.info(f"Simulation completed successfully")
        logger.info(f"Simulation duration: {simulation_duration:.2f} seconds")
        logger.info(f"Results saved to: rsoft_data_files/{opt_name}")

        # Log simulation result status
        if simulation_result:
            logger.info("Simulation result indicates successful completion")
        else:
            logger.warning("Simulation result indicates potential issues")

    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
        logger.error(f"Check that taper profile file '{file_name_dim}' exists")
        raise

    except Exception as e:
        logger.error(f"Simulation failed with error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise RuntimeError(f"Tapered lantern simulation failed: {e}")

    logger.info("Beam propagation simulation completed successfully")
    return core_map


def main():
    """
    Main function to parse command line arguments and run tapered lantern simulations.

    This function handles command-line argument parsing and orchestrates multiple
    simulation runs with varying taper lengths. It sets up logging and manages
    the overall simulation workflow.

    Command Line Arguments
    ----------------------
    --taper-length : list of int
        Three values defining taper length array: [start, stop, num_points]
        Default: [20000, 60000, 100] (20mm to 60mm with 100 points)

    Raises
    ------
    SystemExit
        If command line arguments are invalid or simulation fails
    """

    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description="Run tapered photonic lantern beam propagation simulations "
        "to analyze coupling efficiency and optical losses.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Add command line arguments
    parser.add_argument(
        "--taper-length",
        type=int,
        nargs=3,  # Expect exactly 3 values: start, stop, num_points
        default=[20000, 60000, 100],
        metavar=("START", "STOP", "NUM"),
        help="Taper length range: START STOP NUM_POINTS (in microns). "
        "Creates NUM_POINTS linearly spaced values from START to STOP. "
        "Default: 20000 60000 100",
    )

    # Add additional arguments for future expansion
    parser.add_argument(
        "--data-dir",
        type=str,
        default="output",
        help="Base directory for storing simulation results (default: output)",
    )

    parser.add_argument(
        "--taper-factor",
        type=float,
        default=1.0,
        help="Taper scaling factor (default: 1.0)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    # Parse command line arguments
    args = parser.parse_args()

    # Create unique experiment directory for this simulation run
    expt_dir = get_next_run_folder(args.data_dir, "beamprop_run_")

    # Set up comprehensive logging system
    log_path = os.path.join(args.data_dir, expt_dir, "simulation.log")

    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Configure logging with specified level
    log_level = getattr(logging, args.log_level.upper())
    logger = configure_logging(log_file=log_path, log_level=log_level)

    # Log simulation campaign start
    logger.info("=" * 80)
    logger.info("TAPERED LANTERN SIMULATION CAMPAIGN STARTED")
    logger.info("=" * 80)
    logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Experiment directory: {expt_dir}")
    logger.info(f"Log file: {log_path}")
    logger.info(f"Command line arguments: {vars(args)}")

    # Generate array of taper lengths for parametric study
    logger.info(f"Generating taper length array:")
    logger.info(f"  - Start: {args.taper_length[0]} μm")
    logger.info(f"  - Stop: {args.taper_length[1]} μm")
    logger.info(f"  - Number of points: {args.taper_length[2]}")

    taper_length_array = np.linspace(
        args.taper_length[0],  # Start value
        args.taper_length[1],  # End value
        args.taper_length[2],  # Number of points
    )

    logger.info(f"Generated {len(taper_length_array)} taper lengths")
    logger.debug(f"Taper length array: {taper_length_array}")

    # Run simulation for each taper length
    total_simulations = len(taper_length_array)
    successful_runs = 0
    failed_runs = 0

    # Custom taper profile name
    taper_filename = "sigmoid_taper_profile.dat"
    save_to = os.path.join("output", expt_dir, "rsoft_data_files")
    os.makedirs(save_to, exist_ok=True)
    logger.debug(f"Created directory for rsoft data files: {save_to}")

    z = np.linspace(0, 1, 100)
    taper_ratios = sigmoid_taper_ratio(z, taper_length=1)

    # Save to both data folder and expt_dir
    profile_path_1 = os.path.join(save_to, taper_filename)
    np.savetxt(
        profile_path_1,
        np.column_stack((z, taper_ratios)),
        delimiter="\t",
        header=f"/rn,a,b /nx0 100 0 1 1 OUTPUT_REAL\n ",
        comments="",
    )
    logger.debug(f"Saved taper profile to {profile_path_1}")

    profile_path_2 = os.path.join("output", expt_dir, taper_filename)
    np.savetxt(
        profile_path_2,
        np.column_stack((z, taper_ratios)),
        delimiter="\t",
        header=f"/rn,a,b /nx0 100 0 1 1 OUTPUT_REAL\n ",
        comments="",
    )
    logger.debug(f"Saved taper profile to {profile_path_2}")

    logger.info(f"Starting parametric simulation sweep ({total_simulations} runs)")
    campaign_start_time = time.time()

    for i, taper_length in enumerate(taper_length_array):
        run_name = f"run_{i:03d}"

        logger.info("-" * 60)
        logger.info(f"SIMULATION {i+1}/{total_simulations}: {run_name}")
        logger.info(f"Taper length: {taper_length:.1f} μm")
        logger.info("-" * 60)

        run_start_time = time.time()

        try:
            # Execute individual simulation run
            core_map = beamprop_tapered_lantern(
                expt_dir=expt_dir,  # Experiment directory
                data_dir=args.data_dir,  # Base data directory
                opt_name=run_name,  # Unique run identifier
                taper_factor=args.taper_factor,  # Taper scaling factor
                taper_length=taper_length,  # Current taper length
                highest_mode="LP02",  # Maximum mode order
                launch_mode="LP02",  # Input mode type
                logger=logger,  # Pass logger instance
                mode_output="OUTPUT_NONE",
                file_name_dim=taper_filename,
            )

            run_end_time = time.time()
            run_duration = run_end_time - run_start_time
            successful_runs += 1

            logger.info(f"Run {run_name} completed successfully in {run_duration:.2f}s")
            logger.debug(f"Core map for {run_name}: {core_map}")

        except Exception as e:
            run_end_time = time.time()
            run_duration = run_end_time - run_start_time
            failed_runs += 1

            logger.error(f"Run {run_name} failed after {run_duration:.2f}s")
            logger.error(f"Error: {str(e)}")
            logger.exception("Full error traceback:")

            # Continue with remaining simulations rather than stopping
            logger.info("Continuing with remaining simulations...")

    # Log campaign completion summary
    campaign_end_time = time.time()
    total_duration = campaign_end_time - campaign_start_time

    logger.info("=" * 80)
    logger.info("SIMULATION CAMPAIGN COMPLETED")
    logger.info("=" * 80)
    logger.info(f"Total duration: {total_duration/60:.1f} minutes")
    logger.info(f"Successful runs: {successful_runs}/{total_simulations}")
    logger.info(f"Failed runs: {failed_runs}/{total_simulations}")
    logger.info(f"Success rate: {100*successful_runs/total_simulations:.1f}%")

    if failed_runs > 0:
        logger.warning(f"Some simulations failed. Check log for details.")

    logger.info(f"Results saved in: {os.path.join(args.data_dir, expt_dir)}")
    logger.info("Campaign completed.")


if __name__ == "__main__":
    main()
