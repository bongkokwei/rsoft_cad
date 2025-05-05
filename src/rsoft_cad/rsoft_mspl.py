from rsoft_cad.rsoft_circuit import RSoftCircuit
from rsoft_cad.utils import lantern_layout, visualise_lantern
from rsoft_cad.rsoft_circuit import RSoftCircuit

import matplotlib.pyplot as plt
import numpy as np
import os

lp_mode_cutoffs_freq = {
    "LP01": 0.000,  # No cutoff (always guided)
    "LP11": 2.405,  # First zero of J0
    "LP21": 3.832,  # First zero of J1
    "LP02": 3.832,  # Second zero of J0
    "LP31": 5.136,  # First zero of J2
    "LP12": 5.520,  # Second zero of J1
    "LP41": 6.380,  # First zero of J3
    "LP22": 7.016,  # Second zero of J2
    "LP03": 7.016,  # Third zero of J0
    "LP51": 7.588,  # First zero of J4
    "LP13": 8.654,  # Third zero of J1
    "LP32": 8.417,  # Second zero of J3
    "LP61": 8.772,  # First zero of J5
    "LP42": 9.761,  # Second zero of J4
    "LP71": 9.936,  # First zero of J6
    "LP23": 10.174,  # Third zero of J2
    "LP04": 10.174,  # Fourth zero of J0
    "LP52": 11.065,  # Second zero of J5
    "LP81": 11.086,  # First zero of J7
    "LP33": 11.620,  # Third zero of J3
    "LP14": 11.792,  # Fourth zero of J1
    "LP91": 12.225,  # First zero of J8
    "LP62": 12.339,  # Second zero of J6
    "LP43": 13.015,  # Third zero of J4
    "LP24": 13.324,  # Fourth zero of J2
    "LP05": 13.324,  # Fifth zero of J0
}


class ModeSelectiveLantern(RSoftCircuit):
    """
    Generate a mode selective lantern by specifying the LP mode with the highest cutoff frequency.

    A mode selective lantern is a photonic device that converts between a multimode fiber and
    multiple single-mode fibers, where each single-mode fiber supports a specific spatial mode.
    This class handles the design and configuration of such lanterns based on optical mode theory.
    """

    def __init__(self, **params):
        super().__init__()

        # Lantern LP mode with highest cutoff
        self.cladding_dia = 125.0  # TODO: check if most fibers have 125 micron cladding
        self.cap_dia = 125.0
        self.num_cores = 0
        self.design_filepath = "default"
        self.design_filename = "mspl.ind"

        self.default_fiber_props = {
            "core_dia": 10.4,  # Core diameter in microns
            "cladding_dia": 125.0,  # Cladding diameter in microns
            "core_index": 1.45213,  # Core refractive index
            "cladding_index": 1.44692,  # Cladding refractive index
            # "bg_index": 1.44346,
            "bg_index": 1.4345,
            "pos_x": 0,  # X position in microns
            "pos_y": 0,  # Y position in microns
            "pos_z": 0,  # Z position in microns
            "taper_factor": 1,
            "taper_length": 80000,
        }

        # Update defaults with any provided parameters
        self.default_fiber_props.update(params)
        # Initialize empty bundle to store fiber configurations for each mode
        self.bundle = {}

        # Default simulation parameters
        self.update_global_params(
            structure="STRUCT_FIBER",
            cad_aspectratio_x=50,
            cad_aspectratio_y=50,
            background_index=self.default_fiber_props["bg_index"],
            grid_size=1,
            grid_size_y=1,
            fem_nev=1,  # Number of modes to find
            sim_tool="ST_BEAMPROP",
            slice_display_mode="DISPLAY_CONTOURMAPXZ",
        )

    def set_core_dia(self, core_dict):
        """
        Set the core diameter for specified modes in the bundle.

        Args:
            core_dict: Dictionary mapping mode names to core diameters.
                       Example: {"LP01": 8.2, "LP11a": 9.5}
        """
        for mode, core_dia in core_dict.items():
            if mode in self.bundle:
                self.bundle[mode]["core_dia"] = core_dia

    def set_core_index(self, core_index_dict):
        """
        Set the core refractive index for specified modes in the bundle.

        Args:
            core_index_dict: Dictionary mapping mode names to core refractive indices.
                             Example: {"LP01": 1.4682, "LP11a": 1.4685}
        """
        for mode, core_index in core_index_dict.items():
            if mode in self.bundle:
                self.bundle[mode]["core_index"] = core_index

    def set_cladding_dia(self, cladding_dia_dict):
        """
        Set the cladding diameter for specified modes in the bundle.

        Args:
            cladding_dia_dict: Dictionary mapping mode names to cladding diameters in microns.
                               Example: {"LP01": 125.0, "LP11a": 125.0}
        """
        for mode, cladding_dia in cladding_dia_dict.items():
            if mode in self.bundle:
                self.bundle[mode]["cladding_dia"] = cladding_dia

    def set_cladding_index(self, cladding_index_dict):
        """
        Set the cladding refractive index for specified modes in the bundle.

        Args:
            cladding_index_dict: Dictionary mapping mode names to cladding refractive indices.
                                 Example: {"LP01": 1.4629, "LP11a": 1.4630}
        """
        for mode, cladding_index in cladding_index_dict.items():
            if mode in self.bundle:
                self.bundle[mode]["cladding_index"] = cladding_index

    def set_bg_index(self, bg_index_dict):
        """
        Set the background refractive index for specified modes in the bundle.

        Args:
            bg_index_dict: Dictionary mapping mode names to background refractive indices.
                           Example: {"LP01": 1.0, "LP11a": 1.0}
        """
        for mode, bg_index in bg_index_dict.items():
            if mode in self.bundle:
                self.bundle[mode]["bg_index"] = bg_index

    def set_taper_factor(self, taper_factor=1):
        """
        Set the same taper factor for all fibers in the bundle.

        Args:
            taper_factor: The taper factor to set for all fibers (default: 1).
                          A taper factor of 1 means no tapering.
        """
        self.default_fiber_props["taper_factor"] = taper_factor
        for mode in self.bundle:
            self.bundle[mode]["taper_factor"] = taper_factor

    def set_taper_length(self, taper_length=10000):
        """
        Set the same taper factor for all fibers in the bundle.

        Args:
            taper_factor: The taper factor to set for all fibers (default: 1).
                          A taper factor of 1 means no tapering.
        """
        self.default_fiber_props["taper_length"] = taper_length
        for mode in self.bundle:
            self.bundle[mode]["taper_length"] = taper_length

    def multilayer_lantern_layout(self, cladding_dia, layers_config):
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
                    layer_centres.append(
                        [(centres_x[i], centres_y[i]) for i in range(n)]
                    )
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

    def get_modes_below_cutoff(self, input_mode, lp_mode_cutoffs_freq):
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
            mode
            for mode, cutoff in lp_mode_cutoffs_freq.items()
            if cutoff <= input_cutoff
        ]

        # Sort by cutoff frequency
        return sorted(modes_below_cutoff, key=lambda mode: lp_mode_cutoffs_freq[mode])

    def group_modes_by_radial_number(self, supported_modes):
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

    def create_layers_config(self, radial_groups, scale_factors=None):
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
        """
        if scale_factors is None:
            # Default scale factors increasing by 0.2 for each layer
            scale_factors = {r: 1 for r in radial_groups.keys()}

        layers_config = []

        # Sort radial numbers in descending order (so radial=1 is the outer layer)
        sorted_radial_numbers = sorted(radial_groups.keys(), reverse=True)

        for radial_num in sorted_radial_numbers:
            modes = radial_groups[radial_num]

            # Count circles based on azimuthal numbers
            num_circles = 0
            for mode in modes:
                # Extract azimuthal number (first digit in the mode name)
                azimuthal_num = int(mode[2])

                # Add 2 circles if azimuthal > 0, otherwise add 1
                num_circles += 2 if azimuthal_num > 0 else 1

            # Add the layer configuration
            scale_factor = scale_factors.get(radial_num, 1.0)
            layers_config.append((num_circles, scale_factor))
            self.num_cores += num_circles

        return layers_config

    def create_core_map(self, lp_mode_str):
        """
        Creates a mapping between optical modes and their physical coordinates in the fiber.

        This function:
        1. Determines which modes are supported based on a cutoff frequency (LP13)
        2. Groups these modes by their radial number
        3. Creates a layer configuration where:
           - Modes with radial number = 1 are in the outer layer (reverse sorting)
           - Each radial mode group represents a layer
        4. Returns a dictionary where:
           - Keys are mode strings (e.g., "LP01", "LP11")
           - Values are single (x,y) coordinate tuples

        For modes with azimuthal number > 0 (which would normally get 2 coordinates),
        this function creates two separate keys in the dictionary:
        - Original mode name (e.g., "LP11") for the first coordinate
        - Modified mode name with 'b' suffix (e.g., "LP11b") for the second coordinate

        Returns:
            dict: Mapping of mode strings to their coordinate tuples
        """
        # Get supported modes below the cutoff
        supported_modes = self.get_modes_below_cutoff(lp_mode_str, lp_mode_cutoffs_freq)

        # Group modes by their radial number
        grouped_modes = self.group_modes_by_radial_number(supported_modes)

        # Create the layer configuration
        layer_config = self.create_layers_config(grouped_modes)

        # Get the coordinates for each layer
        layer_centres, layer_radii = self.multilayer_lantern_layout(
            self.cladding_dia,
            layer_config,
        )

        self.cap_dia = 2 * layer_radii[-1] + self.cladding_dia

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

        return core_map

    def update_bundle_with_core_map(self, core_map):
        """
        Updates the fiber bundle with position information from the core map.

        This function assigns spatial coordinates to each fiber in the bundle
        based on the mode-to-position mapping.

        Args:
            core_map (dict): Mapping of mode strings to (x,y) coordinate tuples
        """
        for key, coord_tuple in core_map.items():
            x, y = coord_tuple
            self.bundle[key] = self.default_fiber_props.copy()
            self.bundle[key]["pos_x"] = x
            self.bundle[key]["pos_y"] = y

    def add_fiber_segment(self, core_or_clad="core", segment_id=None, **params):
        """
        Add a fiber segment with core and cladding based on fiber properties.

        Parameters:
        core_or_cladding (str):
        segment_id (int, optional): ID for the segment. If None, auto-incremented.

        Returns:
        str: The generated segment text
        """

        for lp_mode, fiber_prop in self.bundle.items():
            delta = fiber_prop[f"{core_or_clad}_index"] - fiber_prop[f"bg_index"]
            # Default segment properties
            segment_prop = {
                "comp_name": f"{lp_mode}_{core_or_clad.upper()}",
                "begin.x": fiber_prop["pos_x"],
                "begin.y": fiber_prop["pos_y"],
                "begin.z": 0,
                "begin.height": fiber_prop[f"{core_or_clad}_dia"],
                "begin.width": fiber_prop[f"{core_or_clad}_dia"],
                "begin.delta": delta,
                "end.x": fiber_prop["pos_x"] / fiber_prop["taper_factor"],
                "end.y": fiber_prop["pos_y"] / fiber_prop["taper_factor"],
                "end.z": fiber_prop["taper_length"],
                "end.height": fiber_prop[f"{core_or_clad}_dia"]
                / fiber_prop["taper_factor"],
                "end.width": fiber_prop[f"{core_or_clad}_dia"]
                / fiber_prop["taper_factor"],
                "end.delta": delta,
            }

            if fiber_prop["taper_factor"] > 1:
                segment_prop.update(
                    width_taper="TAPER_LINEAR",
                    height_taper="TAPER_LINEAR",
                    position_y_taper="TAPER_LINEAR",
                    position_taper="TAPER_LINEAR",
                )
            self.add_segment(**segment_prop)
            if core_or_clad == "core":
                # Add pathway with this segment
                self.add_pathways(segment_ids=self.segment_counter)
                self.add_pathways_monitor(
                    pathway_id=self.pathway_counter,
                    **{"monitor_type": "MONITOR_FIELD_NEFF"},
                )
        return True

    def add_capillary_segment(self):
        """
        Add a fiber segment with core and cladding based on fiber properties.

        Parameters:
        core_or_cladding (str):
        segment_id (int, optional): ID for the segment. If None, auto-incremented.

        Returns:
        str: The generated segment text
        """

        delta = 0
        # Default segment properties
        segment_prop = {
            "comp_name": "CAPILLARY",
            "begin.x": 0,
            "begin.y": 0,
            "begin.z": 0,
            "begin.height": self.cap_dia,
            "begin.width": self.cap_dia,
            "begin.delta": delta,
            "end.x": 0,
            "end.y": 0,
            "end.z": self.default_fiber_props["taper_length"],
            "end.height": self.cap_dia / self.default_fiber_props["taper_factor"],
            "end.width": self.cap_dia / self.default_fiber_props["taper_factor"],
            "end.delta": delta,
        }

        if self.default_fiber_props["taper_factor"] > 1:
            segment_prop.update(
                width_taper="TAPER_LINEAR",
                height_taper="TAPER_LINEAR",
                position_y_taper="TAPER_LINEAR",
                position_taper="TAPER_LINEAR",
            )
        self.add_segment(**segment_prop)

        # Add pathway with this segment
        self.add_pathways(segment_ids=self.segment_counter)
        self.add_pathways_monitor(pathway_id=self.pathway_counter)

        return True

    def launch_from_fiber(self, lp_node):
        self.add_launch_field(
            launch_type="LAUNCH_GAUSSIAN",
            launch_tilt=0,
            # launch_file="femsim_LP01_ex.m00",
            # launch_file_explicit=1,
            launch_pathway=self.pathway_counter,
            launch_width=self.bundle[lp_node]["core_dia"],
            launch_height=self.bundle[lp_node]["core_dia"],
            launch_position=self.bundle[lp_node]["pos_x"],
            launch_position_y=self.bundle[lp_node]["pos_y"],
        )

    @staticmethod
    def find_segment_by_comp_name(segments, comp_name):
        for segment in segments:
            if f"{comp_name}" in segment:
                # Extract segment number only
                segment_line = segment.split("\n")[0]  # Get "segment X" line
                segment_number = segment_line.replace("segment ", "").strip()
                return segment_number

        # Raise an exception if component is not found
        raise ValueError(f"Component '{comp_name}' not found in any segment")

    def create_lantern(
        self,
        highest_mode="LP02",
        launch_mode="LP01",
        taper_factor=5,
        taper_length=80000,
        core_diameters=None,
        savefile=True,
        femnev=1,
        femsim=True,
        opt_name=0,
        sim_params=None,
    ):
        """
        Create and configure an example mode selective lantern.

        This method demonstrates the complete process of creating a mode selective lantern:
        1. Creating a core map based on the highest supported mode
        2. Updating the bundle with spatial coordinates
        3. Fine-tuning core diameters for each supported mode
        4. Setting the taper factor
        5. Adding fiber segments (core and cladding)
        6. Adding a capillary segment
        7. Configuring the launch field
        8. Setting simulation parameters

        Args:
            highest_mode (str): The highest LP mode to support (default: "LP02")
            launch_mode (str): The mode to launch from (default: "LP01")
            core_diameters (dict, optional): Dictionary mapping mode names to core diameters.
                                          If None, default values will be used.
                                          Example: {"LP01": 10.7, "LP11a": 9.6}
            taper_factor (float): The factor by which the fibers are tapered (default: 5)
            taper_length (float): The length of the taper in microns (default: 80000)
            savefile (bool): Whether to save the design file (default: True)
            femnev (int): Number of eigenmodes to find in FEM simulation (default: 1)
            femsim (bool): Whether to use FEM simulation (default: True)
            opt_name (int or str): Optional name identifier for the output file (default: 0)
            sim_params (dict, optional): Dictionary of simulation parameters to override defaults.
                                       Any parameter that can be passed to update_global_params.
                                       Example: {
                                         "grid_size": 0.5,
                                         "boundary_max": 100,
                                         "sim_tool": "ST_FEMSIM"
                                       }

        Returns:
            dict: The core map showing the spatial layout of supported modes
        """
        # Create a core map for the specified highest mode
        core_map = self.create_core_map(highest_mode)

        # Update the bundle with spatial coordinates from the core map
        self.update_bundle_with_core_map(core_map)

        # Use provided core diameters or set defaults
        if core_diameters is None:
            # Default core diameters to use if none provided
            core_diameters = {
                "LP01": 10.7,  # Fundamental mode gets largest core
                "LP11a": 9.6,  # First higher-order mode pair
                "LP11b": 9.6,
                "LP21a": 8.5,  # Second higher-order mode pair
                "LP21b": 8.5,
                "LP02": 7.35,  # Second radial mode gets smallest core
            }

        # Filter the core diameters to only include modes that exist in the bundle
        core_dia_dict = {
            mode: diameter
            for mode, diameter in core_diameters.items()
            if mode in self.bundle
        }

        self.set_core_dia(core_dia_dict)
        self.set_taper_factor(taper_factor)
        self.set_taper_length(taper_length)

        # Add fiber segments
        self.add_fiber_segment(core_or_clad="core")
        self.add_fiber_segment(core_or_clad="cladding")
        self.add_capillary_segment()

        # Configure the launch field
        if not isinstance(launch_mode, list):
            self.launch_from_fiber(launch_mode)
        else:
            for mode in launch_mode:
                self.launch_from_fiber(lp_node=mode)

        # Prepare default simulation parameters
        default_sim_params = {
            "grid_size": 1,
            "grid_size_y": 1,
            "fem_nev": femnev,
            "slice_display_mode": "DISPLAY_CONTOURMAPXY",
        }

        # Override defaults with user-provided simulation parameters
        if sim_params:
            default_sim_params.update(sim_params)

        # Update global parameters with combined simulation settings
        self.update_global_params(**default_sim_params)

        # Configure the design file name and directory
        self.design_filepath = os.path.join("output", f"mspl_{self.num_cores}_cores")
        self.design_filename = f"mspl_{self.num_cores}_cores_{opt_name}.ind"

        if savefile:
            self.write(
                os.path.join(
                    self.design_filepath,
                    self.design_filename,
                )
            )

        return core_map

    def __str__(self):
        """
        Custom string representation of the ModeSelectiveLantern object.

        Returns:
            str: A formatted string showing all fiber properties in the bundle
        """
        if not self.bundle:
            return "Empty ModeSelectiveLantern (no fibers configured)"

        result = []
        for label, fiber_prop_dict in self.bundle.items():
            result.append(f"{label}:")
            for key, prop in fiber_prop_dict.items():
                result.append(f"\t{key}: {prop}")

        return "\n".join(result)


if __name__ == "__main__":
    # Create a mode selective lantern instance
    mspl = ModeSelectiveLantern()
    core_map = mspl.create_lantern(
        highest_mode="LP11",
        launch_mode="LP01",
        savefile=True,
        opt_name="prototype",
        femsim=False,
    )

    print(mspl)

    # Visualize the lantern design
    fig, ax = visualise_lantern(core_map)
    plt.show()
