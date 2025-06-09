"""
Mode Selective Photonic Lantern implementation - Clean inheritance from PhotonicLantern.
"""

import os
import matplotlib.pyplot as plt

from rsoft_cad.lantern.photonic_lantern import (
    PhotonicLantern,
    visualise_and_save_lantern,
)
from rsoft_cad.layout import create_core_map
from rsoft_cad import LaunchType, MonitorType, TaperType


class ModeSelectiveLantern(PhotonicLantern):
    """
    Generate a mode selective lantern by specifying the LP mode with the highest cutoff frequency.

    A mode selective lantern is a photonic device that converts between a multimode fiber and
    multiple single-mode fibers, where each single-mode fiber supports a specific spatial mode.
    This class handles the design and configuration of such lanterns based on optical mode theory.

    Inherits from PhotonicLantern and overrides specific behaviors for mode-based configuration.
    """

    def __init__(self, **params):
        """
        Initialize the Mode Selective Lantern with default parameters.

        Args:
            **params: Parameters to override default fiber properties
        """
        # Initialize parent class
        super().__init__(**params)

        # Override default filename specific to mode selective lantern
        self.design_filename = "mspl.ind"

    def _create_core_map_and_capillary(self, highest_mode):
        """
        Create the core map and capillary diameter based on the highest supported mode.

        Overrides the parent method to use mode-based core map creation instead of layer-based.

        Args:
            highest_mode (str): The highest LP mode to support (e.g., "LP02", "LP11")

        Returns:
            tuple: (core_map, cap_dia)
        """
        return create_core_map(highest_mode, self.cladding_dia)

    def _get_default_launch_mode(self):
        """
        Get the default launch mode for mode selective lanterns.

        Returns:
            str: Default launch mode ("LP01")
        """
        return "LP01"

    def _get_output_file_prefix(self):
        """
        Get the file prefix for mode selective lantern output files.

        Returns:
            str: File prefix ("mspl")
        """
        return "mspl"

    def create_lantern(
        self,
        highest_mode: str = "LP02",
        launch_mode: str | list[str] | None = None,
        taper_factor: float = 1,
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
        taper_config: TaperType | dict[str, TaperType] = TaperType.linear(),
        launch_type: LaunchType = LaunchType.GAUSSIAN,
        capillary_od: float = 900,
        final_capillary_id: float = 40,
        num_points: int = 100,
    ) -> dict[str, tuple[float, float]]:
        """
        Create and configure a mode selective lantern.

        This method creates a mode selective lantern by specifying the highest supported LP mode.
        A mode selective lantern is a photonic device that converts between a multimode fiber and
        multiple single-mode fibers, where each single-mode fiber supports a specific spatial mode.

        The method performs the following steps:
        1. Creating a core map based on the highest LP mode cutoff frequency
        2. Updating the bundle with spatial coordinates from the core map
        3. Fine-tuning core diameters for each supported mode
        4. Setting the taper factor and length
        5. Adding fiber segments (core and cladding)
        6. Adding a capillary segment
        7. Configuring the launch field
        8. Setting simulation parameters

        All the heavy lifting is done by the parent class - this method provides the
        mode-specific interface and delegates to the parent.

        Args:
            highest_mode (str): The highest LP mode to support (default: "LP02")
                               Examples: "LP01", "LP11", "LP21", "LP02", "LP31", etc.
                               This determines which spatial modes the lantern will support.
            launch_mode (str | list[str] | None): The mode(s) to launch from (None uses "LP01")
                                                 Can be a single mode like "LP01" or a list like ["LP01", "LP11a"]
            taper_factor (float): The factor by which the fibers are tapered (default: 1)
                                 Controls how much the fiber dimensions change along the taper
            taper_length (float): The length of the taper in microns (default: 80000)
                                 Longer tapers generally provide better adiabatic mode conversion
            core_diameters (dict[str, float] | None): Dictionary mapping mode names to core diameters.
                                          If None, default values will be used.
                                          Example: {"LP01": 10.7, "LP11a": 9.6, "LP11b": 9.6}
            savefile (bool): Whether to save the design file (default: True)
            femnev (int): Number of eigenmodes to find in FEM simulation (default: 1)
                         Higher values compute more eigenmodes for analysis
            data_dir (str): Directory to save the design file (default: "output")
            opt_name (int | str): Optional name identifier for the output file (default: 0)
                                 Used for distinguishing different optimization runs
            sim_params (dict[str, any] | None): Dictionary of simulation parameters to override defaults.
                                       Any parameter that can be passed to update_global_params.
                                       Example: {
                                         "grid_size": 0.5,
                                         "boundary_max": 100,
                                         "sim_tool": "ST_FEMSIM"
                                       }
            core_dia_dict (dict[str, float] | None): Dictionary to set core diameters for specific modes
                                                    Alternative way to specify core diameters
            cladding_dia_dict (dict[str, float] | None): Dictionary to set cladding diameters for specific modes
            bg_index_dict (dict[str, float] | None): Dictionary to set background indices for specific modes
                                                    Controls the refractive index of the background material
            cladding_index_dict (dict[str, float] | None): Dictionary to set cladding indices for specific modes
                                                          Controls the refractive index of fiber claddings
            core_index_dict (dict[str, float] | None): Dictionary to set core indices for specific modes
                                                      Controls the refractive index of fiber cores
            monitor_type (MonitorType): Type of monitor to add to each pathway. Defaults to FIBER_POWER.
                                       Controls what quantities are monitored during simulation
            taper_config (TaperType | dict[str, TaperType]): Taper profile to use if tapering is applied.
                                                            Can be a single TaperType for all segments or
                                                            a dictionary mapping segment names to their taper types.
                                                            Examples: TaperType.linear(), TaperType.exponential()
                                                            Defaults to LINEAR.
            launch_type (LaunchType): Type of field distribution to launch. Defaults to GAUSSIAN.
                                     Controls the spatial profile of the launched optical field
            capillary_od (float): Outer diameter of the capillary in microns (default: 900)
                                 The capillary houses the tapered fiber bundle
            final_capillary_id (float): Final inner diameter of the capillary after tapering in microns (default: 40)
                                       Controls the final bundle size at the multimode end
            num_points (int): Number of points along z-axis for model discretization (default: 100)
                             Higher values provide more accurate modeling but increase computation time

        Returns:
            dict[str, tuple[float, float]]: The core map showing the spatial layout of supported modes.
                                           Keys are mode names (e.g., "LP01", "LP11a") and values are
                                           (x, y) coordinate tuples in microns showing where each
                                           single-mode fiber core is positioned.

        Raises:
            ValueError: If the highest_mode is not a valid LP mode designation
            ValueError: If core_diameters contains invalid mode names
            ValueError: If taper_factor or taper_length are non-positive
        """
        # Call parent's create_lantern method with the highest_mode as layer_config
        # The parent will call our overridden _create_core_map_and_capillary method
        return super().create_lantern(
            layer_config=highest_mode,  # This becomes the input to _create_core_map_and_capillary
            launch_mode=launch_mode,
            taper_factor=taper_factor,
            taper_length=taper_length,
            core_diameters=core_diameters,
            savefile=savefile,
            femnev=femnev,
            data_dir=data_dir,
            opt_name=opt_name,
            sim_params=sim_params,
            core_dia_dict=core_dia_dict,
            cladding_dia_dict=cladding_dia_dict,
            bg_index_dict=bg_index_dict,
            cladding_index_dict=cladding_index_dict,
            core_index_dict=core_index_dict,
            monitor_type=monitor_type,
            taper_config=taper_config,
            launch_type=launch_type,
            capillary_od=capillary_od,
            final_capillary_id=final_capillary_id,
            num_points=num_points,
        )


if __name__ == "__main__":
    # Create a mode selective lantern instance
    mspl = ModeSelectiveLantern()
    core_map = mspl.create_lantern(
        highest_mode="LP11",
        launch_mode="LP01",
        savefile=False,
        opt_name="prototype",
    )

    print(mspl)

    # Visualize the lantern design
    fig, ax = visualise_and_save_lantern(core_map)
    plt.show()
