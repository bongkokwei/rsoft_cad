"""
Layout management for photonic lantern structures.
"""

import numpy as np
from rsoft_cad.constants import lp_mode_cutoffs_freq
from rsoft_cad.utils import get_modes_below_cutoff, group_modes_by_radial_number
from rsoft_cad.utils import lantern_layout


def multilayer_lantern_layout(cladding_dia, layers_config):
    """
    Computes the positions of circles arranged in multiple concentric layers with truly optimal packing.

    Parameters:
        cladding_dia (float): Diameter of the smaller circles (cladding diameter).
        layers_config (list): List of tuples (n, radius_factor) where:
            - n: Number of circles in this layer
            - radius_factor: Factor to multiply the reference radius for this layer
                             (1.0 means standard positioning, >1.0 means further from center)
    Returns:
        tuple: (layer_centres, layer_radii) where:
            layer_centres (list): List of lists, each containing tuples of (x,y) coordinates for each layer
            layer_radii (list): List of reference radii for each layer
    """
    layer_centres = []
    layer_radii = []

    # Radius of individual circles
    circle_radius = cladding_dia / 2

    # First, determine the core structure
    # Using a centralized approach to ensure the densest possible layout

    # Collect all circles from all layers
    total_circles = sum(n for n, _ in layers_config)

    # Special case handling for very few circles
    if total_circles <= 1:
        return [[(0, 0)]], np.array([0])

    # For optimal packing, we'll use a different approach:
    # If we have a central circle (like LP01) and a ring around it (like LP11/LP21 modes)

    # Map out the layers with their counts (ignore radius_factor initially for optimal density)
    rings = []
    for n, _ in layers_config:
        rings.append(n)

    # Handle common case for LP mode layouts: central circle + ring of circles
    if len(rings) == 2 and rings[0] == 1 and rings[1] > 0:
        # Central circle (LP01)
        central_coordinates = [(0, 0)]
        layer_centres.append(central_coordinates)
        layer_radii.append(0)  # Center has radius 0

        # Ring around it (LP11/LP21 modes)
        n_outer = rings[1]
        # For densest packing, outer circles should touch the central circle
        # The distance from center to outer circle centers should be 2*circle_radius
        outer_radius = 2 * circle_radius

        # Calculate positions based on lantern_layout but override the radius
        _, centres_x, centres_y = lantern_layout(cladding_dia, n_outer)

        # Normalize and adjust to desired radius
        norm_factor = (
            np.sqrt(centres_x[0] ** 2 + centres_y[0] ** 2) if n_outer > 1 else 1
        )
        if norm_factor > 0:
            adjusted_centres_x = centres_x / norm_factor * outer_radius
            adjusted_centres_y = centres_y / norm_factor * outer_radius
        else:
            adjusted_centres_x = centres_x
            adjusted_centres_y = centres_y

        outer_coordinates = [
            (adjusted_centres_x[i], adjusted_centres_y[i])
            for i in range(len(adjusted_centres_x))
        ]
        layer_centres.append(outer_coordinates)
        layer_radii.append(outer_radius)

        return layer_centres, np.array(layer_radii)

    # For more complex configurations: multiple layers or non-standard counts
    # Fallback to a more geometric approach, focusing on the constraint that
    # neighboring circles must touch

    # Process layers from inner to outer
    previous_layer_radius = 0  # Radius to the centers of circles in previous layer

    for layer_idx, (n, radius_factor) in enumerate(layers_config):
        # Skip empty layers
        if n == 0:
            continue

        # First layer handling (innermost)
        if layer_idx == 0:
            if n == 1:
                # Single central circle
                layer_centres.append([(0, 0)])
                layer_radii.append(0)  # Center point
                previous_layer_radius = 0
            else:
                # Calculate the minimum radius where n circles can fit without overlap
                R, centres_x, centres_y = lantern_layout(cladding_dia, n)
                # Apply minimal radius for densest packing
                layer_centres.append([(centres_x[i], centres_y[i]) for i in range(n)])
                layer_radii.append(R)
                previous_layer_radius = R
        else:
            # For subsequent layers - ensure optimal packing with previous layer
            # The optimal placement has the outer circles touching the inner circles

            # Calculate base layout for this layer
            R, centres_x, centres_y = lantern_layout(cladding_dia, n)

            # Previous layer had circles at distance previous_layer_radius
            # For densest packing, new layer circles should be at distance:
            # previous_layer_radius + 2*circle_radius
            optimal_radius = previous_layer_radius + 2 * circle_radius

            # Normalize and adjust to get densest packing
            if R > 0:
                scaling_factor = optimal_radius / R
                adjusted_centres_x = centres_x * scaling_factor
                adjusted_centres_y = centres_y * scaling_factor
            else:
                adjusted_centres_x = centres_x
                adjusted_centres_y = centres_y

            layer_coords = [
                (adjusted_centres_x[i], adjusted_centres_y[i])
                for i in range(len(adjusted_centres_x))
            ]

            layer_centres.append(layer_coords)
            layer_radii.append(optimal_radius)

            # Update for next layer
            previous_layer_radius = optimal_radius

    return layer_centres, np.array(layer_radii)


def create_layers_config(radial_groups, scale_factors=None):
    """
    Create a layers configuration based on radial groups of modes.

    Rules:
    - Modes with radial number = 1 are in the outer layer
    - Each radial mode group represents a layer
    - Number of circles in a ring depends on the azimuthal number:
      * If azimuthal number > 0: 2 circles
      * Otherwise: 1 circle

    Args:
        radial_groups (dict): Dictionary mapping radial numbers to lists of modes
        scale_factors (dict): Optional scale factors for each radial layer, defaults to
                             {0: 1.0, 1: 1.5, 2: 1.7, ...}

    Returns:
        list: List of tuples (num_circles, scale_factor) for each layer
        int: Total number of cores
    """
    if scale_factors is None:
        # Default scale factors increasing by 0.2 for each layer
        scale_factors = {r: 1 for r in radial_groups.keys()}

    layers_config = []
    num_cores = 0

    # Sort radial numbers in descending order (so radial=1 is the outer layer)
    sorted_radial_numbers = sorted(radial_groups.keys(), reverse=True)

    for radial_num in sorted_radial_numbers:
        modes = radial_groups[radial_num]

        # Count circles based on azimuthal numbers
        layer_circles = 0
        for mode in modes:
            # Extract azimuthal number (first digit in the mode name)
            azimuthal_num = int(mode[2])

            # Add 2 circles if azimuthal > 0, otherwise add 1
            layer_circles += 2 if azimuthal_num > 0 else 1

        # Add the layer configuration
        scale_factor = scale_factors.get(radial_num, 1.0)
        layers_config.append((layer_circles, scale_factor))
        num_cores += layer_circles

    return layers_config, num_cores


def create_core_map(lp_mode_str, cladding_dia):
    """
    Creates a mapping between optical modes and their physical coordinates in the fiber.

    This function:
    1. Determines which modes are supported based on a cutoff frequency
    2. Groups these modes by their radial number
    3. Creates a layer configuration where:
       - Modes with radial number = 1 are in the outer layer (reverse sorting)
       - Each radial mode group represents a layer
    4. Returns a dictionary where:
       - Keys are mode strings (e.g., "LP01", "LP11")
       - Values are single (x,y) coordinate tuples

    Args:
        lp_mode_str (str): The highest LP mode to support (e.g., "LP21")
        cladding_dia (float): Cladding diameter in microns

    Returns:
        tuple: (core_map, cap_dia) where:
            core_map (dict): Mapping of mode strings to their coordinate tuples
            cap_dia (float): Diameter of the capillary
    """
    # Get supported modes below the cutoff
    supported_modes = get_modes_below_cutoff(lp_mode_str, lp_mode_cutoffs_freq)

    # Group modes by their radial number
    grouped_modes = group_modes_by_radial_number(supported_modes)

    # Create the layer configuration
    layer_config, _ = create_layers_config(grouped_modes)

    # Get the coordinates for each layer
    layer_centres, layer_radii = multilayer_lantern_layout(
        cladding_dia,
        layer_config,
    )

    cap_dia = (
        2 * layer_radii[-1] + cladding_dia if layer_radii.size > 0 else cladding_dia
    )

    # Create the core map dictionary
    core_map = {}

    # Process in reverse order of radial numbers (outer to inner)
    sorted_radial_numbers = sorted(grouped_modes.keys(), reverse=True)

    # Iterate through each radial group and corresponding layer
    for layer_idx, radial_num in enumerate(sorted_radial_numbers):
        modes = grouped_modes[radial_num]
        coords = layer_centres[layer_idx]

        # Track position in the current layer's coordinate list
        coord_index = 0

        # Iterate through each mode in the current radial group
        for mode in modes:
            # Extract azimuthal number (first digit in the mode name)
            azimuthal_num = int(mode[2])

            # Determine how many coordinates to assign
            if azimuthal_num > 0 and coord_index + 1 < len(coords):
                # For azimuthal > 0, create two separate keys
                # First coordinate with original name
                core_map[f"{mode}a"] = coords[coord_index]
                # Second coordinate with a 'b' suffix
                core_map[f"{mode}b"] = coords[coord_index + 1]
                coord_index += 2
            elif coord_index < len(coords):
                # For azimuthal = 0, assign 1 coordinate
                core_map[mode] = coords[coord_index]
                coord_index += 1

    return core_map, cap_dia


def create_indexed_core_map(layer_config, cladding_dia):
    """
    Creates a mapping between simple indices and their physical coordinates in the fiber.

    This function:
    1. Uses the provided layer configuration directly
    2. Creates coordinates for each layer using multilayer_lantern_layout
    3. Returns a dictionary where:
       - Keys are simple integer indices (0, 1, 2, ...)
       - Values are single (x,y) coordinate tuples

    Args:
        layer_config (list): List of tuples (num_circles, scale_factor) for each layer
        cladding_dia (float): Cladding diameter in microns

    Returns:
        tuple: (core_map, cap_dia) where:
            core_map (dict): Mapping of integer indices to their coordinate tuples
            cap_dia (float): Diameter of the capillary
    """
    # Get the coordinates for each layer using the provided configuration
    layer_centres, layer_radii = multilayer_lantern_layout(
        cladding_dia,
        layer_config,
    )

    # Calculate capillary diameter
    cap_dia = (
        2 * layer_radii[-1] + cladding_dia if layer_radii.size > 0 else cladding_dia
    )

    # Create the core map dictionary with simple integer indices
    core_map = {}
    current_index = 0

    # Iterate through each layer and assign indices to coordinates
    for layer_coords in layer_centres:
        for coord in layer_coords:
            core_map[f"{current_index}"] = coord
            current_index += 1

    return core_map, cap_dia
