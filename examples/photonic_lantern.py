#!/usr/bin/env python3
"""
Photonic Lantern Simulation Script - Refactored to use configuration files
"""

import json
import os
import argparse
from rsoft_cad.rsoft_circuit import RSoftCircuit


def load_config(config_file="complete_pl_config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file {config_file} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not parse {config_file}.")
        return None


def create_photonic_lantern(config, output_file="output/six_core_PL.ind"):
    """Create photonic lantern model from configuration"""

    # Extract configuration sections
    pl_params = config.get("pl_params", {})
    center_core_segment = config.get("center_core_segment", {})
    center_cladding_segment = config.get("center_cladding_segment", {})
    core_segment_template = config.get("core_segment", {})
    cladding_segment_template = config.get("cladding_segment", {})
    capillary_segment = config.get("capillary_segment", {})
    launch_config = config.get("launch_field_config", {})
    rsoft_circuit_config = config.get("rsoft_circuit_config", {})

    # Get the number of cores
    num_cores = pl_params.get("Num_Cores_Ring", 5)

    # Initialize RSoftCircuit with parameters
    circuit_params = {**pl_params, **rsoft_circuit_config}
    six_core_PL = RSoftCircuit(circuit_params)

    # 1. Add center core
    center_core_segment.update(
        **{
            "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=1),
        }
    )
    six_core_PL.add_segment(**center_core_segment)

    # 2. Add surrounding cores
    for i in range(num_cores):
        # Create a deep copy of the template to avoid modifying the original
        core_segment = dict(core_segment_template)

        # Update segment-specific properties
        core_segment.update(
            {
                "comp_name": f"{i}_CORE",
                "begin.x": f"Core_Ring_Radius*cos({i}*Angular_Sep+Rotate_View)",
                "begin.y": f"Core_Ring_Radius*sin({i}*Angular_Sep+Rotate_View)",
                "end.x": f"Core_Ring_Radius*cos({i}*Angular_Sep+Rotate_View)/Taper_Slope",
                "end.y": f"Core_Ring_Radius*sin({i}*Angular_Sep+Rotate_View)/Taper_Slope",
                "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=i + 2),
            }
        )

        # Add the segment to the circuit
        six_core_PL.add_segment(**core_segment)

    # 3. Add capillary (material-less core that encompasses all)
    capillary_segment.update(
        **{
            "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=7),
        }
    )
    six_core_PL.add_segment(**capillary_segment)

    # 4. Add center cladding
    center_cladding_segment.update(
        **{
            "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=1 + 7),
        }
    )
    six_core_PL.add_segment(**center_cladding_segment)

    # 5. Add surrounding cladding
    for j in range(num_cores):
        # Create a deep copy of the template to avoid modifying the original
        cladding_segment = dict(cladding_segment_template)

        # Update segment-specific properties
        cladding_segment.update(
            {
                "comp_name": f"{j}_CLADDING",
                "begin.x": f"Core_Ring_Radius*cos({j}*Angular_Sep+Rotate_View)",
                "begin.y": f"Core_Ring_Radius*sin({j}*Angular_Sep+Rotate_View)",
                "end.x": f"Core_Ring_Radius*cos({j}*Angular_Sep+Rotate_View)/Taper_Slope",
                "end.y": f"Core_Ring_Radius*sin({j}*Angular_Sep+Rotate_View)/Taper_Slope",
                "end.z": RSoftCircuit.relative_dist(
                    "Taper_Length", segment_id=j + 2 + 7
                ),
            }
        )

        # Add the segment to the circuit
        six_core_PL.add_segment(**cladding_segment)

    # 6. Add pathways and pathway monitors
    for ii in range(1, num_cores + 3):
        six_core_PL.add_pathways(segment_ids=ii)
        six_core_PL.add_pathways_monitor(pathway_id=ii)

    # 7. Add launch field
    port_num = launch_config.get("port_num", 2)
    pathway = launch_config.get("pathway", 7)

    launch_field_params = {
        "launch_pathway": pathway,
        "launch_type": launch_config.get("launch_type", "LAUNCH_GAUSSIAN"),
        "launch_width": launch_config.get("launch_width", "Diameter_SM_Core"),
        "launch_height": launch_config.get("launch_height", "Diameter_SM_Core"),
        "launch_position": f"Core_Ring_Radius*cos({port_num}*Angular_Sep+Rotate_View)",
        "launch_position_y": f"Core_Ring_Radius*sin({port_num}*Angular_Sep+Rotate_View)",
    }

    six_core_PL.add_launch_field(**launch_field_params)

    # 8. Write the circuit to file
    six_core_PL.write(output_file)
    print(f"Photonic lantern model created and saved to {output_file}")

    return True


def main():
    """Main function to handle command-line arguments and run the script"""
    parser = argparse.ArgumentParser(
        description="Create photonic lantern model from configuration"
    )
    parser.add_argument(
        "--config",
        "-c",
        default="config/complete_pl_config.json",
        help="Configuration file (default: config/complete_pl_config.json)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output/six_core_PL/six_core_PL.ind",
        help="Output file path (default: output/six_core_PL.ind)",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    if not config:
        return False

    # Create photonic lantern
    return create_photonic_lantern(config, args.output)


if __name__ == "__main__":
    main()
