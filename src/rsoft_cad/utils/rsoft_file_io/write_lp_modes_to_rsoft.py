import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Union, Optional
from rsoft_cad.utils import (
    write_femsim_field_data,
    generate_lp_mode,
    get_modes_below_cutoff,
)
from rsoft_cad.constants import lp_mode_cutoffs_freq


def generate_and_write_lp_modes(
    mode_field_diam: float = 25,
    highest_mode: str = "LP02",
    num_grid_x: int = 250,
    num_grid_y: int = 250,
    output_dir: str = "./sandbox/ideal_modes",
) -> None:
    """
    Generate and write linearly polarized (LP) optical fiber mode fields to files.

    This function generates various LP modes up to the specified highest mode (e.g., "LP02"),
    calculates their field distributions based on the provided parameters, and writes
    the field data to files in the specified output directory.

    Parameters
    ----------
    mode_field_diam : float, default=25
        Mode field diameter, determining the spatial extent of the optical mode.
    highest_mode : str, default="LP02"
        The highest LP mode to generate, in format "LPmn" where:
        - m is the azimuthal mode number
        - n is the radial mode number
    num_grid_x : int, default=250
        Number of grid points in the x-direction.
    num_grid_y : int, default=250
        Number of grid points in the y-direction.
    output_dir : str, default="./sandbox/ideal_modes"
        Directory where the field data files will be saved.
        Will be created if it doesn't exist.

    Returns
    -------
    None
        The function writes files to disk but does not return any values.

    Notes
    -----
    For modes with azimuthal number > 0, both 'a' and 'b' variants are generated,
    each with both Vertical (V) and Horizontal (H) polarizations.
    For modes with azimuthal number = 0, only 'a' variants are generated with
    both V and H polarizations.

    Examples
    --------
    >>> generate_and_write_lp_modes(
    ...     mode_field_diam=10,
    ...     highest_mode="LP11",
    ...     num_grid_x=300,
    ...     num_grid_y=300,
    ...     output_dir="./fiber_modes"
    ... )
    """
    # Check if output directory exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")

    # Calculate grid bounds based on mode_field_diam
    xmin, xmax = (-mode_field_diam * 2, mode_field_diam * 2)
    ymin, ymax = (-mode_field_diam * 2, mode_field_diam * 2)

    # Get modes below cutoff
    modes = get_modes_below_cutoff(highest_mode, lp_mode_cutoffs_freq)
    modes_list = []

    # Iterate through each mode in the current radial group
    for mode in modes:
        # Extract azimuthal number (first digit in the mode name)
        azimuthal_num = int(mode[2])
        radial_num = int(mode[3])
        # Determine how many coordinates to assign
        if azimuthal_num > 0:
            # For azimuthal > 0, create two separate keys
            # First coordinate with original name
            modes_list.append(f"{mode}a_V")
            modes_list.append(f"{mode}a_H")
            # Second coordinate with a 'b' suffix
            modes_list.append(f"{mode}b_V")
            modes_list.append(f"{mode}b_H")
        else:
            # For azimuthal = 0, assign 1 coordinate
            modes_list.append(f"{mode}a_V")
            modes_list.append(f"{mode}a_H")

    # Generate and write field data for each mode
    for i, mode in enumerate(modes_list):
        azimuthal_num = int(mode[2])
        radial_num = int(mode[3])
        X, Y, field = generate_lp_mode(
            l=azimuthal_num,
            p=radial_num,
            orientation=mode[4],
            mfd=mode_field_diam,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            num_grid_x=num_grid_x,
            num_grid_y=num_grid_y,
        )
        write_femsim_field_data(
            f"{output_dir}/ref_LP{mode}.m{i:02d}",
            abs(field),
            xmin,
            xmax,
            ymin,
            ymax,
        )
