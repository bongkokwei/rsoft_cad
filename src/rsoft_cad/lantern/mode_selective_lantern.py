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
from rsoft_cad import LaunchType, MonitorType, TaperType


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
        highest_mode: str = "LP02",
        launch_mode: str | list[str] = "LP01",
        taper_factor: float = 5,
        taper_length: float = 80000,
        core_diameters: dict[str, float] | None = None,
        savefile: bool = True,
        femnev: int = 1,
        data_dir: str = "output",
        opt_name: int | str = 0,
        sim_params: dict[str, any] | None = None,
        core_dia_dict: dict[str, float] | None = None,
        cladding_dia_dict: dict[str, float] | None = None,
        bg_index_dict: dict[str, float] | None = None,
        cladding_index_dict: dict[str, float] | None = None,
        core_index_dict: dict[str, float] | None = None,
        monitor_type: MonitorType = MonitorType.FIBER_POWER,
        # Updated type hint to allow dictionary of taper types
        taper_type: TaperType | dict[str, TaperType] = TaperType.LINEAR,
        launch_type: LaunchType = LaunchType.GAUSSIAN,
        # Updated type hint to allow list of filenames
        custom_taper_filename: str | list[str] = "custom.dat",
    ) -> dict[str, tuple[float, float]]:
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
            launch_mode (str | list[str]): The mode(s) to launch from (default: "LP01")
            taper_factor (float): The factor by which the fibers are tapered (default: 5)
            taper_length (float): The length of the taper in microns (default: 80000)
            core_diameters (dict[str, float] | None): Dictionary mapping mode names to core diameters.
                                          If None, default values will be used.
                                          Example: {"LP01": 10.7, "LP11a": 9.6}
            savefile (bool): Whether to save the design file (default: True)
            femnev (int): Number of eigenmodes to find in FEM simulation (default: 1)
            opt_name (int | str): Optional name identifier for the output file (default: 0)
            sim_params (dict[str, any] | None): Dictionary of simulation parameters to override defaults.
                                       Any parameter that can be passed to update_global_params.
                                       Example: {
                                         "grid_size": 0.5,
                                         "boundary_max": 100,
                                         "sim_tool": "ST_FEMSIM"
                                       }
            core_dia_dict (dict[str, float] | None): Dictionary to set core diameters for specific modes
            cladding_dia_dict (dict[str, float] | None): Dictionary to set cladding diameters for specific modes
            bg_index_dict (dict[str, float] | None): Dictionary to set background indices for specific modes
            cladding_index_dict (dict[str, float] | None): Dictionary to set cladding indices for specific modes
            core_index_dict (dict[str, float] | None): Dictionary to set core indices for specific modes
            monitor_type: Type of monitor to add to each pathway. Defaults to FIBER_POWER.
            taper_type: Taper profile to use if tapering is applied. Defaults to LINEAR.
            launch_type: Type of field distribution to launch. Defaults to GAUSSIAN.


        Returns:
            dict[str, tuple[float, float]]: The core map showing the spatial layout of supported modes
        """
        # Create a core map for the specified highest mode
        core_map, cap_dia = create_core_map(highest_mode, self.cladding_dia)
        self.cap_dia = cap_dia

        # Update the bundle with spatial coordinates from the core map
        self.update_bundle_with_core_map(core_map)

        # Reset num_cores
        self.num_cores = len(self.bundle)

        # Use provided core diameters or set defaults

        if core_dia_dict is not None:
            self.fiber_config.set_core_dia(core_dia_dict)
        else:
            core_diameters = {
                "LP01": 10.7,  # Fundamental mode gets largest core
                "LP11a": 9.6,  # First higher-order mode pair
                "LP11b": 9.6,
                "LP21a": 8.5,  # Second higher-order mode pair
                "LP21b": 8.5,
                "LP02": 7.35,  # Second radial mode gets smallest core
            }
            self.fiber_config.set_core_dia(core_diameters)

        if cladding_dia_dict is not None:
            self.fiber_config.set_cladding_dia(cladding_dia_dict)

        if cladding_index_dict is not None:
            self.fiber_config.set_cladding_index(cladding_index_dict)

        if core_index_dict is not None:
            self.fiber_config.set_core_index(core_index_dict)

        if bg_index_dict is not None:
            self.fiber_config.set_bg_index(bg_index_dict)

        # Configure fiber properties
        self.set_taper_factor(taper_factor)
        self.set_taper_length(taper_length)

        # Check if taper_type is a dictionary (different taper types for different segments)
        if isinstance(taper_type, dict):
            # If taper_type is a dictionary, custom_taper_filename must be a list
            # to provide matching filenames for each non-linear taper type
            if not isinstance(custom_taper_filename, list):
                raise ValueError(
                    "custom_taper_filename must be a list when taper_type is a dictionary"
                )

            # Each non-linear taper needs its own filename, so lists must match in length
            if len(taper_type) != len(custom_taper_filename):
                raise ValueError(
                    "taper_type dictionary and custom_taper_filename list must have the same length"
                )

            # Iterate through the taper dictionary items and filenames together
            # Each segment (key) has its own taper type and corresponding filename
            for (key, taper), filename in zip(
                taper_type.items(),  # Returns (key, value) pairs from dictionary
                custom_taper_filename,
            ):
                # Only add user taper for non-linear taper types
                if taper != TaperType.LINEAR:
                    # Add custom taper profile from the file for this segment
                    self.add_user_taper(filename=filename)
        # If taper_type is not a dictionary but a single non-linear taper type
        elif taper_type != TaperType.LINEAR:
            # Add a single custom taper profile for all segments
            self.add_user_taper(filename=custom_taper_filename)

        # Add fiber segments using segment manager
        self.segment_manager.add_fiber_segment(
            self.bundle,
            core_or_clad="core",
            taper_type=(
                taper_type if not isinstance(taper_type, dict) else taper_type["fiber"]
            ),
            monitor_type=monitor_type,
        )
        self.segment_manager.add_fiber_segment(
            self.bundle,
            core_or_clad="cladding",
            taper_type=(
                taper_type
                if not isinstance(taper_type, dict)
                else taper_type["cladding"]
            ),
            monitor_type=monitor_type,
        )
        self.segment_manager.add_capillary_segment(
            self.cap_dia,
            taper_factor,
            taper_length,
            taper_type=(
                taper_type if not isinstance(taper_type, dict) else taper_type["cap"]
            ),
        )

        # Configure the launch field
        if not isinstance(launch_mode, list):  # check if list
            self.segment_manager.launch_from_fiber(
                self.bundle,
                launch_mode,
                launch_type=launch_type,
            )
        else:  # more than one launch mode
            for mode in launch_mode:
                self.segment_manager.launch_from_fiber(
                    self.bundle,
                    mode,
                    launch_type=launch_type,
                )

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
        self.design_filepath = os.path.join(data_dir, f"mspl_{self.num_cores}_cores")
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
