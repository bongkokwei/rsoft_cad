"""
Base class for photonic lantern implementations with common functionality.
"""

from rsoft_cad.rsoft_circuit import RSoftCircuit
from rsoft_cad.constants import DEFAULT_FIBER_PROPS


class BaseLantern(RSoftCircuit):
    """
    Base class for photonic lantern implementations with common functionality.
    """

    def __init__(self, **params):
        """
        Initialize the base lantern with default parameters.

        Args:
            **params: Any parameters to override default fiber properties
        """
        super().__init__()

        # Default properties
        self.cladding_dia = 125.0
        self.cap_dia = 125.0
        self.num_cores = 0
        self.design_filepath = "default"
        self.design_filename = "lantern.ind"

        # Initialize default fiber properties
        self.default_fiber_props = DEFAULT_FIBER_PROPS.copy()

        # Update defaults with any provided parameters
        self.default_fiber_props.update(params)

        # Initialize empty bundle to store fiber configurations
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
        Set the same taper length for all fibers in the bundle.

        Args:
            taper_length: The taper length to set for all fibers in microns (default: 10000).
        """
        self.default_fiber_props["taper_length"] = taper_length
        for mode in self.bundle:
            self.bundle[mode]["taper_length"] = taper_length

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

    def __str__(self):
        """
        Custom string representation of the BaseLantern object.

        Returns:
            str: A formatted string showing all fiber properties in the bundle
        """
        if not self.bundle:
            return "Empty Lantern (no fibers configured)"

        result = []
        for label, fiber_prop_dict in self.bundle.items():
            result.append(f"{label}:")
            for key, prop in fiber_prop_dict.items():
                result.append(f"\t{key}: {prop}")

        return "\n".join(result)
