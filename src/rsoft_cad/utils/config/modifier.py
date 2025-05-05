#!/usr/bin/env python3
"""
Utility script to modify photonic lantern configuration and create new configuration files.
"""

import json
import argparse
import os
from copy import deepcopy


def load_config(config_file="config/complete_pl_config.json"):
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


def save_config(config, output_file):
    """Save configuration to JSON file"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    try:
        with open(output_file, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def modify_parameter(config, param_path, value):
    """
    Modify a parameter in the configuration.

    Args:
        config: The configuration dictionary
        param_path: Path to the parameter (e.g., "pl_params.Num_Cores_Ring")
        value: New value for the parameter

    Returns:
        Modified configuration dictionary
    """
    # Split the path into parts
    parts = param_path.split(".")

    # Navigate to the target dictionary
    target = config
    for i, part in enumerate(parts[:-1]):
        if part not in target:
            print(f"Warning: Creating new section '{part}' in configuration")
            target[part] = {}
        target = target[part]

    # Get the last part (the parameter name)
    param_name = parts[-1]

    # Check if parameter exists
    if param_name in target:
        old_value = target[param_name]
        # Try to convert to appropriate type if original is numeric
        if isinstance(old_value, (int, float)) and not isinstance(value, (int, float)):
            try:
                if isinstance(old_value, int):
                    value = int(value)
                else:
                    value = float(value)
            except ValueError:
                # Keep as string if conversion fails (might be a formula)
                pass
        print(f"Changed {param_path}: {old_value} -> {value}")
    else:
        print(f"Added new parameter {param_path}: {value}")

    # Update the parameter
    target[param_name] = value

    return config


def list_configuration(config, prefix=""):
    """
    Recursively list all parameters in the configuration.

    Args:
        config: Configuration dictionary or subdictionary
        prefix: Current path prefix for nested parameters
    """
    for key, value in sorted(config.items()):
        current_path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            # Recursively list subdictionaries
            print(f"\n[{current_path}]")
            list_configuration(value, current_path)
        else:
            # Print parameter
            print(f"{current_path} = {value}")


def main():
    parser = argparse.ArgumentParser(
        description="Modify photonic lantern configuration"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="config/complete_pl_config.json",
        help="Input configuration file (default: config/complete_pl_config.json)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output configuration file (default: based on input filename)",
    )
    parser.add_argument(
        "--param",
        "-p",
        action="append",
        nargs=2,
        metavar=("PATH", "VALUE"),
        help="Parameter path and value to modify (e.g., 'pl_params.Num_Cores_Ring' '6')",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all parameters in the input file",
    )

    args = parser.parse_args()

    # Default output filename
    if not args.output and args.param:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_modified{ext}"

    # Load configuration
    config = load_config(args.input)
    if not config:
        return

    # List configuration if requested
    if args.list:
        print(f"\nConfiguration in {args.input}:")
        print("=" * 50)
        list_configuration(config)

    # Modify parameters if provided
    if args.param:
        # Make a copy of the configuration
        new_config = deepcopy(config)

        # Apply each modification
        for param_path, value in args.param:
            new_config = modify_parameter(new_config, param_path, value)

        # Save the modified configuration
        if save_config(new_config, args.output) and args.list:
            # Show the new configuration
            print(f"\nUpdated configuration in {args.output}:")
            print("=" * 50)
            list_configuration(new_config)

    # If no actions specified, show help
    if not args.list and not args.param:
        parser.print_help()


if __name__ == "__main__":
    main()
