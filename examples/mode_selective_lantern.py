from rsoft_cad.rsoft_circuit import RSoftCircuit
from rsoft_cad.utils.cir_lantern_layout import lantern_layout
from rsoft_cad.utils.plot_utils import visualise_lantern
from rsoft_cad.rsoft_circuit import RSoftCircuit

import matplotlib.pyplot as plt


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
        self.default_fiber_props = {
            "core_dia": 8.2,  # Core diameter in microns
            "cladding_dia": 125.0,  # Cladding diameter in microns
            "core_index": 1.45213,  # Core refractive index
            "cladding_index": 1.44692,  # Cladding refractive index
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
        self.update_global_params(
            cad_aspectratio_x=50,
            cad_aspectratio_y=50,
            background_index=self.default_fiber_props["bg_index"],
            grid_size=1,
            grid_size_y=1,
            fem_nev=1,  # Number of modes to find
            sim_tool="ST_BEAMPROP",
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

    def multilayer_lantern_layout(self, cladding_dia, layers_config):
        """
        Computes the positions of circles arranged in multiple concentric layers.
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

        for layer_idx, (n, radius_factor) in enumerate(layers_config):
            # Calculate the basic layout for this layer
            R, centres_x, centres_y = lantern_layout(cladding_dia, n)

            # Apply the radius factor to adjust the distance from center
            adjusted_R = R * radius_factor
            adjusted_centres_x = centres_x * radius_factor
            adjusted_centres_y = centres_y * radius_factor

            # Create a list of (x,y) coordinate tuples for this layer
            layer_coords = [
                (adjusted_centres_x[i], adjusted_centres_y[i])
                for i in range(len(adjusted_centres_x))
            ]

            # Add to our layer lists
            layer_centres.append(layer_coords)
            layer_radii.append(adjusted_R)

        return layer_centres, layer_radii

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
            scale_factors = {r: 1.2 for r in radial_groups.keys()}

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

        self.cap_dia = layer_radii[-1] + 2 * self.cladding_dia

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
                self.add_pathways_monitor(pathway_id=self.pathway_counter)
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


if __name__ == "__main__":
    # Create a mode selective lantern instance
    mspl = ModeSelectiveLantern()

    # Create a core map for LP02 mode (this will support 6 modes: LP01, LP11a/b, LP21a/b, LP02)
    core_map = mspl.create_core_map("LP02")

    # Update the bundle with spatial coordinates from the core map
    mspl.update_bundle_with_core_map(core_map)

    # Fine-tune the core diameters for each supported mode to optimize mode selectivity
    mspl.set_core_dia(
        {
            "LP01": 10.7,  # Fundamental mode gets largest core
            "LP11a": 9.6,  # First higher-order mode pair
            "LP11b": 9.6,
            "LP21a": 8.5,  # Second higher-order mode pair
            "LP21b": 8.5,
            "LP02": 7.35,  # Second radial mode gets smallest core
        }
    )
    mspl.set_taper_factor(13)

    # Print the properties of each fiber in the bundle
    for label, fiber_prop_dict in mspl.bundle.items():
        print(f"{label}:")
        for key, prop in fiber_prop_dict.items():
            print(f"\t{key}: {prop}")

    launch_mode = "LP02"
    mspl.add_fiber_segment(core_or_clad="core")
    mspl.add_fiber_segment(core_or_clad="cladding")
    mspl.add_capillary_segment()
    mspl.launch_from_fiber(launch_mode)

    mspl.write(f"output/mspl/mspl_{launch_mode}.ind")

    # # Visualize the lantern design
    # fig, ax = visualise_lantern(core_map)
    # plt.show()
