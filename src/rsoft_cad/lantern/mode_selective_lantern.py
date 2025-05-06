"""
Mode Selective Photonic Lantern implementation.
"""

import os
import matplotlib.pyplot as plt

from rsoft_cad.lantern.base_lantern import BaseLantern
from rsoft_cad.lantern.fiber_config import FiberConfigurator
from rsoft_cad.lantern.segment_manager import SegmentManager
from rsoft_cad.utils import visualise_lp_lantern
from rsoft_cad.layout import create_core_map


class ModeSelectiveLantern(BaseLantern):
    """
    Generate a mode selective lantern by specifying the LP mode with the highest cutoff frequency.

    A mode selective lantern is a photonic device that converts between a multimode fiber and
    multiple single-mode fibers, where each single-mode fiber supports a specific spatial mode.
    This class handles the design and configuration of such lanterns based on optical mode theory.
    """

    def __init__(self, **params):
        """
        Initialize the Mode Selective Lantern with default parameters.

        Args:
            **params: Parameters to override default fiber properties
        """
        # Initialize base class
        super().__init__(**params)

        # Set default filename specific to mode selective lantern
        self.design_filename = "mspl.ind"

        # Create helper objects using composition
        self.fiber_config = FiberConfigurator(self.bundle)
        self.segment_manager = SegmentManager(self)

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
        Create and configure a mode selective lantern.

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
        core_map, cap_dia = create_core_map(highest_mode, self.cladding_dia)
        self.cap_dia = cap_dia

        # Update the bundle with spatial coordinates from the core map
        self.update_bundle_with_core_map(core_map)

        # Reset num_cores
        self.num_cores = len(self.bundle)

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
        core_dia_dict = self.fiber_config.filter_core_diameters(core_diameters)

        # Configure fiber properties
        self.fiber_config.set_core_dia(core_dia_dict)
        self.set_taper_factor(taper_factor)
        self.set_taper_length(taper_length)

        # Add fiber segments using segment manager
        self.segment_manager.add_fiber_segment(self.bundle, core_or_clad="core")
        self.segment_manager.add_fiber_segment(self.bundle, core_or_clad="cladding")
        self.segment_manager.add_capillary_segment(
            self.cap_dia, taper_factor, taper_length
        )

        # Configure the launch field
        if not isinstance(launch_mode, list):
            self.segment_manager.launch_from_fiber(self.bundle, launch_mode)
        else:
            for mode in launch_mode:
                self.segment_manager.launch_from_fiber(self.bundle, mode)

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

        # Set simulation parameters
        self.update_global_params(**default_sim_params)

        # Configure the design file name and directory
        self.design_filepath = os.path.join("output", f"mspl_{self.num_cores}_cores")
        self.design_filename = f"mspl_{self.num_cores}_cores_{opt_name}.ind"

        # Save the design file if requested
        if savefile:
            os.makedirs(self.design_filepath, exist_ok=True)
            self.write(
                os.path.join(
                    self.design_filepath,
                    self.design_filename,
                )
            )

        # Return the core map
        return core_map


def visualise_and_save_lantern(core_map, filename=None):
    """
    Utility function to visualize a lantern design and optionally save the figure.

    Args:
        core_map (dict): Core map from create_lantern method
        filename (str, optional): If provided, save the figure to this path

    Returns:
        tuple: (fig, ax) Matplotlib figure and axes objects
    """
    # Visualize the lantern design
    fig, ax = visualise_lp_lantern(core_map)

    # Save if filename is provided
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches="tight")

    return fig, ax


if __name__ == "__main__":
    # Create a mode selective lantern instance
    mspl = ModeSelectiveLantern()
    core_map = mspl.create_lantern(
        highest_mode="LP11",
        launch_mode="LP01",
        savefile=False,
        opt_name="prototype",
        femsim=False,
    )

    print(mspl)

    # Visualize the lantern design
    fig, ax = visualise_and_save_lantern(core_map)
    plt.show()
