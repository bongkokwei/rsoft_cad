"""
Photonic Lantern implementation.
"""

import os
import matplotlib.pyplot as plt

from rsoft_cad.lantern.base_lantern import BaseLantern
from rsoft_cad.lantern.fiber_config import FiberConfigurator
from rsoft_cad.lantern.segment_manager import SegmentManager
from rsoft_cad.utils import visualise_lp_lantern
from rsoft_cad.layout import create_indexed_core_map
from rsoft_cad.geometry import model_photonic_lantern_taper, extract_lantern_endpoints
from rsoft_cad import LaunchType, MonitorType, TaperType


class PhotonicLantern(BaseLantern):
    """
    Generate a photonic lantern by specifying the number of cores in concentric rings.
    """

    def __init__(self, **params):
        """
        Initialize the photonic lantern with default parameters.

        Args:
            **params: Parameters to override default fiber properties
        """
        # Initialize base class
        super().__init__(**params)

        # Set default filename for photonic lantern
        self.design_filename = "photonic_lantern.ind"

        # Create helper objects using composition
        self.fiber_config = FiberConfigurator(self.bundle)
        self.segment_manager = SegmentManager(self)

    def configure_tapers(self, taper_config):
        """
        Configure taper types and add custom taper profiles when needed.

        Args:
            taper_config (TaperType | dict[str, TaperType]): Either a single taper type
                for all segments or a dictionary mapping segment names to their taper types.
        """
        # Handle dictionary of segment-specific tapers
        if isinstance(taper_config, dict):
            for segment_key, taper in taper_config.items():
                if taper.is_user_taper() and taper.custom_filename:
                    self.add_user_taper(filename=taper.custom_filename)
        # Handle a single taper for all segments
        elif isinstance(taper_config, TaperType) and taper_config.is_user_taper():
            if taper_config.custom_filename:
                self.add_user_taper(filename=taper_config.custom_filename)

    def get_segment_taper_type(self, taper_config, segment_key):
        if isinstance(taper_config, dict):
            return taper_config.get(segment_key, TaperType.linear()).taper_type
        return taper_config.taper_type

    def create_lantern(
        self,
        layer_config: list,
        launch_mode: str | list[str] = "0",
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
        Create and configure a photonic lantern.

        This method demonstrates the complete process of creating a photonic lantern:
        1. Creating a core map based on the layer configuration
        2. Updating the bundle with spatial coordinates
        3. Configuring core diameters for each fiber
        4. Setting the taper factor and length
        5. Adding fiber segments (core and cladding)
        6. Adding a capillary segment
        7. Configuring the launch field
        8. Setting simulation parameters

        Args:
            layer_config (list): List of tuples (num_circles, scale_factor) for each layer
            launch_mode (str | list[str]): The mode(s) to launch from (default: "0")
            taper_factor (float): The factor by which the fibers are tapered (default: 1)
            taper_length (float): The length of the taper in microns (default: 80000)
            core_diameters (dict[str, float] | None): Dictionary mapping fiber names to core diameters.
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
            core_dia_dict (dict[str, float] | None): Dictionary to set core diameters for specific fibers
            cladding_dia_dict (dict[str, float] | None): Dictionary to set cladding diameters for specific fibers
            bg_index_dict (dict[str, float] | None): Dictionary to set background indices for specific fibers
            cladding_index_dict (dict[str, float] | None): Dictionary to set cladding indices for specific fibers
            core_index_dict (dict[str, float] | None): Dictionary to set core indices for specific fibers
            monitor_type: Type of monitor to add to each pathway. Defaults to FIBER_POWER.
            taper_config: Taper profile to use if tapering is applied. Defaults to LINEAR.
            launch_type: Type of field distribution to launch. Defaults to GAUSSIAN.
            capillary_od (float): Outer diameter of the capillary in microns (default: 900)
            final_capillary_id (float): Final inner diameter of the capillary after tapering in microns (default: 40)
            num_points (int): Number of points along z-axis for model discretization (default: 100)

        Returns:
            dict[str, tuple[float, float]]: The core map showing the spatial layout of fiber cores
        """
        # Create a core map based on the layer configuration
        core_map, cap_dia = create_indexed_core_map(layer_config, self.cladding_dia)
        self.cap_dia = cap_dia

        # Update the bundle with spatial coordinates from the core map
        self.update_bundle_with_core_map(core_map)

        # Reset num_cores
        self.num_cores = len(self.bundle)

        # Use provided core diameters or set defaults
        if core_dia_dict is not None:
            self.fiber_config.set_core_dia(core_dia_dict)
            # Update core_diameters for the model to use the same values
            core_diameters = core_dia_dict
        else:
            core_diameters = {fiber_name: 10.4 for fiber_name in core_map.keys()}
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

        # Configure taper properties
        self.configure_tapers(taper_config)

        # Model the physical properties of the lantern
        # This creates a 3D model of the photonic lantern's physical structure
        self.model = model_photonic_lantern_taper(
            z_points=num_points,  # Number of points along z-axis for model discretization
            taper_length=taper_length,  # Total length of the taper in microns
            cladding_diameter=self.default_fiber_props["cladding_dia"],
            final_capillary_id=final_capillary_id,  # Final inner diameter of capillary after tapering
            capillary_id=cap_dia,  # Initial inner diameter of the capillary
            capillary_od=capillary_od,  # Outer diameter of the capillary
            core_map=core_map,  # Spatial layout of fiber cores
            core_diameters=core_diameters,  # Diameters for each fiber core
        )

        (
            cladding_endpoints,
            core_endpoints,
            cap_endpoints,
        ) = extract_lantern_endpoints(self.model)

        # Add fiber segments using segment manager
        self.segment_manager.add_fiber_segment(
            self.bundle,
            core_or_clad="core",
            taper_type=self.get_segment_taper_type(taper_config, "core"),
            monitor_type=monitor_type,
            per_fiber_overrides=core_endpoints,
        )
        self.segment_manager.add_fiber_segment(
            self.bundle,
            core_or_clad="cladding",
            taper_type=self.get_segment_taper_type(taper_config, "cladding"),
            monitor_type=monitor_type,
            per_fiber_overrides=cladding_endpoints,
        )
        self.segment_manager.add_capillary_segment(
            self.cap_dia,
            taper_factor,
            taper_length,
            taper_type=self.get_segment_taper_type(taper_config, "cap"),
            segment_prop_overrides=cap_endpoints,
            monitor_type=MonitorType.PARTIAL_POWER,
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
        self.design_filepath = os.path.join(
            data_dir, f"photonic_lantern_{self.num_cores}_cores"
        )
        self.design_filename = f"photonic_lantern_{self.num_cores}_cores_{opt_name}.ind"

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
    # Create a photonic lantern instance
    pl = PhotonicLantern()
    example_config = [
        (1, 1.0),  # Center layer: 1 circle at center
        (6, 1.0),  # First ring: 6 circles
        (12, 1.0),  # Second ring: 12 circles
    ]

    core_map = pl.create_lantern(
        layer_config=example_config,
        launch_mode="0",
        savefile=True,
        opt_name="prototype",
    )

    # print(pl)

    # Visualize the lantern design
    fig, ax = visualise_and_save_lantern(core_map)
    plt.show()
