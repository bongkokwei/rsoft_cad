import os


class RSoftCircuit:
    def __init__(self, params=None, **extra_param):
        # Default parameter dictionary
        self.params = {
            "alpha": 0,
            "background_index": 1,
            "cad_aspectratio": 1,
            "delta": 0.1,
            "dimension": 3,
            "eim": 0,
            "free_space_wavelength": 1.55,
            "height": 1,
            "k0": "(2 * pi) / free_space_wavelength",
            "lambda": "free_space_wavelength",
            "launch_tilt": 1,
            "sim_tool": "ST_BEAMPROP",
            "structure": "STRUCT_CHANNEL",
            "width": 1,
        }

        # Update with params dictionary if provided
        if params is not None:
            self.params.update(params)

        # Update with any additional keyword arguments
        self.params.update(extra_param)

        self.segment_counter = 0
        self.pathway_counter = 0
        self.monitor_counter = 0
        self.launch_field_counter = 0

        # Store generated elements
        self.segments = []
        self.pathways = []
        self.monitors = []
        self.launch_fields = []

    def update_global_params(self, **params):
        # TODO: Add some data validations
        self.params.update(params)

    def add_segment(self, segment_id=None, **properties):
        if segment_id is None:
            self.segment_counter += 1
            segment_id = self.segment_counter

        # Default segment properties
        segment_props = {
            "structure": "STRUCT_FIBER",
            "comp_name": "CORE",
            "begin.x": 0,
            "begin.y": 0,
            "begin.z": 0,
            "begin.height": 0,
            "begin.width": 0,
            "begin.delta": 0,
            "end.x": 0,
            "end.y": 0,
            "end.z": 0,
            "end.height": 0,
            "end.width": 0,
            "end.delta": 0,
        }

        # Update with any custom properties
        segment_props.update(properties)

        # Generate the segment text
        segment_text = f"segment {segment_id}\n"
        for key, value in segment_props.items():
            segment_text += f"\t{key} = {value}\n"
        segment_text += "end segment\n"

        # Store the segment
        self.segments.append(segment_text)

        return segment_text

    def add_pathways(self, pathway_id=None, segment_ids=None):
        if pathway_id is None:
            self.pathway_counter += 1
            pathway_id = self.pathway_counter

        if segment_ids is None:
            segment_ids = [1]  # Default is just segment 1
        elif isinstance(segment_ids, int):
            segment_ids = [segment_ids]  # Convert single ID to list

        # Generate the pathway text
        pathway_text = f"pathway {pathway_id}\n"
        for segment_id in segment_ids:
            pathway_text += f"\t{segment_id}\n"
        pathway_text += "end pathway\n"

        # Store the pathway
        self.pathways.append(pathway_text)

        return pathway_text

    def add_pathways_monitor(self, monitor_id=None, pathway_id=1, **properties):
        if monitor_id is None:
            self.monitor_counter += 1
            monitor_id = self.monitor_counter

        # Default monitor properties
        monitor_props = {
            "pathway": pathway_id,
            "monitor_type": "MONITOR_WG_POWER",
            "monitor_component": "COMPONENT_BOTH",
        }

        # Update with any custom properties
        monitor_props.update(properties)

        # Generate the monitor text
        monitor_text = f"monitor {monitor_id}\n"
        for key, value in monitor_props.items():
            monitor_text += f"\t{key} = {value}\n"
        monitor_text += "end monitor\n"

        # Store the monitor
        self.monitors.append(monitor_text)

        return monitor_text

    def add_launch_field(self, launch_id=None, pathway_id=1, **properties):
        if launch_id is None:
            self.launch_field_counter += 1
            launch_id = self.launch_field_counter

        # Default launch field properties
        launch_props = {
            "launch_pathway": pathway_id,
            "launch_type": "LAUNCH_GAUSSIAN",
            "launch_random_set": 69,
            "launch_align_file": 1,
            "launch_width": 0,
            "launch_height": 0,
            "launch_position": 0,
            "launch_position_y": 0,
            "launch_polarizer": 2,
            "launch_polarizer_angle": 45,
        }

        # Update with any custom properties
        launch_props.update(properties)

        # Generate the launch field text
        launch_text = f"launch_field {launch_id}\n"
        for key, value in launch_props.items():
            launch_text += f"\t{key} = {value}\n"
        launch_text += "end launch_field\n"

        # Store the launch field
        self.launch_fields.append(launch_text)
        self.update_global_params(**launch_props)

        return launch_text

    def write(self, filepath):
        """
        Combine all generated circuit elements and write them to a file.
        Creates the directory if it doesn't exist.

        Parameters:
        filepath (str): Path to the output file

        Returns:
        bool: True if write was successful, False otherwise
        """
        try:
            # Make sure the directory exists
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Prepare the contents of the file
            content = ""

            # Add parameters
            content += "# Global parameters\n"
            for key, value in self.params.items():
                content += f"{key} = {value}\n"
            content += "\n"

            # Add segments
            if self.segments:
                content += "# Segments\n"
                for segment in self.segments:
                    content += segment + "\n"

            # Add pathways
            if self.pathways:
                content += "# Pathways\n"
                for pathway in self.pathways:
                    content += pathway + "\n"

            # Add monitors
            if self.monitors:
                content += "# Monitors\n"
                for monitor in self.monitors:
                    content += monitor + "\n"

            # Add launch fields
            if self.launch_fields:
                content += "# Launch Fields\n"
                for launch_field in self.launch_fields:
                    content += launch_field + "\n"

            # Write to file
            with open(filepath, "w") as f:
                f.write(content)

            print(f"Circuit written to {filepath}")
            return True

        except Exception as e:
            print(f"Error writing circuit to {filepath}: {e}")
            return False

    @staticmethod
    def relative_dist(var_name: str, segment_id: int):
        return f"{var_name} rel begin segment {segment_id}"


if __name__ == "__main__":
    # Example usage:
    circuit = RSoftCircuit()

    # Add some segments
    circuit.add_segment()
    circuit.add_segment()

    # Add a pathway using these segments
    circuit.add_pathways(segment_ids=[1, 2])

    # Add a monitor for the pathway
    circuit.add_pathways_monitor(monitor_id=1, pathway_id=1)

    # Add a launch field
    circuit.add_launch_field(launch_id=1, pathway_id=1)

    # Write the circuit to a file
    circuit.write("output/my_circuit.ind")
