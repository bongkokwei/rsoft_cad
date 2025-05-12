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
        segment_prop_overrides: Optional[Dict[str, Any]] = None,
        per_fiber_overrides: Optional[Dict[str, Dict[str, Any]]] = None,
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
            segment_prop_overrides: Dictionary to override default properties for all segments.
                                  Keys should match the segment property names (e.g., 'begin.x', 'end.z').
            per_fiber_overrides: Dictionary mapping LP mode names to property overrides for specific fibers.
                                Each value should be a dictionary of property name to value mappings.

        Returns:
            True if the segments were successfully added.

        Examples:
            # Basic usage (existing functionality)
            manager.add_fiber_segment(bundle)

            # Override properties for all fibers
            manager.add_fiber_segment(bundle, segment_prop_overrides={"begin.z": 5})

            # Override properties for specific fibers
            manager.add_fiber_segment(
                bundle,
                per_fiber_overrides={
                    "LP01": {"comp_name": "CORE_LP01_SPECIAL"},
                    "LP11": {"begin.width": 12}
                }
            )
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

            # Apply global overrides if provided
            if segment_prop_overrides:
                segment_prop.update(segment_prop_overrides)

            # Apply per-fiber overrides if provided
            if per_fiber_overrides and lp_mode in per_fiber_overrides:
                segment_prop.update(per_fiber_overrides[lp_mode])

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
        segment_prop_overrides: Optional[Dict[str, Any]] = None,
        monitor_type: MonitorType = MonitorType.FIBER_POWER,
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
            taper_type: Taper profile to use if tapering is applied. Defaults to LINEAR.
            segment_prop_overrides: Dictionary to override default properties for the capillary segment.
                                  Keys should match the segment property names (e.g., 'begin.x', 'end.z').
            monitor_type: Type of monitor to add to the pathway. Defaults to FIBER_POWER.

        Returns:
            True if the capillary segment was successfully added

        Examples:
            # Basic usage (existing functionality)
            manager.add_capillary_segment(100, 2, 1000)

            # Override capillary properties
            manager.add_capillary_segment(
                100, 2, 1000,
                segment_prop_overrides={"comp_name": "CAPILLARY_CUSTOM", "begin.x": 10}
            )
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

        # Apply overrides if provided
        if segment_prop_overrides:
            segment_prop.update(segment_prop_overrides)

        segment_prop.update(
            width_taper=taper_type,
            height_taper=taper_type,
            position_y_taper=taper_type,
            position_taper=taper_type,
        )

        self.circuit.add_segment(**segment_prop)

        # Add pathway with this segment
        self.circuit.add_pathways(segment_ids=self.circuit.segment_counter)
        self.circuit.add_pathways_monitor(
            pathway_id=self.circuit.pathway_counter, monitor_type=monitor_type
        )

        return True

    def launch_from_fiber(
        self,
        bundle: Dict[str, Dict[str, Union[float, str]]],
        lp_node: str,
        launch_type: LaunchType = LaunchType.GAUSSIAN,
        launch_prop_overrides: Optional[Dict[str, Any]] = None,
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
            launch_prop_overrides: Dictionary to override default launch properties.
                                 Keys should match the launch field parameters
                                 (e.g., 'launch_tilt', 'launch_width').

        Returns:
            None

        Examples:
            # Basic usage (existing functionality)
            manager.launch_from_fiber(bundle, "LP01")

            # Override launch properties
            manager.launch_from_fiber(
                bundle, "LP01",
                launch_prop_overrides={
                    "launch_tilt": 5,
                    "launch_width": 20
                }
            )
        """
        # Default launch properties
        launch_params = {
            "launch_type": launch_type,
            "launch_tilt": 0,
            "launch_pathway": self.circuit.pathway_counter,
            "launch_width": bundle[lp_node]["core_dia"],
            "launch_height": bundle[lp_node]["core_dia"],
            "launch_position": bundle[lp_node]["pos_x"],
            "launch_position_y": bundle[lp_node]["pos_y"],
        }

        # Apply overrides if provided
        if launch_prop_overrides:
            launch_params.update(launch_prop_overrides)

        self.circuit.add_launch_field(**launch_params)
