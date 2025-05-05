from rsoft_cad.simulations import make_parameterised_lantern
from functools import partial
import numpy as np
import pandas as pd
import os
import time
import argparse

from rsoft_cad.rsoft_simulations import run_simulation
from rsoft_cad.utils import get_next_run_folder


def beamprop_tapered_lantern(
    expt_dir="beamprop_run_001",
    taper_factor=11,
    taper_length=50000,
    highest_mode="LP02",
    launch_mode="LP02",
    femnev=12,
    result_files_prefix="run",
    opt_name="run_000",
):

    beamprop_expt = partial(
        make_parameterised_lantern,
        highest_mode=highest_mode,
        launch_mode=launch_mode,
        sim_type="beamprop",
        femnev=femnev,
        taper_length=taper_length,
        expt_dir=expt_dir,
    )

    filepath, filename, core_map = beamprop_expt(
        opt_name=opt_name,
        taper_factor=taper_factor,
    )

    # Run simulation
    simulation_result = run_simulation(
        filepath,
        filename,
        sim_package="bsimw32",
        prefix_name=result_files_prefix,
        save_folder="rsoft_data_files",
        hide_sim=True,
    )


def main():
    """Parse command line arguments and run tapered lantern simulations."""
    parser = argparse.ArgumentParser(
        description="Run tapered lantern simulations to analyse loss."
    )

    parser.add_argument(
        "--taper-factor",
        type=float,
        default=13,
        help="List of taper factors to simulate (default: 13)",
    )

    parser.add_argument(
        "--taper-length",
        type=int,
        nargs="+",
        default=[20000, 60000, 100],
        help="start/stop/num points values to generate taper length array",
    )

    args = parser.parse_args()

    expt_dir = get_next_run_folder("output", "beamprop_run_")
    taper_length_array = np.linspace(
        args.taper_length[0],
        args.taper_length[1],
        args.taper_length[2],
    )

    for i, taper_length in enumerate(taper_length_array):
        beamprop_tapered_lantern(
            expt_dir=expt_dir,
            opt_name=f"run_{i:03d}",
            taper_factor=args.taper_factor,
            taper_length=taper_length,
            highest_mode="LP02",
            launch_mode="LP02",
            result_files_prefix=f"run_{i:03d}",
        )


if __name__ == "__main__":
    main()
