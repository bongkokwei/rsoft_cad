import numpy as np

from fiber import OpticalFiber
from rsoft_cad.utils.hex_lantern_layout import hexagonal_fiber_layout


class HexagonalMCF(OpticalFiber):
    def __init__(self, prop=None, **prop_dict):
        super().__init__(prop, **prop_dict)

        # Default MCF properties
        self.mcf_props = {
            "num_rings": 2,  # Number of hexagonal rings around the central core
            "spacing_factor": 1.05,  # Factor to adjust spacing between cores (1.0 = touching)
            "core_properties": {},  # Dictionary to store custom properties for individual cores
            "all_core_ids": [],  # List to track all created core IDs
        }

        # Update with any properties provided
        if prop is not None and isinstance(prop, dict):
            self.mcf_props.update(
                {k: v for k, v in prop.items() if k in self.mcf_props}
            )
        self.mcf_props.update(
            {k: v for k, v in prop_dict.items() if k in self.mcf_props}
        )

        self.update_global_params(
            cad_aspectratio_x=50,
            cad_aspectratio_y=50,
            background_index=1,
            grid_size=1,
            grid_size_y=1,
            fem_nev=3,  # Number of modes to find
            sim_tool="ST_FEMSIM",
        )

    def set_num_rings(self, num_rings):
        """
        Set the number of hexagonal rings around the central core.

        Parameters:
        num_rings (int): Number of hexagonal rings

        Returns:
        bool: True if successful, False otherwise
        """
        if not isinstance(num_rings, int) or num_rings < 0:
            print("Error: Number of rings must be a non-negative integer")
            return False

        self.mcf_props["num_rings"] = num_rings
        return True

    def set_spacing_factor(self, spacing_factor):
        """
        Set the spacing factor between cores.

        Parameters:
        spacing_factor (float): Factor to adjust spacing between cores (1.0 = touching)

        Returns:
        bool: True if successful, False otherwise
        """
        if spacing_factor < 1.0:
            print("Warning: Spacing factor < 1.0 may cause cores to overlap")

        self.mcf_props["spacing_factor"] = spacing_factor
        return True

    def set_core_property(self, core_id, property_name, property_value):
        """
        Set a custom property for a specific core.

        Parameters:
        core_id (str): ID of the core
        property_name (str): Name of the property
        property_value: Value of the property

        Returns:
        bool: True if successful, False otherwise
        """
        if core_id not in self.mcf_props["core_properties"]:
            self.mcf_props["core_properties"][core_id] = {}

        self.mcf_props["core_properties"][core_id][property_name] = property_value
        return True

    def calculate_core_positions(self):
        """
        Calculate the positions of cores arranged in a hexagonal pattern.

        Returns:
        tuple: (centers_x, centers_y) containing arrays of core center coordinates
        """

        # Use core diameter for spacing calculation
        core_dia = self.fiber_props["core_dia"]
        num_rings = self.mcf_props["num_rings"]
        spacing_factor = self.mcf_props["spacing_factor"]

        effective_spacing = (
            self.fiber_props["cladding_dia"] / core_dia
        ) * spacing_factor

        # Call the hexagonal layout function
        centers_x, centers_y = hexagonal_fiber_layout(
            core_dia,
            num_rings,
            effective_spacing,
        )

        return centers_x, centers_y

    def create_hexagonal_mcf(self, base_id="FIBER", apply_custom_props=True):
        """
        Create a hexagonal multi-core fiber with the specified properties.

        Parameters:
        base_id (str): Base ID for naming the cores
        apply_custom_props (bool): Whether to apply custom properties from core_properties

        Returns:
        HexagonalMCF: self for method chaining
        """
        # Calculate core positions
        centers_x, centers_y = self.calculate_core_positions()

        # Reset the list of core IDs
        self.mcf_props["all_core_ids"] = []

        """NEED TO CHANGE THIS"""
        self.set_length(55000)
        self.fiber_props["taper_factor"] = 1

        # Create each fiber core
        for i, (x, y) in enumerate(zip(centers_x, centers_y)):
            # Generate unique IDs for this core
            fiber_id = f"{base_id}_{i}"
            core_id = f"{fiber_id}_CORE"
            cladding_id = f"{fiber_id}_CLAD"

            # Store the core ID
            self.mcf_props["all_core_ids"].append(core_id)

            # Store original position
            original_x = self.fiber_props["pos_x"]
            original_y = self.fiber_props["pos_y"]

            # Set position for this core
            # self.fiber_props["pos_x"] = original_x + x
            # self.fiber_props["pos_y"] = original_y + y

            self.set_pos(original_x + x, original_y + y)

            # Apply any custom properties for this core
            original_props = {}
            if apply_custom_props and fiber_id in self.mcf_props["core_properties"]:
                for prop_name, prop_value in self.mcf_props["core_properties"][
                    fiber_id
                ].items():
                    if prop_name in self.fiber_props:
                        # Save original value
                        original_props[prop_name] = self.fiber_props[prop_name]
                        # Apply custom value
                        self.fiber_props[prop_name] = prop_value

            # Create core and cladding segments
            self.add_core_segment(core_id=core_id)
            self.add_cladding_segment(cladding_id=cladding_id)

            # Add pathway with this segment
            seg_id = self.find_segment_by_comp_name(self.segments, core_id)
            pth_way = self.add_pathways(segment_ids=[seg_id])

            # Add monitor for this core
            self.add_pathways_monitor(pathway_id=i + 1)

            # Restore original position for next core
            self.fiber_props["pos_x"] = original_x
            self.fiber_props["pos_y"] = original_y

            # Restore any modified properties
            for prop_name, prop_value in original_props.items():
                self.fiber_props[prop_name] = prop_value

        return self

    def get_core_count(self):
        """
        Get the number of cores in the MCF.

        Returns:
        int: Number of cores
        """
        return len(self.mcf_props["all_core_ids"])

    def add_launch_fields_all_cores(self, launch_file="SMF28_LP01.m00"):
        """
        Add launch fields to all cores in the MCF.

        Parameters:
        launch_file (str): Launch field file to use

        Returns:
        HexagonalMCF: self for method chaining
        """
        for i, core_id in enumerate(self.mcf_props["all_core_ids"]):
            # Find the pathway associated with this core
            # Assuming pathways are created in the same order as cores
            pathway_id = i + 1

            # Add launch field
            # Note: This is a placeholder; the actual implementation would depend on
            # the specifics of the add_launch_field method in the parent class
            if hasattr(self, "add_launch_field"):
                self.add_launch_field(pathway_id=pathway_id, launch_file=launch_file)

        return self

    def create_standard_hexagonal_mcf(
        self, base_id="MCF", num_rings=2, spacing_factor=1.05
    ):
        """
        Create a standard hexagonal MCF with default parameters.

        Parameters:
        base_id (str): Base ID for naming the cores
        num_rings (int): Number of hexagonal rings around the central core
        spacing_factor (float): Factor to adjust spacing between cores

        Returns:
        HexagonalMCF: self for method chaining
        """
        # Set MCF properties
        self.set_num_rings(num_rings)
        self.set_spacing_factor(spacing_factor)

        # Set standard SMF-28 parameters for each core
        self.set_core_dia(10.4)
        self.set_cladding_dia(125.0)
        self.set_core_index(1.45213)
        self.set_cladding_index(1.44692)
        self.set_background_index(1.4345)
        self.set_length(10000)  # 1mm length

        # Create the MCF
        self.create_hexagonal_mcf(base_id=base_id)

        return self


# Example usage
if __name__ == "__main__":
    # Create a standard hexagonal MCF with 2 rings
    mcf = HexagonalMCF()
    mcf.create_standard_hexagonal_mcf(num_rings=1)

    # Print the number of cores
    print(f"Created MCF with {mcf.get_core_count()} cores")

    # Write to file
    mcf.write(f"output/hex_{mcf.get_core_count()}_cores_mcf.ind")
