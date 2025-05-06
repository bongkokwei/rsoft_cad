"""
Module for handling segment creation and management for photonic lanterns.
"""


class SegmentManager:
    """
    Handles the creation and management of segments for photonic lanterns.
    """

    def __init__(self, circuit_ref):
        """
        Initialize the segment manager with a reference to the circuit.

        Args:
            circuit_ref: Reference to the RSoftCircuit object
        """
        self.circuit = circuit_ref

    def add_fiber_segment(self, bundle, core_or_clad="core"):
        """
        Add a fiber segment with core and cladding based on fiber properties.

        Args:
            bundle (dict): The fiber bundle containing fiber properties
            core_or_clad (str): Whether to add "core" or "cladding" segments

        Returns:
            bool: True if successful
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
                    width_taper="TAPER_LINEAR",
                    height_taper="TAPER_LINEAR",
                    position_y_taper="TAPER_LINEAR",
                    position_taper="TAPER_LINEAR",
                )
            self.circuit.add_segment(**segment_prop)
            if core_or_clad == "core":
                # Add pathway with this segment
                self.circuit.add_pathways(segment_ids=self.circuit.segment_counter)
                self.circuit.add_pathways_monitor(
                    pathway_id=self.circuit.pathway_counter,
                    **{"monitor_type": "MONITOR_FIELD_NEFF"},
                )
        return True

    def add_capillary_segment(self, cap_dia, taper_factor, taper_length):
        """
        Add a capillary segment to contain the fibers.

        Args:
            cap_dia (float): Capillary diameter in microns
            taper_factor (float): Taper factor for the capillary
            taper_length (float): Taper length in microns

        Returns:
            bool: True if successful
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
                width_taper="TAPER_LINEAR",
                height_taper="TAPER_LINEAR",
                position_y_taper="TAPER_LINEAR",
                position_taper="TAPER_LINEAR",
            )
        self.circuit.add_segment(**segment_prop)

        # Add pathway with this segment
        self.circuit.add_pathways(segment_ids=self.circuit.segment_counter)
        self.circuit.add_pathways_monitor(pathway_id=self.circuit.pathway_counter)

        return True

    def launch_from_fiber(self, bundle, lp_node):
        """
        Configure launch field from a specific fiber.

        Args:
            bundle (dict): The fiber bundle containing fiber properties
            lp_node (str): The LP mode to launch from

        Returns:
            None
        """
        self.circuit.add_launch_field(
            launch_type="LAUNCH_GAUSSIAN",
            launch_tilt=0,
            launch_pathway=self.circuit.pathway_counter,
            launch_width=bundle[lp_node]["core_dia"],
            launch_height=bundle[lp_node]["core_dia"],
            launch_position=bundle[lp_node]["pos_x"],
            launch_position_y=bundle[lp_node]["pos_y"],
        )
