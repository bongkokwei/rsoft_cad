"""
Utility functions for working with optical modes in the RSoft CAD package.
"""

import numpy as np
from scipy.interpolate import interp1d


def get_modes_below_cutoff(input_mode, lp_mode_cutoffs_freq):
    """
    Return all modes with cutoff frequencies less than or equal to
    the cutoff frequency of the input mode.

    Args:
        input_mode (str): The mode string (e.g., "LP21")
        lp_mode_cutoffs_freq (dict): Dictionary mapping mode strings to cutoff frequencies

    Returns:
        list: List of mode strings with cutoff frequencies <= the input mode's cutoff
    """
    if input_mode not in lp_mode_cutoffs_freq:
        raise ValueError(
            f"Mode '{input_mode}' not found in cutoff frequency dictionary"
        )

    # Get the cutoff frequency of the input mode
    input_cutoff = lp_mode_cutoffs_freq[input_mode]

    # Find all modes with cutoff frequencies <= input_cutoff
    modes_below_cutoff = [
        mode for mode, cutoff in lp_mode_cutoffs_freq.items() if cutoff <= input_cutoff
    ]

    # Sort by cutoff frequency
    return sorted(modes_below_cutoff, key=lambda mode: lp_mode_cutoffs_freq[mode])


def group_modes_by_radial_number(supported_modes):
    """
    Group LP modes by their radial number.

    For LP modes in format "LPml", where:
    - m is the azimuthal number (first digit)
    - l is the radial number (second digit)

    Args:
        supported_modes (list): List of LP mode strings (e.g., ["LP01", "LP11", "LP21"])

    Returns:
        dict: Dictionary mapping radial numbers to lists of modes
    """
    radial_groups = {}

    for mode in supported_modes:
        # Extract the radial number (second digit in the mode name)
        if len(mode) == 4 and mode.startswith("LP"):
            radial_number = int(mode[3])

            # Initialize the list for this radial number if it doesn't exist
            if radial_number not in radial_groups:
                radial_groups[radial_number] = []

            # Add the mode to the appropriate group
            radial_groups[radial_number].append(mode)

    return radial_groups


def find_segment_by_comp_name(segments, comp_name):
    """
    Find a segment by its component name.

    Args:
        segments (list): List of segment strings
        comp_name (str): Component name to search for

    Returns:
        str: Segment number if found

    Raises:
        ValueError: If component is not found in any segment
    """
    for segment in segments:
        if f"{comp_name}" in segment:
            # Extract segment number only
            segment_line = segment.split("\n")[0]  # Get "segment X" line
            segment_number = segment_line.replace("segment ", "").strip()
            return segment_number

    # Raise an exception if component is not found
    raise ValueError(f"Component '{comp_name}' not found in any segment")


def interpolate_taper_value(model, key, z_pos, mode_name=None):
    """
    Interpolate a value from the taper model at a specific z-position.

    Parameters:
    -----------
    model : dict
        The taper model dictionary containing the data
    key : str
        The key in the model dictionary to interpolate.
        Must be one of: "fiber_diameters", "core_diameters", "fiber_positions",
        "capillary_inner_diameter", "capillary_outer_diameter",
        "mode_positions", or "mode_core_diameters"
    z_pos : float
        The z-position at which to interpolate
    mode_name : str, optional
        For mode-related keys ("mode_positions", "mode_core_diameters"),
        the LP mode name to interpolate. Required for these keys.

    Returns:
    --------
    float
        The interpolated value at the specified z-position
    """
    # Define valid keys
    standard_keys = [
        "fiber_diameters",
        "core_diameters",
        "fiber_positions",
        "capillary_inner_diameter",
        "capillary_outer_diameter",
    ]
    mode_keys = ["mode_positions", "mode_core_diameters"]

    # Validate key
    if key not in standard_keys and key not in mode_keys:
        raise ValueError(
            f"Invalid key: '{key}'. Valid keys are: {standard_keys + mode_keys}"
        )

    # Get the z-positions array
    z = model["z"]

    # Check if z_pos is within the bounds of the z array
    if z_pos < np.min(z) or z_pos > np.max(z):
        raise ValueError(
            f"z_pos {z_pos} is outside the range of the model ({np.min(z)} to {np.max(z)})"
        )

    # Handle standard arrays
    if key in standard_keys:
        f = interp1d(z, model[key])
        return float(f(z_pos))

    # Handle mode-specific data
    elif key in mode_keys:
        if mode_name is None:
            raise ValueError(f"Mode name must be provided for key '{key}'")

        if mode_name not in model["lp_modes"]:
            raise ValueError(f"Mode name '{mode_name}' is not in the list of LP modes")

        f = interp1d(z, model[key][mode_name])
        return float(f(z_pos))
