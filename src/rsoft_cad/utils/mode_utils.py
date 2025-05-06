"""
Utility functions for working with optical modes in the RSoft CAD package.
"""


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
