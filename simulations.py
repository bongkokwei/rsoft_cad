from examples.mode_selective_lantern import ModeSelectiveLantern
from rsoft_cad.utils.plot_utils import visualise_lantern

import os
import sys
import subprocess

import numpy as np
import matplotlib.pyplot as plt


def main():

    taper_factor = 12
    femsim = False
    launch_from = "LP11a"

    mspl = ModeSelectiveLantern()
    mspl.update_global_params(
        mode_set_setting=0,
        output_as_3d=1,
        field_output_format="OUTPUT_REAL",
    )
    core_map = mspl.create_lantern(
        highest_mode="LP02",
        launch_mode=launch_from,
        taper_factor=taper_factor,
        femnev=4,
        femsim=femsim,
        opt_name="",
    )

    design_filepath = mspl.design_filepath
    design_filename = mspl.design_filename

    # Save simulation results to this directory
    target_dir = design_filepath + "beamprop_test_002/"

    # Create the folder if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created folder: {target_dir}")

    # Change to the directory
    os.chdir(target_dir)
    print(f"Changed directory to: {os.getcwd()}")

    if femsim:

        print(f"\n Running FEMSIM when taper factor = {taper_factor}...\n")
        result = subprocess.run(
            [
                "femsim",
                "-hide",
                "../" + design_filename,
                f"prefix=femsim_tf_{taper_factor}_{launch_from}",
            ],
            capture_output=True,
            text=True,
        )
    else:
        print(f"\n Running BeamProp when taper factor = {taper_factor}...\n")
        result = subprocess.run(
            [
                "bsimw32",
                "-hide",
                "../" + design_filename,
                f"prefix=beamprop_tf_{taper_factor}_{launch_from}",
            ],
            capture_output=True,
            text=True,
        )

    # Change to the script dir
    os.chdir("../../..")
    print(f"Changed directory back to: {os.getcwd()}")


if __name__ == "__main__":
    main()
