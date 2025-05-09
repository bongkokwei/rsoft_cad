"""
Module for handling segment creation and management for photonic lanterns.

This module provides functionality to create and manage various segments in photonic lantern
structures, including fiber segments, capillary segments, and launching configurations.
It interfaces with RSoft CAD to implement the physical structures.
"""

from typing import Dict, Union, Any, Optional, List
from rsoft_cad import LaunchType, MonitorType, TaperType


class SegmentManager:
    """
    Handles the creation and management of segments for photonic lanterns.

    This class provides methods to add fiber segments (both core and cladding),
    capillary segments, and configure launch fields for simulation of photonic
    lantern structures.
    """

    def __init__(self, circuit_ref) -> None:
        """
        Initialize the segment manager with a reference to the circuit.

        Args:
            circuit_ref: Reference to the RSoftCircuit object that will be used
                         to add segments and pathways.
        """
        self.circuit = circuit_ref

    def add_fiber_segment(
        self,
        bundle: Dict[str, Dict[str, Union[float, str]]],
        core_or_clad: str = "core",
        monitor_type: MonitorType = MonitorType.FIBER_POWER,
        taper_type: TaperType = TaperType.LINEAR,
    ) -> bool:
        """
        Add a fiber segment with core and cladding based on fiber properties.

        Creates segments for each fiber in the bundle with appropriate dimensions
        and refractive index profiles. If adding core segments, also creates
        pathways and monitors for each segment.

        Args:
            bundle: Dictionary mapping LP mode names to fiber properties.
                   Each fiber property dict should contain keys for position ('pos_x', 'pos_y'),
                   dimensions ('core_dia', 'cladding_dia'), refractive indices
                   ('core_index', 'cladding_index', 'bg_index'), and taper properties
                   ('taper_factor', 'taper_length').
            core_or_clad: Whether to add "core" or "cladding" segments. Defaults to "core".
            monitor_type: Type of monitor to add to each pathway. Defaults to FIBER_POWER.
            taper_type: Taper profile to use if tapering is applied. Defaults to LINEAR.

        Returns:
            True if the segments were successfully added.
        """
        for lp_mode, fiber_prop in bundle.items():
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
                    width_taper=taper_type,
                    height_taper=taper_type,
                    position_y_taper=taper_type,
                    position_taper=taper_type,
                )
            self.circuit.add_segment(**segment_prop)
            if core_or_clad == "core":
                # Add pathway with this segment
                self.circuit.add_pathways(segment_ids=self.circuit.segment_counter)
                self.circuit.add_pathways_monitor(
                    pathway_id=self.circuit.pathway_counter,
                    monitor_type=monitor_type,
                )
        return True

    def add_capillary_segment(
        self,
        cap_dia: float,
        taper_factor: float,
        taper_length: float,
        taper_type: TaperType = TaperType.LINEAR,
    ) -> bool:
        """
        Add a capillary segment to contain the fibers.

        Creates a cylindrical segment centered at the origin that can serve as
        a container for the fiber bundle. The capillary can be tapered from its
        initial diameter by the specified taper factor.

        Args:
            cap_dia: Capillary diameter in microns
            taper_factor: Taper factor for the capillary (ratio of input to output diameter)
            taper_length: Taper length in microns
            monitor_type: Type of monitor to add to each pathway. Defaults to FIBER_POWER.
            taper_type: Taper profile to use if tapering is applied. Defaults to LINEAR.

        Returns:
            True if the capillary segment was successfully added
        """
        delta = 0
        # Default segment properties
        segment_prop = {
            "comp_name": "CAPILLARY",
            "begin.x": 0,
            "begin.y": 0,
            "begin.z": 0,
            "begin.height": cap_dia,
            "begin.width": cap_dia,
            "begin.delta": delta,
            "end.x": 0,
            "end.y": 0,
            "end.z": taper_length,
            "end.height": cap_dia / taper_factor,
            "end.width": cap_dia / taper_factor,
            "end.delta": delta,
        }

        if taper_factor > 1:
            segment_prop.update(
                width_taper=taper_type,
                height_taper=taper_type,
                position_y_taper=taper_type,
                position_taper=taper_type,
            )
        self.circuit.add_segment(**segment_prop)

        # Add pathway with this segment
        self.circuit.add_pathways(segment_ids=self.circuit.segment_counter)
        self.circuit.add_pathways_monitor(pathway_id=self.circuit.pathway_counter)

        return True

    def launch_from_fiber(
        self,
        bundle: Dict[str, Dict[str, Union[float, str]]],
        lp_node: str,
        launch_type: LaunchType = LaunchType.GAUSSIAN,
    ) -> None:
        """
        Configure launch field from a specific fiber.

        Sets up the initial field distribution for simulation, launching from
        a specified fiber in the bundle with characteristics matching that fiber's
        core properties.

        Args:
            bundle: Dictionary mapping LP mode names to fiber properties
            lp_node: The LP mode identifier to launch from (key in the bundle dict)
            launch_type: Type of field distribution to launch. Defaults to GAUSSIAN.

        Returns:
            None
        """
        self.circuit.add_launch_field(
            launch_type=launch_type,
            launch_tilt=0,
            launch_pathway=self.circuit.pathway_counter,
            launch_width=bundle[lp_node]["core_dia"],
            launch_height=bundle[lp_node]["core_dia"],
            launch_position=bundle[lp_node]["pos_x"],
            launch_position_y=bundle[lp_node]["pos_y"],
        )
