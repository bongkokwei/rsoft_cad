"""
Module for handling fiber-specific configuration for photonic lanterns.
"""


class FiberConfigurator:
    """
    Handles fiber-specific configuration for photonic lanterns.
    """

    def __init__(self, bundle):
        """
        Initialize the fiber configurator.

        Args:
            bundle (dict): The fiber bundle to configure
        """
        self.bundle = bundle

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

    def filter_core_diameters(self, core_diameters):
        """
        Filter the core diameters to only include modes that exist in the bundle.

        Args:
            core_diameters (dict): Dictionary mapping mode names to core diameters

        Returns:
            dict: Filtered dictionary with only modes that exist in the bundle
        """
        return {
            mode: diameter
            for mode, diameter in core_diameters.items()
            if mode in self.bundle
        }
