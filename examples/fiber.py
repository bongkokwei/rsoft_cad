from rsoft_cad.rsoft_circuit import RSoftCircuit
import rsoft_cad.utils.config.modifier as mc


class OpticalFiber(RSoftCircuit):
    def __init__(self, prop=None, **prop_dict):
        super().__init__(prop, **prop_dict)

        self.fiber_props = {
            "core_dia": 8.2,  # Core diameter in microns
            "cladding_dia": 125.0,  # Cladding diameter in microns
            "core_index": 1,  # Core refractive index
            "cladding_index": 1,  # Cladding refractive index
            "bg_index": 1,
            "length": 1000,  # Fiber length in microns
            "pos_x": 0,  # X position in microns
            "pos_y": 0,  # Y position in microns
            "pos_z": 0,  # Z position in microns
            "taper_factor": 1,
        }

        # Update with any properties provided
        if prop is not None:
            self.fiber_props.update(prop)
        self.fiber_props.update(prop_dict)

        # Update global parameters related to fiber
        self.update_global_params(
            eim=0,
            structure="STRUCT_FIBER",
            background_index=self.fiber_props["bg_index"],
        )

    def set_cladding_dia(self, cladding_dia):
        """
        Set the cladding diameter with validation.

        Parameters:
        cladding_dia (float): Cladding diameter in microns

        Returns:
        bool: True if successful, False otherwise
        """
        # Data validation: cladding must be larger than core
        if cladding_dia <= self.fiber_props.get("core_dia", 0):
            print("Error: Cladding diameter must be larger than core diameter")
            return False

        self.fiber_props["cladding_dia"] = cladding_dia
        return True

    def set_core_dia(self, core_dia):
        """
        Set the core diameter with validation.

        Parameters:
        core_dia (float): Core diameter in microns

        Returns:
        bool: True if successful, False otherwise
        """
        # Data validation: core must be smaller than cladding
        if core_dia >= self.fiber_props.get("cladding_dia", float("inf")):
            print("Error: Core diameter must be smaller than cladding diameter")
            return False

        self.fiber_props["core_dia"] = core_dia
        return True

    def set_cladding_index(self, cladding_index):
        """
        Set the cladding refractive index with validation.

        Parameters:
        cladding_index (float): Cladding refractive index

        Returns:
        bool: True if successful, False otherwise
        """
        # Data validation: core index must be higher than cladding index
        if cladding_index >= self.fiber_props.get("core_index", float("inf")):
            print("Error: Cladding index must be lower than core index")
            return False

        self.fiber_props["cladding_index"] = cladding_index
        # Update background index to match cladding
        # self.update_global_params(background_index=cladding_index)
        return True

    def set_background_index(self, bg_index):
        """
        Set the background refractive index with validation.
        Parameters:
        bg_index (float): Background refractive index
        Returns:
        bool: True if successful, False otherwise
        """
        # Data validation: core index must be higher than background index
        if bg_index >= self.fiber_props.get("core_index", float("inf")):
            print("Error: Background index must be lower than core index")
            return False
        self.fiber_props["bg_index"] = bg_index
        # Update cladding index to match background
        self.update_global_params(background_index=bg_index)
        return True

    def set_core_index(self, core_index):
        """
        Set the core refractive index with validation.

        Parameters:
        core_index (float): Core refractive index

        Returns:
        bool: True if successful, False otherwise
        """
        # Data validation: core index must be higher than cladding index
        if core_index <= self.fiber_props.get("cladding_index", 0):
            print("Error: Core index must be higher than cladding index")
            return False

        self.fiber_props["core_index"] = core_index
        return True

    def set_length(self, length):
        """
        Set the fiber length.

        Parameters:
        length (float): Fiber length in microns

        Returns:
        bool: True if successful, False otherwise
        """
        if length <= 0:
            print("Error: Length must be positive")
            return False

        self.fiber_props["length"] = length
        return True

    def set_pos(self, x=0, y=0, z=0):
        """
        Set the starting position of the fiber.

        Parameters:
        x (float): X-coordinate position in microns
        y (float): Y-coordinate position in microns
        z (float): Z-coordinate position in microns

        Returns:
        bool: True if successful, False otherwise
        """
        # Store position in fiber properties
        self.fiber_props["pos_x"] = x
        self.fiber_props["pos_y"] = y
        self.fiber_props["pos_z"] = z

        return True

    def set_taper_factor(self, taper_factor):
        """
        Set the taper factor of the fiber

        Parameters:
        taper_factor (float): Coefficient that linearly tapers a fiber

        Returns:
        bool: True if successful, False otherwise
        """

        self.fiber_props.update(taper_factor=taper_factor)

        return True

    def add_core_segment(self, segment_id=None, core_id="CORE", **params):
        """
        Add a fiber segment with core and cladding based on fiber properties.

        Parameters:
        segment_id (int, optional): ID for the segment. If None, auto-incremented.

        Returns:
        str: The generated segment text
        """
        # Calculate delta based on refractive indices
        n1 = self.fiber_props["core_index"]
        n_bg = self.fiber_props["bg_index"]
        delta = n1 - n_bg

        # Default segment properties
        fiber_props = {
            "comp_name": core_id,
            "begin.x": self.fiber_props["pos_x"],
            "begin.y": self.fiber_props["pos_y"],
            "begin.z": self.fiber_props["pos_z"],
            "begin.height": self.fiber_props["core_dia"],
            "begin.width": self.fiber_props["core_dia"],
            "begin.delta": delta,
            "end.x": self.fiber_props["pos_x"] / self.fiber_props["taper_factor"],
            "end.y": self.fiber_props["pos_y"] / self.fiber_props["taper_factor"],
            "end.z": self.fiber_props["length"],
            "end.height": self.fiber_props["core_dia"]
            / self.fiber_props["taper_factor"],
            "end.width": self.fiber_props["core_dia"]
            / self.fiber_props["taper_factor"],
            "end.delta": delta,
        }

        fiber_props.update(params)

        if self.fiber_props["taper_factor"] > 1:
            self.fiber_props.update(
                width_taper="TAPER_LINEAR",
                height_taper="TAPER_LINEAR",
                position_y_taper="TAPER_LINEAR",
                position_taper="TAPER_LINEAR",
            )

        return self.add_segment(**fiber_props)

    def add_cladding_segment(self, segment_id=None, cladding_id="CLAD", **params):
        """
        Add a fiber segment with core and cladding based on fiber properties.

        Parameters:
        segment_id (int, optional): ID for the segment. If None, auto-incremented.

        Returns:
        str: The generated segment text
        """
        # Calculate delta based on refractive indices
        n1 = self.fiber_props["cladding_index"]
        n_bg = self.fiber_props["bg_index"]
        delta = n1 - n_bg

        # Default segment properties
        cladding_props = {
            "comp_name": cladding_id,
            "begin.x": self.fiber_props["pos_x"],
            "begin.y": self.fiber_props["pos_y"],
            "begin.z": self.fiber_props["pos_z"],
            "begin.height": self.fiber_props["cladding_dia"],
            "begin.width": self.fiber_props["cladding_dia"],
            "begin.delta": delta,
            "end.x": self.fiber_props["pos_x"] / self.fiber_props["taper_factor"],
            "end.y": self.fiber_props["pos_y"] / self.fiber_props["taper_factor"],
            "end.z": self.fiber_props["length"],
            "end.height": self.fiber_props["cladding_dia"]
            / self.fiber_props["taper_factor"],
            "end.width": self.fiber_props["cladding_dia"]
            / self.fiber_props["taper_factor"],
            "end.delta": delta,
        }

        cladding_props.update(params)

        if self.fiber_props["taper_factor"] > 1:
            self.fiber_props.update(
                width_taper="TAPER_LINEAR",
                height_taper="TAPER_LINEAR",
                position_y_taper="TAPER_LINEAR",
                position_taper="TAPER_LINEAR",
            )

        return self.add_segment(**cladding_props)

    def add_capillary_segment(self, segment_id=None, cap_id="CAPILLARY", **params):
        """
        Add a capillary segment based on fiber properties.

        Parameters:
        segment_id (int, optional): ID for the segment. If None, auto-incremented.

        Returns:
        str: The generated segment text
        """
        # Calculate delta based on refractive indices
        delta = 0

        # Default segment properties
        capillary_props = {
            "comp_name": cap_id,
            "begin.x": 0,
            "begin.y": 0,
            "begin.z": 0,
            "begin.height": self.fiber_props["cap_dia"],
            "begin.width": self.fiber_props["cap_dia"],
            "begin.delta": delta,
            "end.x": 0,
            "end.y": 0,
            "end.z": self.fiber_props["length"],
            "end.height": self.fiber_props["cap_dia"]
            / self.fiber_props["taper_factor"],
            "end.width": self.fiber_props["cap_dia"] / self.fiber_props["taper_factor"],
            "end.delta": delta,
        }

        capillary_props.update(params)

        if self.fiber_props["taper_factor"] > 1:
            self.fiber_props.update(
                width_taper="TAPER_LINEAR",
                height_taper="TAPER_LINEAR",
                position_y_taper="TAPER_LINEAR",
                position_taper="TAPER_LINEAR",
            )

        return self.add_segment(**capillary_props)

    def create_standard_smf(self, fiber_id=None, pos_x=0, pos_y=0):
        """
        Create a standard single mode fiber with typical SMF-28 parameters.

        Returns:
        OpticalFiber: self for method chaining
        """
        self.fiber_props.update(
            pos_x=pos_x,
            pos_y=pos_y,
        )

        # Set SMF-28 standard parameters
        self.set_core_dia(10.4)
        self.set_cladding_dia(125.0)
        self.set_core_index(1.4682)
        self.set_cladding_index(1.4628)
        self.set_length(10000)  # 1mm length

        # Add fiber segment
        if fiber_id is not None:
            core_id = f"{fiber_id}_CORE"
            cladding_id = f"{fiber_id}_CLAD"
        else:
            core_id = "CORE"
            cladding_id = "CLAD"

        self.add_core_segment(core_id=core_id)
        self.add_cladding_segment(cladding_id=cladding_id)

        # Add pathway with this segment
        seg_id = self.find_segment_by_comp_name(self.segments, core_id)

        self.add_pathways(segment_ids=seg_id)

        # Add standard monitor
        self.add_pathways_monitor(segment_ids=seg_id)

        # Add standard launch field for SMF
        # self.add_launch_field(pathway_id=1, launch_file="SMF28_LP01.m00")

        return self

    @staticmethod
    def find_segment_by_comp_name(segments, comp_name):
        for segment in segments:
            if f"comp_name = {comp_name}" in segment:
                # Extract segment number only
                segment_line = segment.split("\n")[0]  # Get "segment X" line
                segment_number = segment_line.replace("segment ", "").strip()
                return segment_number

        # Raise an exception if component is not found
        raise ValueError(f"Component '{comp_name}' not found in any segment")


if __name__ == "__main__":
    # Example usage
    smf = OpticalFiber()
    smf.create_standard_smf(fiber_id=99, pos_x=0, pos_y=0)
    # Write to file
    smf.write("output/smf28_fiber.ind")
